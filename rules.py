"""Loads and saves user organization rules."""

import json
import os

from app_paths import migrate_local_file
from neatify import extension_categories


DEFAULT_EXTENSION_VERSION = 3

DEFAULT_EXTENSION_UPDATES = {
    "xls": "Spreadsheets",
    "xlsx": "Spreadsheets",
    "csv": "Spreadsheets",
    "ppt": "Presentations",
    "pptx": "Presentations",
}


def get_default_rules():
    return {
        "extensions": extension_categories.copy(),
        "keywords": {},
        "keyword_rules": [],
        "default_extension_version": DEFAULT_EXTENSION_VERSION,
    }


def get_rules_file():
    return migrate_local_file("neatify_rules.json")


def load_rules():
    rules_file_path = get_rules_file()

    if not os.path.exists(rules_file_path):
        return get_default_rules()

    with open(rules_file_path, "r", encoding="utf-8") as rules_file:
        rules = json.load(rules_file)

    rules_changed = False

    if "extensions" not in rules:
        rules["extensions"] = extension_categories.copy()
        rules["default_extension_version"] = DEFAULT_EXTENSION_VERSION
        rules_changed = True
    else:
        default_extension_version = rules.get("default_extension_version", 1)

        if default_extension_version < DEFAULT_EXTENSION_VERSION:
            for extension in extension_categories:
                if extension not in rules["extensions"]:
                    rules["extensions"][extension] = extension_categories[extension]

            if default_extension_version < 3:
                for extension in DEFAULT_EXTENSION_UPDATES:
                    if rules["extensions"].get(extension) == "Documents":
                        rules["extensions"][extension] = DEFAULT_EXTENSION_UPDATES[extension]

            rules["default_extension_version"] = DEFAULT_EXTENSION_VERSION
            rules_changed = True

    if "keywords" not in rules:
        rules["keywords"] = {}

    if "keyword_rules" not in rules:
        rules["keyword_rules"] = []

    for keyword in rules["keywords"]:
        existing_rule = find_keyword_rule(rules["keyword_rules"], keyword, "")

        if existing_rule is None:
            rules["keyword_rules"].append({
                "keyword": keyword,
                "destination": rules["keywords"][keyword],
                "scope": "",
            })
            rules_changed = True

    if rules_changed:
        try:
            save_rules(rules)
        except OSError:
            pass

    return rules


def save_rules(rules):
    rules_file_path = get_rules_file()

    with open(rules_file_path, "w", encoding="utf-8") as rules_file:
        json.dump(rules, rules_file, indent=4)


def get_category_for_file(file_name):
    return get_arrangement_for_file(file_name)["destination"]


def get_arrangement_for_file(file_name, folder_path=""):
    rules = load_rules()
    return get_arrangement_for_file_with_rules(file_name, folder_path, rules)


def get_arrangement_for_file_with_rules(file_name, folder_path, rules):
    lowered_file_name = file_name.lower()
    normalized_folder_path = normalize_scope_path(folder_path)

    folder_rules = []
    global_rules = []

    for rule in rules["keyword_rules"]:
        keyword = rule.get("keyword", "")
        scope = normalize_scope_path(rule.get("scope", ""))

        if keyword == "":
            continue

        if keyword.lower() not in lowered_file_name:
            continue

        if scope != "" and scope == normalized_folder_path:
            folder_rules.append(rule)
        elif scope == "":
            global_rules.append(rule)

    for rule in folder_rules + global_rules:
        return {
            "destination": clean_destination_folder(rule.get("destination", "Other")),
            "reason": "Keyword: " + rule.get("keyword", ""),
        }

    for keyword in rules["keywords"]:
        if keyword.lower() in lowered_file_name:
            return {
                "destination": clean_destination_folder(rules["keywords"][keyword]),
                "reason": "Keyword: " + keyword,
            }

    extension = get_extension_from_file_name(file_name)

    destination = rules["extensions"].get(extension, "Other")

    return {
        "destination": clean_destination_folder(destination),
        "reason": "Extension: " + extension,
    }


def find_keyword_rule(keyword_rules, keyword, scope):
    clean_keyword = keyword.lower()
    clean_scope = normalize_scope_path(scope)

    for rule in keyword_rules:
        if rule.get("keyword", "").lower() == clean_keyword and normalize_scope_path(rule.get("scope", "")) == clean_scope:
            return rule

    return None


def normalize_scope_path(scope):
    if scope == "":
        return ""

    return os.path.abspath(os.path.expanduser(scope))


def clean_destination_folder(destination):
    clean_parts = []

    for part in destination.replace("\\", "/").split("/"):
        clean_part = part.strip()

        if clean_part in ["", ".", ".."]:
            continue

        clean_parts.append(clean_part)

    if len(clean_parts) == 0:
        return "Other"

    return os.path.join(*clean_parts)


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


def add_keyword_rule(keyword, category, scope=""):
    rules = load_rules()
    clean_keyword = keyword.lower()
    clean_scope = normalize_scope_path(scope)
    clean_destination = clean_destination_folder(category)

    if clean_scope == "":
        rules["keywords"][clean_keyword] = clean_destination

    existing_rule = find_keyword_rule(rules["keyword_rules"], clean_keyword, clean_scope)

    if existing_rule is None:
        rules["keyword_rules"].append({
            "keyword": clean_keyword,
            "destination": clean_destination,
            "scope": clean_scope,
        })
    else:
        existing_rule["destination"] = clean_destination

    save_rules(rules)


def remove_extension_rule(extension):
    rules = load_rules()
    clean_extension = extension.lower().replace(".", "")

    if clean_extension in rules["extensions"]:
        del rules["extensions"][clean_extension]

    save_rules(rules)


def remove_keyword_rule(keyword, scope=None):
    rules = load_rules()
    clean_keyword = keyword.lower()

    if scope is None and clean_keyword in rules["keywords"]:
        del rules["keywords"][clean_keyword]

    if scope is None:
        rules["keyword_rules"] = [
            rule for rule in rules["keyword_rules"]
            if rule.get("keyword", "").lower() != clean_keyword
        ]
    else:
        clean_scope = normalize_scope_path(scope)
        rules["keyword_rules"] = [
            rule for rule in rules["keyword_rules"]
            if not (
                rule.get("keyword", "").lower() == clean_keyword
                and normalize_scope_path(rule.get("scope", "")) == clean_scope
            )
        ]

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
