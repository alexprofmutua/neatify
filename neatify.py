# Python toools for working with files and folders
import os
import platform
# Imports tools for opening files on macOS and Linux
import subprocess
# Imports Python's date/time tools
from datetime import datetime
from app_paths import migrate_local_file
from journal import append_move_state, append_move_states, create_move_state_record, create_operation_id, get_journal_path, read_journal_records
from sqlite_store import get_sqlite_operation_ids, import_legacy_history_items, mark_batch_undone, read_sqlite_history_items, record_batch_plan, record_batch_results, recover_sqlite_operations

# Shortcuts
system = os
paths = system.path

folders_to_organize = [
    "~/Downloads",
    "~/Desktop",
    "~/Documents",
    "~/Pictures",
    "~/Music",
    "~/Movies",
]

extension_categories = {
    "jpg": "Images",
    "jpeg": "Images",
    "png": "Images",
    "gif": "Images",
    "webp": "Images",
    "svg": "Images",
    "heic": "Images",

    "pdf": "Documents",
    "doc": "Documents",
    "docx": "Documents",
    "txt": "Documents",
    "rtf": "Documents",
    "md": "Documents",

    "xls": "Spreadsheets",
    "xlsx": "Spreadsheets",
    "csv": "Spreadsheets",

    "ppt": "Presentations",
    "pptx": "Presentations",

    "mp4": "Videos",
    "mov": "Videos",
    "avi": "Videos",
    "mkv": "Videos",
    "webm": "Videos",

    "mp3": "Audio",
    "wav": "Audio",
    "m4a": "Audio",

    "zip": "Archives",
    "rar": "Archives",
    "7z": "Archives",
    "tar": "Archives",
    "gz": "Archives",
    "dmg": "Archives",

    "py": "Code",
    "js": "Code",
    "html": "Code",
    "css": "Code",
    "java": "Code",
    "cpp": "Code",
    "c": "Code",
    "json": "Code",

    "exe": "Installers",
    "msi": "Installers",
    "pkg": "Installers",
}

def get_extension(file_name):
    if "." in file_name:
        parts = file_name.split(".")
        extension = parts[-1].lower()
    else:
        extension = "other"

    return extension

# Find item starting from ~, which is normally home folder
def find_item(item_name, search_folder="~"):
    search_path = paths.expanduser(search_folder)
    found_items = []

    if not paths.exists(search_path):
        print("Error: search folder does not exists:", search_path)
        return found_items

    search_name = item_name.lower()

    for current_folder, folders, files in system.walk(search_path):
        for folder in folders:
            if search_name in folder.lower():
                found_items.append(paths.join(current_folder, folder))

        for file in files:
            if search_name in file.lower():
                found_items.append(paths.join(current_folder, file))

    return found_items

def open_item(item_path):
    full_path = paths.expanduser(item_path)

    if not paths.exists(full_path):
        print("Error: item does not exist:", full_path)
        return
    # Checks the operating system
    os_name = platform.system()

    if os_name == "Darwin":
        subprocess.run(["open", full_path])
    elif os_name == "Windows":
        system.startfile(full_path)
    elif os_name == "Linux":
        subprocess.run(["xdg-open", full_path])
    else:
        print("Error: opening files is not supported on this OS.")

def find_and_open(item_name, search_folder="~"):
    results = find_item(item_name, search_folder)

    if len(results) == 0:
        print("No matching item found.")
        return

    if len(results) == 1:
        open_item(results[0])
        return
    # If several items found, list them instead of opening any of them
    print("Multiple items found:")

    number = 1

    for result in results:
        print(str(number) + ".", result)
        number = number + 1

def move_file(full_path, destination, dry_run, move_id=None, quiet=False):
    if dry_run:
        if not quiet:
            print("Would move:", full_path, "->", destination)
    else:
        if move_id is None:
            move_id = create_move_id()

        operation_id = create_operation_id()

        if paths.exists(destination):
            raise FileExistsError("Destination already exists: " + destination)

        prepared_move = {
            "operation_id": operation_id,
            "old_path": full_path,
            "new_path": destination,
        }

        record_batch_plan(move_id, [prepared_move])
        append_move_state(operation_id, move_id, full_path, destination, "planned")
        append_move_state(operation_id, move_id, full_path, destination, "moving")

        try:
            system.rename(full_path, destination)
        except OSError as error:
            failed_move = prepared_move.copy()
            failed_move["error"] = str(error)
            record_batch_results(move_id, [], [failed_move])
            raise

        append_move_state(operation_id, move_id, full_path, destination, "moved")
        record_batch_results(move_id, [prepared_move], [])
        if not quiet:
            print("Moved:", full_path, "->", destination)
        append_move_state(operation_id, move_id, full_path, destination, "history_committed")


def move_files_batch(move_plan, move_id=None):
    if move_id is None:
        move_id = create_move_id()

    prepared_moves = []
    errors = []

    for move in move_plan:
        old_path = move["old_path"]
        new_path = move["new_path"]

        if not paths.exists(old_path):
            errors.append("Missing: " + old_path)
            continue

        if paths.exists(new_path):
            errors.append("Destination already exists: " + new_path)
            continue

        prepared_moves.append({
            "operation_id": create_operation_id(),
            "old_path": old_path,
            "new_path": new_path,
        })

    # One durable SQLite transaction records the whole batch before any file moves.
    record_batch_plan(move_id, prepared_moves)

    moved_moves = []
    failed_moves = []
    moved_count = 0

    for move in prepared_moves:
        old_path = move["old_path"]
        new_path = move["new_path"]

        try:
            system.makedirs(paths.dirname(new_path), exist_ok=True)

            if paths.exists(new_path):
                raise FileExistsError("Destination already exists: " + new_path)

            system.rename(old_path, new_path)
            moved_count = moved_count + 1
            moved_moves.append(move)
        except OSError as error:
            errors.append(paths.basename(old_path) + ": " + str(error))
            failed_move = move.copy()
            failed_move["error"] = str(error)
            failed_moves.append(failed_move)

    record_batch_results(move_id, moved_moves, failed_moves)

    return {
        "move_id": move_id,
        "moved_count": moved_count,
        "errors": errors,
    }

def create_move_id():
    return "move_" + datetime.now().strftime("%Y%m%d%H%M%S%f")

def create_history_record(action, old_path, new_path, move_id):
    # Gets the current date and time and Formats the date/time into readable text, in that order
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "version": 1,
        "time": timestamp,
        "move_id": move_id,
        "action": action,
        "old_path": old_path,
        "new_path": new_path,
    }


def write_history(action, old_path, new_path, move_id):
    write_history_records([create_history_record(action, old_path, new_path, move_id)])


def write_history_records(history_records):
    # Opens the history file in append mode and closes it afterwards.
    import json

    history_path = get_history_path()
    history_folder = paths.dirname(history_path)
    system.makedirs(history_folder, exist_ok=True)

    with open(history_path, "a", encoding="utf-8") as history_file:
        for history_record in history_records:
            history_file.write(json.dumps(history_record, sort_keys=True, ensure_ascii=False) + "\n")

        history_file.flush()
        system.fsync(history_file.fileno())

def parse_history_line(line):
    import json

    stripped_line = line.strip()

    if stripped_line == "":
        return None

    if stripped_line.startswith("{"):
        try:
            history_record = json.loads(stripped_line)
        except json.JSONDecodeError:
            return None

        required_keys = ["time", "move_id", "action", "old_path", "new_path"]

        for key in required_keys:
            if key not in history_record:
                return None

        return {
            "time": history_record["time"],
            "move_id": history_record["move_id"],
            "action": history_record["action"],
            "item": paths.basename(history_record["old_path"]),
            "from": paths.dirname(history_record["old_path"]),
            "to": paths.dirname(history_record["new_path"]),
            "path_for_icon": history_record["new_path"],
            "old_path": history_record["old_path"],
            "new_path": history_record["new_path"],
        }

    parts = stripped_line.split(" | ", 3)

    if len(parts) != 4:
        return None

    timestamp = parts[0]
    move_id = parts[1]
    action = parts[2]
    paths_part = parts[3]

    if paths_part.count(" -> ") != 1:
        return None

    old_path, new_path = paths_part.split(" -> ", 1)

    return {
        "time": timestamp,
        "move_id": move_id,
        "action": action,
        "item": paths.basename(old_path),
        "from": paths.dirname(old_path),
        "to": paths.dirname(new_path),
        "path_for_icon": new_path,
        "old_path": old_path,
        "new_path": new_path,
    }

def read_history_items():
    import_legacy_history_once()
    return read_sqlite_history_items()


def import_legacy_history_once():
    history_path = get_history_path()

    if not paths.exists(history_path):
        return 0

    legacy_items = []

    with open(history_path, "r", encoding="utf-8") as history_file:
        for line in history_file:
            history_item = parse_history_line(line)

            if history_item is not None:
                legacy_items.append(history_item)

    return import_legacy_history_items(history_path, legacy_items)

def get_history_path():
    return migrate_local_file("neatify_history.txt")

def undo_last_move():
    history_items = read_history_items()

    if len(history_items) == 0:
        print("No history file found.")
        return "No history file found."

    undone_move_ids = []

    for history_item in reversed(history_items):
        move_id = history_item["move_id"]
        action = history_item["action"]

        if action == "UNDONE":
            undone_move_ids.append(move_id)
            continue

        if action == "Moved" and move_id not in undone_move_ids:
            return undo_move_by_id(move_id)

    print("No move history found.")
    return "No move history found."

def undo_move_by_id(target_move_id):
    history_items = read_history_items()

    if len(history_items) == 0:
        return "No history file found."

    moves_to_undo = []
    undone_move_ids = []

    for history_item in history_items:
        move_id = history_item["move_id"]
        action = history_item["action"]

        if move_id != target_move_id:
            continue

        if action == "UNDONE":
            undone_move_ids.append(move_id)
            continue

        if action == "Moved":
            moves_to_undo.append(history_item)

    if target_move_id in undone_move_ids:
        return "This move has already been undone."

    if len(moves_to_undo) == 0:
        return "Move not found."

    for move_to_undo in moves_to_undo:
        old_path = move_to_undo["old_path"]
        new_path = move_to_undo["new_path"]

        if not paths.exists(new_path):
            return "Error: moved file does not exist: " + new_path

        if paths.exists(old_path):
            return "Error: original location already has a file: " + old_path

    for move_to_undo in moves_to_undo:
        old_path = move_to_undo["old_path"]
        new_path = move_to_undo["new_path"]
        operation_id = create_operation_id()
        append_move_state(operation_id, target_move_id, new_path, old_path, "undo_planned")
        append_move_state(operation_id, target_move_id, new_path, old_path, "undo_moving")
        system.rename(new_path, old_path)
        append_move_state(operation_id, target_move_id, new_path, old_path, "undo_moved")
        append_move_state(operation_id, target_move_id, new_path, old_path, "undo_history_committed")

    mark_batch_undone(target_move_id)

    return "Undone " + str(len(moves_to_undo)) + " files."

def recover_incomplete_operations():
    sqlite_recovery_result = recover_sqlite_operations()
    sqlite_operation_ids = get_sqlite_operation_ids()
    recovered_count = 0
    conflict_count = 0
    operations = {}

    for record in read_journal_records():
        operation_id = record.get("operation_id")

        if operation_id is None:
            continue

        if operation_id in sqlite_operation_ids:
            continue

        operations.setdefault(operation_id, []).append(record)

    completed_states = [
        "history_committed",
        "failed",
        "recovered_no_move",
        "recovery_conflict",
        "undo_history_committed",
        "undo_failed",
    ]

    for operation_id in operations:
        records = operations[operation_id]
        latest_record = records[-1]
        latest_state = latest_record.get("state")

        if latest_state in completed_states:
            continue

        batch_id = latest_record.get("batch_id")
        source_path = latest_record.get("source_path")
        destination_path = latest_record.get("destination_path")

        if source_path is None or destination_path is None:
            continue

        source_exists = paths.exists(source_path)
        destination_exists = paths.exists(destination_path)

        if latest_state in ["planned", "moving"]:
            if destination_exists and not source_exists:
                append_move_state(operation_id, batch_id, source_path, destination_path, "moved")
                write_history("Moved", source_path, destination_path, batch_id)
                append_move_state(operation_id, batch_id, source_path, destination_path, "history_committed")
                recovered_count = recovered_count + 1
            elif source_exists and not destination_exists:
                append_move_state(operation_id, batch_id, source_path, destination_path, "recovered_no_move")
            else:
                append_move_state(operation_id, batch_id, source_path, destination_path, "recovery_conflict")
                conflict_count = conflict_count + 1
        elif latest_state == "moved":
            if destination_exists and not source_exists:
                write_history("Moved", source_path, destination_path, batch_id)
                append_move_state(operation_id, batch_id, source_path, destination_path, "history_committed")
                recovered_count = recovered_count + 1
            else:
                append_move_state(operation_id, batch_id, source_path, destination_path, "recovery_conflict")
                conflict_count = conflict_count + 1
        elif latest_state in ["undo_planned", "undo_moving"]:
            if destination_exists and not source_exists:
                append_move_state(operation_id, batch_id, source_path, destination_path, "undo_moved")
                write_history("UNDONE", source_path, destination_path, batch_id)
                append_move_state(operation_id, batch_id, source_path, destination_path, "undo_history_committed")
                recovered_count = recovered_count + 1
            elif source_exists and not destination_exists:
                append_move_state(operation_id, batch_id, source_path, destination_path, "recovered_no_move")
            else:
                append_move_state(operation_id, batch_id, source_path, destination_path, "recovery_conflict")
                conflict_count = conflict_count + 1
        elif latest_state == "undo_moved":
            if destination_exists and not source_exists:
                write_history("UNDONE", source_path, destination_path, batch_id)
                append_move_state(operation_id, batch_id, source_path, destination_path, "undo_history_committed")
                recovered_count = recovered_count + 1
            else:
                append_move_state(operation_id, batch_id, source_path, destination_path, "recovery_conflict")
                conflict_count = conflict_count + 1

    return {
        "recovered": recovered_count + sqlite_recovery_result["recovered"],
        "conflicts": conflict_count + sqlite_recovery_result["conflicts"],
    }

def get_unique_destination(destination):
    if not paths.exists(destination):
        return destination

    folder = paths.dirname(destination)
    file_name = paths.basename(destination)

    name, extension = paths.splitext(file_name)

    counter = 2

    while True:
        new_file_name = name + " " + str(counter) + extension
        new_destination = paths.join(folder, new_file_name)

        if not paths.exists(new_destination):
            return new_destination

        counter = counter + 1


def get_folder_name_set(folder):
    names = set()

    try:
        with system.scandir(folder) as entries:
            for entry in entries:
                names.add(entry.name)
    except FileNotFoundError:
        return names
    except OSError:
        return names

    return names


def get_unique_destination_with_name_cache(destination, taken_names_by_folder):
    folder = paths.dirname(destination)
    file_name = paths.basename(destination)

    if folder not in taken_names_by_folder:
        taken_names_by_folder[folder] = get_folder_name_set(folder)

    taken_names = taken_names_by_folder[folder]

    if file_name not in taken_names:
        taken_names.add(file_name)
        return destination

    name, extension = paths.splitext(file_name)
    counter = 2

    while True:
        new_file_name = name + " " + str(counter) + extension

        if new_file_name not in taken_names:
            taken_names.add(new_file_name)
            return paths.join(folder, new_file_name)

        counter = counter + 1


def is_safe_destination(base_folder, destination):
    base_path = paths.realpath(paths.expanduser(base_folder))
    destination_path = paths.realpath(paths.expanduser(destination))

    try:
        return paths.commonpath([base_path, destination_path]) == base_path
    except ValueError:
        return False


def get_common_folder_names():
    os_name = platform.system()

    if os_name == "Darwin":
        return ["Downloads", "Desktop", "Documents", "Pictures", "Music", "Movies"]

    if os_name == "Windows":
        return ["Downloads", "Desktop", "Documents", "Pictures", "Music", "Videos"]

    if os_name == "Linux":
        return ["Downloads", "Desktop", "Documents", "Pictures", "Music", "Videos"]

    return ["Downloads", "Desktop", "Documents"]

def get_common_folders():
    home = paths.expanduser("~")
    folder_names = get_common_folder_names()

    folders = []
    candidate_roots = [home]

    if platform.system() == "Windows":
        for variable_name in ["USERPROFILE", "OneDrive", "OneDriveConsumer", "OneDriveCommercial"]:
            folder_root = os.environ.get(variable_name)

            if folder_root is not None and folder_root not in candidate_roots:
                candidate_roots.append(folder_root)

    for folder_name in folder_names:
        for candidate_root in candidate_roots:
            folder_path = paths.join(candidate_root, folder_name)
            normalized_path = paths.abspath(paths.expanduser(folder_path))

            if normalized_path in folders:
                continue

            if paths.exists(normalized_path) and paths.isdir(normalized_path):
                folders.append(normalized_path)
                break

    return folders

def organize_common_folders(dry_run=True):
    folders = get_common_folders()

    for folder in folders:
        print("Organizing folder:", folder)
        organize_folder(folder, dry_run)

def preview_organize_folder(folder_path):
    from rules import get_arrangement_for_file_with_rules, load_rules

    folder = paths.expanduser(folder_path)
    preview_groups = {}
    rules = load_rules()

    if not paths.exists(folder):
        return preview_groups

    if not paths.isdir(folder):
        return preview_groups

    for entry in sorted(system.scandir(folder), key=lambda item: item.name.lower()):
        file = entry.name
        full_path = entry.path

        try:
            is_file = entry.is_file(follow_symlinks=False)
        except OSError:
            continue

        if is_file:
            category = get_arrangement_for_file_with_rules(file, folder, rules)["destination"]

            if category not in preview_groups:
                preview_groups[category] = []

            preview_groups[category].append(file)

    return preview_groups

def organize_folder(folder_path, dry_run=True):
    from rules import get_arrangement_for_file_with_rules, load_rules

    # Converts the string into full path
    folder = paths.expanduser(folder_path)

    # If folder does not exist, put a message
    if not paths.exists(folder):
        print("Error: Folder does not exist:", folder)
        return

    # If path is not a folder, put a message
    if not paths.isdir(folder):
        print("Error: path is not a folder:", folder)
        return

    moved_count = 0
    hidden_count = 0
    folder_count = 0
    batch_id = create_move_id()
    rules = load_rules()
    taken_names_by_folder = {}

    try:
        folder_entries = sorted(system.scandir(folder), key=lambda item: item.name.lower())
    except PermissionError as error:
        print("Error: cannot read folder:", error)
        return
    except OSError as error:
        print("Error: cannot scan folder:", error)
        return

    # Converting the files in folder into full paths
    for entry in folder_entries:
        file = entry.name
        # Skips hidden files
        if file[:1] == ".":
            hidden_count = hidden_count + 1
            continue

        full_path = entry.path

        try:
            is_file = entry.is_file(follow_symlinks=False)
        except OSError:
            folder_count = folder_count + 1
            continue

        if is_file:
            # Looks for extension and keyword rules, if it finds one, use it as category, if not, use "Other"
            category = get_arrangement_for_file_with_rules(file, folder, rules)["destination"]

            # exist_ok = True, Do not crash if the folder already exists.
            extension_folder = paths.join(folder, category)
            # Creating the folder
            system.makedirs(extension_folder, exist_ok=True)
            # Creates the final path where the file would go
            destination = paths.join(extension_folder, file)
            unique_destination = get_unique_destination_with_name_cache(destination, taken_names_by_folder)

            if not is_safe_destination(folder, unique_destination):
                print("Skipped unsafe destination:", unique_destination)
            else:
                move_file(full_path, unique_destination, dry_run, batch_id)
                moved_count = moved_count + 1
        else:
            # If it is not a file, skip it and count as skipped
            folder_count = folder_count + 1

    print("Done.")

    if dry_run:
        print("Files that would be organized:", moved_count)
    else:
        print("Files organized:", moved_count)
    
    print("Hidden items skipped:", hidden_count)
    print("Folders skipped:", folder_count)

if __name__ == "__main__":
    organize_common_folders(dry_run=True)
