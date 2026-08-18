# Python toools for working with files and folders
import os

# Shortcuts
system = os
paths = system.path

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

def move_file(full_path, destination, dry_run):
    if dry_run:
        print("Would move:", full_path, "->", destination)
    else:
        system.rename(full_path, destination)
        print("Moved:", full_path, "->", destination)

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
    organize_folder("~/Downloads", dry_run=True)