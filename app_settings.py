"""Loads and saves Neatify app preferences."""

import json
import os

from app_paths import migrate_local_file


def get_default_settings():
    return {
        "theme": "midnight",
        "search_type": "All",
        "include_subfolders": True,
    }


def get_settings_file():
    return migrate_local_file("neatify_settings.json")


def load_app_settings():
    settings_file_path = get_settings_file()

    if not os.path.exists(settings_file_path):
        return get_default_settings()

    with open(settings_file_path, "r", encoding="utf-8") as settings_file:
        settings = json.load(settings_file)

    defaults = get_default_settings()

    for key in defaults:
        if key not in settings:
            settings[key] = defaults[key]

    return settings


def save_app_settings(settings):
    settings_file_path = get_settings_file()

    with open(settings_file_path, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=4)
