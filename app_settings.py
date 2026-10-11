"""Loads and saves Neatify app preferences."""

import json
import os

from app_paths import migrate_local_file


def get_default_settings():
    return {
        "theme": "finder_light",
        "search_type": "All",
        "include_subfolders": True,
        "arrangement_structure": "Rule Only",
        "arrangement_date_source": "Modified Date",
        "default_theme_version": 2,
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

    migrated_default_theme = False

    if settings.get("default_theme_version") is None and settings.get("theme") == "midnight":
        settings["theme"] = defaults["theme"]
        migrated_default_theme = True

    for key in defaults:
        if key not in settings:
            settings[key] = defaults[key]

    if migrated_default_theme:
        save_app_settings(settings)

    return settings


def save_app_settings(settings):
    settings_file_path = get_settings_file()

    with open(settings_file_path, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=4)
