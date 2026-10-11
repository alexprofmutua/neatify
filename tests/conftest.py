"""Shared test fixtures for Neatify safety tests."""

import os
import sys

import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def isolated_app_files(tmp_path, monkeypatch):
    """Keep tests away from the user's real Neatify settings and history."""
    import journal
    import neatify
    import rules

    history_path = tmp_path / "neatify_history.txt"
    journal_path = tmp_path / "neatify_journal.jsonl"
    rules_path = tmp_path / "neatify_rules.json"

    monkeypatch.setattr(neatify, "get_history_path", lambda: str(history_path))
    monkeypatch.setattr(journal, "get_journal_path", lambda: str(journal_path))
    monkeypatch.setattr(rules, "get_rules_file", lambda: str(rules_path))

    return {
        "history_path": history_path,
        "journal_path": journal_path,
        "rules_path": rules_path,
    }


@pytest.fixture
def make_file():
    def _make_file(path, contents="data"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    return _make_file
