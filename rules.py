"""Loads and saves user organization rules."""

import json
import os

from neatify import extension_categories


RULES_FILE = "neatify_rules.json"


def get_default_rules():
    return {
        "extensions": extension_categories.copy(),
        "keywords": {},
    }


def load_rules():
    if not os.path.exists(RULES_FILE):
        return get_default_rules()

    with open(RULES_FILE, "r") as rules_file:
        rules = json.load(rules_file)

    if "extensions" not in rules:
        rules["extensions"] = extension_categories.copy()

    if "keywords" not in rules:
        rules["keywords"] = {}

    return rules


def save_rules(rules):
    with open(RULES_FILE, "w") as rules_file:
        json.dump(rules, rules_file, indent=4)


def get_category_for_file(file_name):
    rules = load_rules()
    lowered_file_name = file_name.lower()

    for keyword in rules["keywords"]:
        if keyword.lower() in lowered_file_name:
            return rules["keywords"][keyword]

    extension = get_extension_from_file_name(file_name)

    return rules["extensions"].get(extension, "Other")


def get_extension_from_file_name(file_name):
    if "." in file_name:
        parts = file_name.split(".")
        return parts[-1].lower()

    return "other"


def add_extension_rule(extension, category):
    rules = load_rules()
    clean_extension = extension.lower().replace(".", "")
    rules["extensions"][clean_extension] = category
    save_rules(rules)


def add_keyword_rule(keyword, category):
    rules = load_rules()
    rules["keywords"][keyword.lower()] = category
    save_rules(rules)


def remove_extension_rule(extension):
    rules = load_rules()
    clean_extension = extension.lower().replace(".", "")

    if clean_extension in rules["extensions"]:
        del rules["extensions"][clean_extension]

    save_rules(rules)


def remove_keyword_rule(keyword):
    rules = load_rules()
    clean_keyword = keyword.lower()

    if clean_keyword in rules["keywords"]:
        del rules["keywords"][clean_keyword]

    save_rules(rules)


def find_with_filters(search_text, search_folder, search_type="All", include_subfolders=True):
    search_path = os.path.expanduser(search_folder)
    clean_search_text = search_text.lower().replace(".", "")
    found_items = []

    if not os.path.exists(search_path):
        return found_items

    if not os.path.isdir(search_path):
        return found_items

    clean_search_type = search_type.lower()

    if include_subfolders:
        folders_to_search = []

        for current_folder, folders, files in os.walk(search_path):
            folders_to_search.append((current_folder, folders, files))
    else:
        folders = []
        files = []

        for item in os.listdir(search_path):
            full_path = os.path.join(search_path, item)

            if os.path.isdir(full_path):
                folders.append(item)
            elif os.path.isfile(full_path):
                files.append(item)

        folders_to_search = [(search_path, folders, files)]

    for current_folder, folders, files in folders_to_search:
        if clean_search_type in ["all", "folders"]:
            for folder in folders:
                if clean_search_text in folder.lower():
                    found_items.append(os.path.join(current_folder, folder))

        if clean_search_type == "folders":
            continue

        for file_name in files:
            full_path = os.path.join(current_folder, file_name)

            if not os.path.isfile(full_path):
                continue

            extension = get_extension_from_file_name(file_name)
            category = get_category_for_file(file_name)

            if clean_search_type != "all" and clean_search_type != "files":
                if clean_search_type != extension and clean_search_type != category.lower():
                    continue

            if clean_search_text == extension:
                found_items.append(full_path)
            elif clean_search_text == category.lower():
                found_items.append(full_path)
            elif clean_search_text in file_name.lower():
                found_items.append(full_path)

    return found_items
