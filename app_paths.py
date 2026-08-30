"""Builds paths used by Neatify in development and packaged app mode."""

import os
import sys
import tempfile


APP_NAME = "Neatify"


def get_project_path(*path_parts):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, *path_parts)


def get_user_data_folder():
    home = os.path.expanduser("~")

    if sys.platform == "darwin":
        data_folder = os.path.join(home, "Library", "Application Support", APP_NAME)
    elif sys.platform == "win32":
        app_data = os.environ.get("APPDATA", home)
        data_folder = os.path.join(app_data, APP_NAME)
    else:
        data_folder = os.path.join(home, ".local", "share", APP_NAME)

    try:
        os.makedirs(data_folder, exist_ok=True)
        return data_folder
    except OSError:
        fallback_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".neatify_data")

        try:
            os.makedirs(fallback_folder, exist_ok=True)
            return fallback_folder
        except OSError:
            temp_folder = os.path.join(tempfile.gettempdir(), APP_NAME)
            os.makedirs(temp_folder, exist_ok=True)
            return temp_folder


def get_user_data_path(file_name):
    return os.path.join(get_user_data_folder(), file_name)


def migrate_local_file(file_name):
    old_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    new_path = get_user_data_path(file_name)

    if old_path != new_path and os.path.exists(old_path) and not os.path.exists(new_path):
        with open(old_path, "r", encoding="utf-8") as old_file:
            contents = old_file.read()

        with open(new_path, "w", encoding="utf-8") as new_file:
            new_file.write(contents)

    return new_path
