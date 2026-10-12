"""Undo, journal, recovery, and fault-injection tests."""

import os
import subprocess
import sys

import pytest

import journal
import neatify


pytestmark = pytest.mark.safety


def test_undo_last_move_restores_file(isolated_app_files, make_file, tmp_path):
    source = make_file(tmp_path / "report.pdf")
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()

    neatify.move_file(str(source), str(destination), dry_run=False, move_id="move_1")

    assert destination.exists()
    assert not source.exists()

    result = neatify.undo_last_move()

    assert result == "Undone 1 files."
    assert source.exists()
    assert not destination.exists()


def test_batch_move_is_recorded_as_one_undoable_batch(isolated_app_files, make_file, tmp_path):
    source_one = make_file(tmp_path / "one.pdf")
    source_two = make_file(tmp_path / "two.jpg")
    destination_one = tmp_path / "Documents" / "one.pdf"
    destination_two = tmp_path / "Images" / "two.jpg"

    result = neatify.move_files_batch([
        {"old_path": str(source_one), "new_path": str(destination_one)},
        {"old_path": str(source_two), "new_path": str(destination_two)},
    ], move_id="batch_1")

    assert result["moved_count"] == 2
    assert result["errors"] == []
    assert destination_one.exists()
    assert destination_two.exists()
    assert isolated_app_files["database_path"].exists()

    history_items = neatify.read_history_items()
    batch_history_items = [
        item for item in history_items
        if item["move_id"] == "batch_1" and item["action"] == "Moved"
    ]

    assert len(batch_history_items) == 2

    undo_result = neatify.undo_move_by_id("batch_1")

    assert undo_result == "Undone 2 files."
    assert source_one.exists()
    assert source_two.exists()
    assert not destination_one.exists()
    assert not destination_two.exists()


def test_read_history_imports_legacy_text_history_once(isolated_app_files, make_file, tmp_path):
    source = make_file(tmp_path / "report.pdf")
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()

    isolated_app_files["history_path"].write_text(
        "2026-01-01 00:00:00 | old_move | Moved | /old/report.pdf -> /old/Documents/report.pdf\n",
        encoding="utf-8",
    )

    neatify.move_file(str(source), str(destination), dry_run=False, move_id="sqlite_move")

    history_items = neatify.read_history_items()
    second_read = neatify.read_history_items()

    assert sorted(item["move_id"] for item in history_items) == ["old_move", "sqlite_move"]
    assert sorted(item["move_id"] for item in second_read) == ["old_move", "sqlite_move"]


@pytest.mark.fault_injection
def test_failure_before_rename_leaves_source_in_place(isolated_app_files, make_file, monkeypatch, tmp_path):
    source = make_file(tmp_path / "report.pdf")
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()

    def fail_before_move(old_path, new_path):
        raise OSError("simulated rename failure")

    monkeypatch.setattr(neatify.system, "rename", fail_before_move)

    with pytest.raises(OSError):
        neatify.move_file(str(source), str(destination), dry_run=False, move_id="move_fail_before")

    assert source.exists()
    assert not destination.exists()


@pytest.mark.fault_injection
def test_history_failure_does_not_leave_untracked_move(isolated_app_files, make_file, monkeypatch, tmp_path):
    source = make_file(tmp_path / "report.pdf")
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()

    original_record_batch_results = neatify.record_batch_results

    def fail_history_commit(batch_id, moved_moves, failed_moves):
        raise OSError("simulated sqlite history failure")

    monkeypatch.setattr(neatify, "record_batch_results", fail_history_commit)

    with pytest.raises(OSError):
        neatify.move_file(str(source), str(destination), dry_run=False, move_id="move_history_failure")

    assert not source.exists()
    assert destination.exists()

    records = journal.read_journal_records()

    assert any(record.get("state") == "moved" for record in records)
    assert not any(record.get("state") == "history_committed" for record in records)

    monkeypatch.setattr(neatify, "record_batch_results", original_record_batch_results)
    recovery_result = neatify.recover_incomplete_operations()

    assert recovery_result == {"recovered": 1, "conflicts": 0}
    assert neatify.undo_last_move() == "Undone 1 files."
    assert source.exists()
    assert not destination.exists()


def test_arrange_creates_crash_recovery_journal(isolated_app_files, make_file, tmp_path):
    folder = tmp_path / "Downloads"
    make_file(folder / "report.pdf")

    neatify.organize_folder(str(folder), dry_run=False)

    assert isolated_app_files["journal_path"].exists()


def test_recovery_is_idempotent_after_history_failure(isolated_app_files, make_file, monkeypatch, tmp_path):
    source = make_file(tmp_path / "report.pdf")
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()

    original_record_batch_results = neatify.record_batch_results

    def fail_history_commit(batch_id, moved_moves, failed_moves):
        raise OSError("simulated sqlite history failure")

    monkeypatch.setattr(neatify, "record_batch_results", fail_history_commit)

    with pytest.raises(OSError):
        neatify.move_file(str(source), str(destination), dry_run=False, move_id="move_idempotent")

    monkeypatch.setattr(neatify, "record_batch_results", original_record_batch_results)

    first_result = neatify.recover_incomplete_operations()
    second_result = neatify.recover_incomplete_operations()

    assert first_result == {"recovered": 1, "conflicts": 0}
    assert second_result == {"recovered": 0, "conflicts": 0}


def test_malformed_and_truncated_journal_records_are_ignored_safely(isolated_app_files):
    isolated_app_files["journal_path"].write_text('{"state": "planned"\nnot-json\n', encoding="utf-8")

    records = journal.read_journal_records()

    assert len(records) == 2
    assert records[0]["state"] == "malformed_record"
    assert records[1]["state"] == "malformed_record"


def test_recovery_after_subprocess_crash_after_rename(tmp_path):
    data_folder = tmp_path / "app_data"
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()
    source.write_text("data", encoding="utf-8")

    crash_script = tmp_path / "crash_after_rename.py"
    crash_script.write_text(
        "\n".join([
            "import os",
            "import neatify",
            "source = os.environ['NEATIFY_SOURCE']",
            "destination = os.environ['NEATIFY_DESTINATION']",
            "real_rename = os.rename",
            "def crash_after_rename(old_path, new_path):",
            "    real_rename(old_path, new_path)",
            "    os._exit(17)",
            "neatify.system.rename = crash_after_rename",
            "neatify.move_file(source, destination, dry_run=False, move_id='move_subprocess')",
        ]),
        encoding="utf-8",
    )

    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.getcwd()
    environment["NEATIFY_DATA_DIR"] = str(data_folder)
    environment["NEATIFY_SOURCE"] = str(source)
    environment["NEATIFY_DESTINATION"] = str(destination)

    result = subprocess.run([sys.executable, str(crash_script)], env=environment, check=False)

    assert result.returncode == 17
    assert not source.exists()
    assert destination.exists()

    environment["PYTHONPATH"] = os.getcwd()
    recovery_script = tmp_path / "recover.py"
    recovery_script.write_text(
        "import neatify\nprint(neatify.recover_incomplete_operations())\n",
        encoding="utf-8",
    )

    recovery_result = subprocess.run(
        [sys.executable, str(recovery_script)],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "{'recovered': 1, 'conflicts': 0}" in recovery_result.stdout
