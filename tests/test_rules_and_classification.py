"""Tests for rule classification behavior."""

import os

import pytest

import rules


pytestmark = pytest.mark.safety


def test_default_extension_classification_uses_sensible_categories(isolated_app_files):
    loaded_rules = rules.load_rules()

    assert rules.get_arrangement_for_file_with_rules("photo.HEIC", "", loaded_rules)["destination"] == "Images"
    assert rules.get_arrangement_for_file_with_rules("notes.md", "", loaded_rules)["destination"] == "Documents"
    assert rules.get_arrangement_for_file_with_rules("budget.xlsx", "", loaded_rules)["destination"] == "Spreadsheets"
    assert rules.get_arrangement_for_file_with_rules("slides.pptx", "", loaded_rules)["destination"] == "Presentations"
    assert rules.get_arrangement_for_file_with_rules("installer.exe", "", loaded_rules)["destination"] == "Installers"
    assert rules.get_arrangement_for_file_with_rules("unknown.custom", "", loaded_rules)["destination"] == "Other"


def test_folder_keyword_rule_beats_global_keyword_rule(isolated_app_files, tmp_path):
    folder = tmp_path / "class"
    other_folder = tmp_path / "other"
    folder.mkdir()
    other_folder.mkdir()

    loaded_rules = {
        "extensions": {"pdf": "Documents"},
        "keywords": {},
        "keyword_rules": [
            {"keyword": "invoice", "destination": "Global Receipts", "scope": ""},
            {"keyword": "invoice", "destination": "Class Receipts", "scope": str(folder)},
        ],
    }

    assert rules.get_arrangement_for_file_with_rules("invoice.pdf", str(folder), loaded_rules)["destination"] == "Class Receipts"
    assert rules.get_arrangement_for_file_with_rules("invoice.pdf", str(other_folder), loaded_rules)["destination"] == "Global Receipts"


def test_keyword_rule_beats_extension_rule(isolated_app_files):
    loaded_rules = {
        "extensions": {"pdf": "Documents"},
        "keywords": {},
        "keyword_rules": [
            {"keyword": "resume", "destination": "Applications", "scope": ""},
        ],
    }

    result = rules.get_arrangement_for_file_with_rules("resume.pdf", "", loaded_rules)

    assert result["destination"] == "Applications"
    assert result["reason"] == "Keyword: resume"


def test_folder_extension_rule_beats_global_extension_rule(isolated_app_files, tmp_path):
    folder = tmp_path / "downloads"
    other_folder = tmp_path / "desktop"
    folder.mkdir()
    other_folder.mkdir()

    loaded_rules = {
        "extensions": {"pdf": "Documents"},
        "extension_rules": [
            {"extension": "pdf", "destination": "Class PDFs", "scope": str(folder)},
        ],
        "keywords": {},
        "keyword_rules": [],
    }

    assert rules.get_arrangement_for_file_with_rules("notes.pdf", str(folder), loaded_rules)["destination"] == "Class PDFs"
    assert rules.get_arrangement_for_file_with_rules("notes.pdf", str(other_folder), loaded_rules)["destination"] == "Documents"


def test_keyword_rule_still_beats_folder_extension_rule(isolated_app_files, tmp_path):
    folder = tmp_path / "downloads"
    folder.mkdir()

    loaded_rules = {
        "extensions": {"pdf": "Documents"},
        "extension_rules": [
            {"extension": "pdf", "destination": "Folder PDFs", "scope": str(folder)},
        ],
        "keywords": {},
        "keyword_rules": [
            {"keyword": "resume", "destination": "Applications", "scope": ""},
        ],
    }

    assert rules.get_arrangement_for_file_with_rules("resume.pdf", str(folder), loaded_rules)["destination"] == "Applications"


def test_destination_folder_cleans_path_traversal_parts():
    cleaned = rules.clean_destination_folder("../Reports/./Invoices")

    assert cleaned == os.path.join("Reports", "Invoices")


def test_remove_global_keyword_rule_removes_legacy_keyword_map(isolated_app_files):
    rules.add_keyword_rule("invoice", "Receipts", "")

    loaded_rules = rules.load_rules()
    assert loaded_rules["keywords"]["invoice"] == "Receipts"
    assert rules.get_arrangement_for_file_with_rules("invoice.pdf", "", loaded_rules)["destination"] == "Receipts"

    rules.remove_keyword_rule("invoice", "")

    loaded_rules = rules.load_rules()
    assert "invoice" not in loaded_rules["keywords"]
    assert rules.get_arrangement_for_file_with_rules("invoice.pdf", "", loaded_rules)["destination"] == "Documents"


def test_remove_global_extension_rule_restores_other_classification(isolated_app_files):
    rules.add_extension_rule("custom", "Custom Files", "")

    loaded_rules = rules.load_rules()
    assert rules.get_arrangement_for_file_with_rules("sample.custom", "", loaded_rules)["destination"] == "Custom Files"

    rules.remove_extension_rule("custom", "")

    loaded_rules = rules.load_rules()
    assert "custom" not in loaded_rules["extensions"]
    assert rules.get_arrangement_for_file_with_rules("sample.custom", "", loaded_rules)["destination"] == "Other"


def test_remove_scoped_keyword_rule_keeps_global_rule(isolated_app_files, tmp_path):
    folder = tmp_path / "downloads"
    folder.mkdir()

    rules.add_keyword_rule("invoice", "Global Receipts", "")
    rules.add_keyword_rule("invoice", "Folder Receipts", str(folder))

    loaded_rules = rules.load_rules()
    assert rules.get_arrangement_for_file_with_rules("invoice.pdf", str(folder), loaded_rules)["destination"] == "Folder Receipts"

    rules.remove_keyword_rule("invoice", str(folder))

    loaded_rules = rules.load_rules()
    assert rules.get_arrangement_for_file_with_rules("invoice.pdf", str(folder), loaded_rules)["destination"] == "Global Receipts"
