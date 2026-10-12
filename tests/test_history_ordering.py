"""Tests for History page ordering."""

import pytest

import window


pytestmark = pytest.mark.safety


def test_history_batches_are_sorted_by_time_not_storage_source(monkeypatch):
    history_items = [
        {
            "time": "2026-10-11 23:57:43",
            "move_id": "sqlite_new",
            "action": "Moved",
            "item": "new.csv",
            "from": "/Downloads",
            "to": "/Downloads/Spreadsheets",
            "path_for_icon": "/Downloads/Spreadsheets/new.csv",
            "old_path": "/Downloads/new.csv",
            "new_path": "/Downloads/Spreadsheets/new.csv",
        },
        {
            "time": "2026-10-11 18:49:28",
            "move_id": "legacy_old",
            "action": "Moved",
            "item": "old.png",
            "from": "/Desktop",
            "to": "/Desktop/Images",
            "path_for_icon": "/Desktop/Images/old.png",
            "old_path": "/Desktop/old.png",
            "new_path": "/Desktop/Images/old.png",
        },
    ]

    monkeypatch.setattr(window, "read_history_items", lambda: history_items)

    neatify_window = window.NeatifyWindow.__new__(window.NeatifyWindow)
    batches = neatify_window.get_history_batches()

    assert [batch["move_id"] for batch in batches] == ["sqlite_new", "legacy_old"]
