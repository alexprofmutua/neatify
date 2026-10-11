"""Tests for current find/search behavior."""

import pytest

import rules


pytestmark = pytest.mark.safety


def test_find_with_filters_can_search_only_current_folder(isolated_app_files, make_file, tmp_path):
    root = tmp_path / "root"
    make_file(root / "invoice.pdf")
    make_file(root / "nested" / "invoice_nested.pdf")

    results = rules.find_with_filters("invoice", str(root), search_type="Files", include_subfolders=False)

    assert str(root / "invoice.pdf") in results
    assert str(root / "nested" / "invoice_nested.pdf") not in results


def test_find_with_filters_can_include_subfolders(isolated_app_files, make_file, tmp_path):
    root = tmp_path / "root"
    make_file(root / "invoice.pdf")
    make_file(root / "nested" / "invoice_nested.pdf")

    results = rules.find_with_filters("invoice", str(root), search_type="Files", include_subfolders=True)

    assert str(root / "invoice.pdf") in results
    assert str(root / "nested" / "invoice_nested.pdf") in results
