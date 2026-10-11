"""Tests for current filesystem behavior and safety boundaries."""

import os
import stat

import pytest

import neatify


pytestmark = pytest.mark.safety


def test_unique_destination_renames_duplicate(make_file, tmp_path):
    existing = make_file(tmp_path / "Documents" / "report.pdf")
    destination = existing

    unique_destination = neatify.get_unique_destination(str(destination))

    assert os.path.basename(unique_destination) == "report 2.pdf"


def test_unique_destination_cache_reserves_names_inside_same_batch(make_file, tmp_path):
    make_file(tmp_path / "Documents" / "report.pdf")
    taken_names_by_folder = {}
    destination = str(tmp_path / "Documents" / "report.pdf")

    first = neatify.get_unique_destination_with_name_cache(destination, taken_names_by_folder)
    second = neatify.get_unique_destination_with_name_cache(destination, taken_names_by_folder)

    assert os.path.basename(first) == "report 2.pdf"
    assert os.path.basename(second) == "report 3.pdf"


def test_safe_destination_accepts_child_path(tmp_path):
    base = tmp_path / "Downloads"
    child = base / "Documents" / "report.pdf"

    assert neatify.is_safe_destination(str(base), str(child))


def test_safe_destination_rejects_directory_escape(tmp_path):
    base = tmp_path / "Downloads"
    outside = tmp_path / "Secrets" / "report.pdf"

    assert not neatify.is_safe_destination(str(base), str(outside))


def test_hidden_files_are_skipped(isolated_app_files, make_file, tmp_path):
    folder = tmp_path / "Downloads"
    visible = make_file(folder / "report.pdf")
    hidden = make_file(folder / ".secret.pdf")

    neatify.organize_folder(str(folder), dry_run=False)

    assert not visible.exists()
    assert (folder / "Documents" / "report.pdf").exists()
    assert hidden.exists()
    assert not (folder / "Documents" / ".secret.pdf").exists()


def test_symlink_file_is_not_followed(isolated_app_files, make_file, tmp_path):
    folder = tmp_path / "Downloads"
    target = make_file(tmp_path / "outside.pdf")
    symlink_path = folder / "linked.pdf"
    folder.mkdir()

    try:
        symlink_path.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not available on this platform or filesystem.")

    neatify.organize_folder(str(folder), dry_run=False)

    assert symlink_path.exists()
    assert target.exists()
    assert not (folder / "Documents" / "linked.pdf").exists()


def test_missing_source_move_raises_file_not_found(isolated_app_files, tmp_path):
    missing = tmp_path / "missing.pdf"
    destination = tmp_path / "Documents" / "missing.pdf"
    destination.parent.mkdir()

    with pytest.raises(FileNotFoundError):
        neatify.move_file(str(missing), str(destination), dry_run=False)


def test_permission_denied_folder_does_not_crash(isolated_app_files, tmp_path):
    folder = tmp_path / "locked"
    folder.mkdir()
    original_mode = stat.S_IMODE(folder.stat().st_mode)

    try:
        folder.chmod(0)

        if os.access(folder, os.R_OK | os.X_OK):
            pytest.skip("This environment can still read the folder after chmod(0).")

        neatify.organize_folder(str(folder), dry_run=False)
    finally:
        folder.chmod(original_mode)


def test_malformed_filename_with_history_delimiter_can_be_undone(isolated_app_files, make_file, tmp_path):
    source = make_file(tmp_path / "name -> with arrow.pdf")
    destination = tmp_path / "Documents" / source.name
    destination.parent.mkdir()

    neatify.move_file(str(source), str(destination), dry_run=False, move_id="move_delimiter")

    assert neatify.undo_last_move() == "Undone 1 files."
    assert source.exists()
