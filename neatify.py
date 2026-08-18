# Python toools for working with files and folders
import os
import platform
# Imports tools for opening files on macOS and Linux
import subprocess
# Imports Python's date/time tools
from datetime import datetime

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

    "pdf": "Documents",
    "doc": "Documents",
    "docx": "Documents",
    "txt": "Documents",
    "rtf": "Documents",
    "odt": "Documents",

    "xls": "Spreadsheets",
    "xlsx": "Spreadsheets",
    "csv": "Spreadsheets",

    "ppt": "Presentations",
    "pptx": "Presentations",

    "mp4": "Videos",
    "mov": "Videos",
    "avi": "Videos",
    "mkv": "Videos",

    "mp3": "Audio",
    "wav": "Audio",
    "aac": "Audio",
    "m4a": "Audio",

    "zip": "Archives",
    "rar": "Archives",
    "7z": "Archives",
    "tar": "Archives",
    "gz": "Archives",

    "py": "Code",
    "js": "Code",
    "html": "Code",
    "css": "Code",
    "java": "Code",
    "cpp": "Code",
    "c": "Code",
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
        subprocess.run("xdg-open", full_path)
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

    for results in results:
        print(str(number) + ".", results)
        number = number + 1

def move_file(full_path, destination, dry_run):
    if dry_run:
        print("Would move:", full_path, "->", destination)
    else:
        move_id = create_move_id()
        system.rename(full_path, destination)
        print("Moved:", full_path, "->", destination)
        write_history("Moved", full_path, destination, move_id)

def create_move_id():
    return "move_" + datetime.now().strftime("%Y%m%d%H%MS%f")

def write_history(action, old_path, new_path, move_id):
    # Gets the current date and time and Formats the date/time into readable text, in that order
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Opens the history file in append mode and closes it afterwards.
    with open("neatify_history.txt", "a") as history_file:
        history_file.write(timestamp + " | " + move_id + " | " + action + " | " + old_path + " -> " + new_path + "\n")

def undo_last_move():
    history_path = "neatify_history.txt"

    if not paths.exists(history_path):
        print("No history file found.")
        return

    with open(history_path, "r") as history_file:
        lines = history_file.readlines()

    undone_move_ids = []

    for line in reversed(lines):
        parts = line.strip().split(" | ")

        if len(parts) != 4:
            continue
        move_id = parts[1]
        action = parts[2]
        paths_part = parts[3]

        if action == "UNDONE":
            undone_move_ids.append(move_id)
            continue

        if " | MOVED | " and move_id not in undone_move_ids:
            old_path, new_path = paths_part.split(" -> ")
            
            if not paths.exists(new_path):
                print("Error: moved file does not exist:", new_path)
                return

            if paths.exists(old_path):
                print("Error: original location already has a file:", old_path)
                return

            system.rename(new_path, old_path)
            print("Undone:", new_path, "->", old_path)
            write_history("UNDONE", new_path, old_path, move_id)
            return

    print("No move history found.")

def get_unique_destination(destination):
    if not paths.exists(destination):
        return destination

    folder = paths.dirname(destination)
    file_name = paths.basename(destination)

    name, extension = paths.splitext(file_name)

    counter = 1

    while True:
        new_file_name = name + "_" + str(counter) + extension
        new_destination = paths.join(folder, new_file_name)

        if not paths.exists(new_destination):
            return new_destination

        counter = counter + 1


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

    for folder_name in folder_names:
        folder_path = paths.join(home, folder_name)

        if paths.exists(folder_path) and paths.isdir(folder_path):
            folders.append(folder_path)

    return folders

def organize_common_folders(dry_run=True):
    folders = get_common_folders()

    for folder in folders:
        print("Organizing folder:", folder)
        organize_folder(folder, dry_run)

def organize_folder(folder_path, dry_run=True):
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

    # Converting the files in folder into full paths
    for file in system.listdir(folder):
        # Skips hidden files
        if file[:1] == ".":
            hidden_count = hidden_count + 1
            continue

        full_path = paths.join(folder, file)

        if paths.isfile(full_path):
            extension = get_extension(file)
            # Looks for extension in dictionary, if it finds it, use it in category, if not, use "Other"
            category = extension_categories.get(extension, "Other")

            # exist_ok = True, Do not crash if the folder already exists.
            extension_folder = paths.join(folder, category)
            # Creating the folder
            system.makedirs(extension_folder, exist_ok=True)
            # Creates the final path where the file would go
            destination = paths.join(extension_folder, file)
            unique_destination = get_unique_destination(destination)
            move_file(full_path, unique_destination, dry_run)
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