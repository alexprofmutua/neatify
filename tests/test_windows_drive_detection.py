"""Tests for Windows external drive detection."""

import os

import pytest

import neatify
import window


pytestmark = pytest.mark.safety


def test_windows_external_drive_detection_skips_system_and_unreadable_drives(monkeypatch):
    existing_paths = {"D:\\", "E:\\", "F:\\"}
    unreadable_paths = {"E:\\"}

    monkeypatch.setenv("SystemDrive", "C:")
    monkeypatch.setattr(window.os.path, "exists", lambda item_path: item_path in existing_paths)
    monkeypatch.setattr(window.os.path, "isdir", lambda item_path: item_path in existing_paths)

    def fake_listdir(item_path):
        if item_path in unreadable_paths:
            raise OSError("not readable")

        return []

    monkeypatch.setattr(window.os, "listdir", fake_listdir)

    assert window.get_windows_external_drive_paths() == ["D:\\", "F:\\"]


def test_windows_common_folders_include_onedrive_when_local_folder_is_missing(monkeypatch):
    existing_paths = {
        os.path.abspath("C:\\Users\\Alex/Downloads"),
        os.path.abspath("C:\\Users\\Alex\\OneDrive/Desktop"),
        os.path.abspath("C:\\Users\\Alex\\OneDrive/Documents"),
    }

    monkeypatch.setenv("USERPROFILE", "C:\\Users\\Alex")
    monkeypatch.setenv("OneDrive", "C:\\Users\\Alex\\OneDrive")
    monkeypatch.setattr(neatify.platform, "system", lambda: "Windows")
    monkeypatch.setattr(neatify.paths, "expanduser", lambda item_path: "C:\\Users\\Alex" if item_path == "~" else item_path)
    monkeypatch.setattr(neatify.paths, "exists", lambda item_path: os.path.abspath(item_path) in existing_paths)
    monkeypatch.setattr(neatify.paths, "isdir", lambda item_path: os.path.abspath(item_path) in existing_paths)

    common_folders = neatify.get_common_folders()

    assert os.path.abspath("C:\\Users\\Alex/Downloads") in common_folders
    assert os.path.abspath("C:\\Users\\Alex\\OneDrive/Desktop") in common_folders
    assert os.path.abspath("C:\\Users\\Alex\\OneDrive/Documents") in common_folders
