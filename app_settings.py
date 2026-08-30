"""Loads and saves Neatify app preferences."""

import json
import os


SETTINGS_FILE = "neatify_settings.json"


def get_default_settings():
    return {
        "theme": "midnight",
        "search_type": "All",
        "include_subfolders": True,
    }


def load_app_settings():
    if not os.path.exists(SETTINGS_FILE):
        return get_default_settings()

    with open(SETTINGS_FILE, "r") as settings_file:
        settings = json.load(settings_file)

    defaults = get_default_settings()

    for key in defaults:
        if key not in settings:
            settings[key] = defaults[key]

    return settings


def save_app_settings(settings):
    with open(SETTINGS_FILE, "w") as settings_file:
        json.dump(settings, settings_file, indent=4)
