"""Tests for SQLite operation storage."""

import os

import pytest

import sqlite_store


pytestmark = pytest.mark.safety


def test_sqlite_records_batch_history(isolated_app_files, tmp_path):
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    source.write_text("data", encoding="utf-8")
    destination.parent.mkdir()

    move = {
        "operation_id": "op_1",
        "old_path": str(source),
        "new_path": str(destination),
    }

    sqlite_store.record_batch_plan("batch_1", [move])
    os.rename(source, destination)
    sqlite_store.record_batch_results("batch_1", [move], [])

    history_items = sqlite_store.read_sqlite_history_items()

    assert len(history_items) == 1
    assert history_items[0]["move_id"] == "batch_1"
    assert history_items[0]["action"] == "Moved"
    assert history_items[0]["old_path"] == str(source)
    assert history_items[0]["new_path"] == str(destination)


def test_sqlite_recovery_marks_completed_planned_move(isolated_app_files, tmp_path):
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    source.write_text("data", encoding="utf-8")
    destination.parent.mkdir()

    move = {
        "operation_id": "op_recover",
        "old_path": str(source),
        "new_path": str(destination),
    }

    sqlite_store.record_batch_plan("batch_recover", [move])
    os.rename(source, destination)

    recovery_result = sqlite_store.recover_sqlite_operations()

    assert recovery_result == {"recovered": 1, "conflicts": 0}

    history_items = sqlite_store.read_sqlite_history_items()

    assert len(history_items) == 1
    assert history_items[0]["move_id"] == "batch_recover"


def test_sqlite_recovery_is_idempotent(isolated_app_files, tmp_path):
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    source.write_text("data", encoding="utf-8")
    destination.parent.mkdir()

    move = {
        "operation_id": "op_idempotent",
        "old_path": str(source),
        "new_path": str(destination),
    }

    sqlite_store.record_batch_plan("batch_idempotent", [move])
    os.rename(source, destination)

    first_result = sqlite_store.recover_sqlite_operations()
    second_result = sqlite_store.recover_sqlite_operations()

    assert first_result == {"recovered": 1, "conflicts": 0}
    assert second_result == {"recovered": 0, "conflicts": 0}


def test_sqlite_history_marks_undone_batches(isolated_app_files, tmp_path):
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    source.write_text("data", encoding="utf-8")
    destination.parent.mkdir()

    move = {
        "operation_id": "op_undo",
        "old_path": str(source),
        "new_path": str(destination),
    }

    sqlite_store.record_batch_plan("batch_undo", [move])
    os.rename(source, destination)
    sqlite_store.record_batch_results("batch_undo", [move], [])
    sqlite_store.mark_batch_undone("batch_undo")

    history_items = sqlite_store.read_sqlite_history_items()

    assert [item["action"] for item in history_items] == ["Moved", "UNDONE"]
    assert history_items[1]["move_id"] == "batch_undo"


def test_import_legacy_history_items_is_one_time(isolated_app_files):
    history_items = [
        {
            "time": "2026-01-01 00:00:00",
            "move_id": "legacy_batch",
            "action": "Moved",
            "old_path": "/old/report.pdf",
            "new_path": "/old/Documents/report.pdf",
        },
    ]

    first_count = sqlite_store.import_legacy_history_items("/old/neatify_history.txt", history_items)
    second_count = sqlite_store.import_legacy_history_items("/old/neatify_history.txt", history_items)
    imported_history = sqlite_store.read_sqlite_history_items()

    assert first_count == 1
    assert second_count == 0
    assert len(imported_history) == 1
    assert imported_history[0]["move_id"] == "legacy_batch"
