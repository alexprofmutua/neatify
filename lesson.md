---
title: Neatify Project Notes
author: Alex M
date: 2026-08-30
---

# Neatify Project Notes

**Name:** Alex Prof  
**Project:** Neatify  
**Topic:** Python, File Systems, GUI Programming, and Software Packaging  
**Date:** 2026-08-30

---

## How To Use These Notes

These notes are meant to work like a learner's guide.

If someone wanted to build Neatify from scratch, they should not start with the full GUI. They should build the project layer by layer:

```text
simple script
-> safer script
-> helper functions
-> categories
-> history
-> undo
-> search
-> GUI
-> settings
-> packaging
```

Each step below explains:

- What we are building
- Why we are building it
- What computer science idea it teaches
- What Python idea it teaches

---

## Step 1: Build The Simplest Organizer

The first version should only organize one folder.

At this stage, the program does not need a GUI, settings, themes, undo, or search.

The goal is only:

```text
Look inside Downloads and move files into folders based on their extensions.
```

Example:

```text
report.pdf -> pdf/report.pdf
photo.png  -> png/photo.png
song.mp3   -> mp3/song.mp3
```

### Algorithm

1. Find the Downloads folder.
2. List everything inside it.
3. Skip hidden files.
4. Build the full path for each item.
5. Check if the item is a file.
6. Find the file extension.
7. Create a folder for that extension.
8. Move the file into that folder.

### CS Idea

This is an **algorithm**.

An algorithm is a step-by-step method for solving a problem.

### Python Tools

```python
os.listdir(folder)
os.path.join(folder, file)
os.path.isfile(path)
os.makedirs(folder, exist_ok=True)
os.rename(old_path, new_path)
```

---

## Step 2: Add Safe Mode With `dry_run`

Moving files immediately can be dangerous.

So we add:

```python
dry_run = True
```

When `dry_run` is `True`, the program only prints what it would move.

When `dry_run` is `False`, the program actually moves the file.

### CS Idea

This is a **control flag**.

A control flag is a variable that changes the behavior of a program.

```text
dry_run = True  -> preview only
dry_run = False -> real action
```

This teaches safe testing.

---

## Step 3: Create Helper Functions

At first, it is normal to write everything in one function.

But once the code grows, we split it into helper functions.

Example:

```python
def get_extension(file_name):
    ...

def move_file(full_path, destination, dry_run):
    ...
```

### CS Idea

This is **decomposition**.

Decomposition means breaking one big problem into smaller problems.

Instead of one giant function doing everything, we create smaller functions with clear jobs.

This makes the code easier to:

- Read
- Debug
- Test
- Reuse
- Explain in interviews

---

## Step 4: Organize By Category

Extension folders work, but they are not very user-friendly.

This:

```text
pdf/
docx/
png/
jpg/
mp4/
```

is less useful than:

```text
Documents/
Images/
Videos/
Code/
Archives/
```

So we use a dictionary:

```python
extension_categories = {
    "pdf": "Documents",
    "docx": "Documents",
    "png": "Images",
    "jpg": "Images",
    "mp4": "Videos",
}
```

### CS Idea

This uses a **dictionary**, which stores key-value pairs.

| Key | Value |
|-----|-------|
| pdf | Documents |
| png | Images |
| mp4 | Videos |

The program can now ask:

```python
category = extension_categories.get(extension, "Other")
```

Meaning:

"Get the category for this extension. If it does not exist, use `Other`."

---

## Step 5: Handle Duplicate Names

Problem:

```text
Documents/report.pdf already exists
```

If another `report.pdf` is moved there, we should not overwrite the old file.

So Neatify creates a unique name:

```text
report_1.pdf
report_2.pdf
report_3.pdf
```

### Algorithm

1. Check if the destination exists.
2. If it does not exist, use it.
3. If it exists, try `_1`.
4. If `_1` exists, try `_2`.
5. Keep going until a free name is found.

### CS Idea

This uses a **while loop**.

A while loop is useful when we do not know exactly how many times we need to repeat something.

---

## Step 6: Generalize From Downloads To Any Folder

The first version only works for Downloads.

Then we change:

```python
def organize_downloads():
```

to:

```python
def organize_folder(folder_path):
```

Now the same function can organize any folder.

### CS Idea

This is **generalization**.

Generalization means changing code from one specific case to many possible cases.

Specific:

```text
Only Downloads.
```

General:

```text
Any folder path.
```

---

## Step 7: Add Common Folders And External Drives

Users should not need to type every path manually.

So Neatify finds common folders:

- Downloads
- Desktop
- Documents
- Pictures
- Music
- Movies

On macOS, it can also look for external drives in:

```text
/Volumes
```

### CS Idea

This is **environment-aware programming**.

Programs often need to behave differently depending on the operating system.

Examples:

- macOS uses `Movies`
- Windows commonly uses `Videos`
- External drives appear differently across operating systems

---

## Step 8: Add Preview Before Move

Before moving files, the app should show what will happen.

Example:

```text
Documents
report.pdf, notes.docx, syllabus.pdf + 14 more

Images
photo.jpg, screenshot.png + 6 more
```

The user can then choose:

```text
Proceed
Cancel
```

### CS Idea

This is **separating planning from execution**.

Planning:

```text
What would happen?
```

Execution:

```text
Actually do it.
```

This is important when the program changes user files.

---

## Step 9: Add History

After files move, the app writes down what happened.

History stores:

- Time
- Move batch ID
- Action
- Old path
- New path

Example:

```text
2026-08-30 18:45:12 | move_20260830184512000123 | Moved | old/path/report.pdf -> new/path/report.pdf
```

### CS Idea

This is **persistence**.

Persistence means saving data so it still exists after the app closes.

---

## Step 10: Add Undo

Undo works because history remembers both paths.

If the move was:

```text
Downloads/report.pdf -> Downloads/Documents/report.pdf
```

Undo does:

```text
Downloads/Documents/report.pdf -> Downloads/report.pdf
```

### Algorithm

1. Read history.
2. Find the selected batch.
3. Check if it was already undone.
4. Check if the moved file still exists.
5. Check if the original path is free.
6. Move the file back.
7. Write an `UNDONE` record.

### CS Idea

This is **reversibility**.

A reversible operation stores enough information to go backward.

---

## Step 11: Add Search

Users need to find files and folders.

The basic search algorithm is:

1. Choose a starting folder.
2. Walk through the folder.
3. Look at every folder name and file name.
4. Compare each name with the search text.
5. Store matching results.
6. Show the results.

Python gives us:

```python
for current_folder, folders, files in os.walk(search_path):
```

### CS Idea

This is **tree traversal**.

A file system is shaped like a tree:

```text
Downloads
  Documents
    report.pdf
  Images
    photo.png
```

Searching through folders is like walking through a tree.

---

## Step 12: Add Search Filters

Search becomes better when users can narrow results.

Examples:

- All
- Files
- Folders
- Documents
- Images
- Videos
- `pdf`
- `png`

### CS Idea

This is **filtering**.

Filtering means keeping only the items that match a condition.

In code, `continue` helps skip items:

```python
if clean_search_type != extension:
    continue
```

Meaning:

"This item does not match, so go to the next item."

---

## Step 13: Build The GUI

The GUI turns Neatify from a script into an app.

Neatify uses PySide6.

Important GUI objects:

| Object | Meaning |
|--------|---------|
| `QApplication` | The whole app manager |
| `QMainWindow` | The main window |
| `QWidget` | A visual container |
| `QLabel` | Text |
| `QPushButton` | Button |
| `QLineEdit` | Text input |
| `QTreeWidget` | List/tree display |
| `QVBoxLayout` | Top-to-bottom layout |
| `QHBoxLayout` | Left-to-right layout |
| `QGridLayout` | Row and column layout |

The app layout became:

```text
command buttons
ask input
left folders | center browser | right output
```

### CS Idea

This is **event-driven programming**.

The app waits for events:

- Button click
- Text typed
- Enter pressed
- Folder selected
- File double-clicked

Example:

```python
self.arrange_button.clicked.connect(self.start_arrange_command)
```

Meaning:

"When the Arrange button is clicked, call this function."

---

## Step 14: Use Classes And State

As the GUI grows, a class helps organize the app.

```python
class NeatifyWindow(QMainWindow):
```

This means:

`NeatifyWindow` is our custom window.

Inside a class, `self` means:

```text
this object
```

Example:

```python
self.state = AppState()
```

Meaning:

"This window has an app state object."

### CS Idea

This is **object-oriented programming**.

A class groups related data and behavior together.

State means what the app remembers, such as:

- Selected folder
- Current folder being viewed
- Folder being arranged
- Current preview
- Current theme

---

## Step 15: Split The Code Into Files

One file is okay at the beginning.

A larger app should be split into modules.

Neatify uses:

| File | Job |
|------|-----|
| `gui.py` | Starts the app |
| `window.py` | Builds and controls the GUI |
| `style.py` | Stores the visual style |
| `components.py` | Reusable UI helpers |
| `state.py` | Runtime app state |
| `neatify.py` | Core file actions, history, and undo |
| `rules.py` | Custom rules and search |
| `app_settings.py` | Saves user preferences |
| `app_paths.py` | Finds assets and user-data paths |

### CS Idea

This is **separation of concerns**.

Each file has a clear responsibility.

This makes the project easier to:

- Maintain
- Debug
- Test
- Explain
- Extend

---

## Step 16: Add Settings And Themes

Settings let the user change behavior without editing code.

Neatify settings include:

- Theme
- Search type
- Include subfolders

Settings are saved as JSON:

```json
{
    "theme": "midnight",
    "search_type": "All",
    "include_subfolders": true
}
```

### CS Idea

This is **configuration**.

Configuration stores user choices outside the source code.

---

## Step 17: Use Proper App Paths

When running as a script, saving files beside the code may work.

But installed apps should save user data in a proper app-data folder.

On macOS, that is usually:

```text
~/Library/Application Support/Neatify
```

Neatify uses `app_paths.py` for:

- Logo paths
- Packaged app paths
- Settings paths
- Rules paths
- History paths

### CS Idea

This is **defensive programming**.

Good software works in different environments instead of assuming everything runs from the project folder.

---

## Step 18: Package The App

Development version:

```text
python gui.py
```

User version:

```text
Neatify.app
Neatify-macOS.dmg
```

Packaging uses:

- PyInstaller for the `.app`
- `hdiutil` for the `.dmg`

### CS Idea

This is **deployment**.

Deployment means preparing software so other people can install and use it.

---

## Step 19: Think Like A Software Engineer

A software engineer does not only ask:

```text
Does the code run?
```

They also ask:

- Is it safe?
- Is it understandable?
- Can a user recover from mistakes?
- Can another developer read it?
- Can it be packaged?
- Can it be tested?
- Can it be improved later?

This is the difference between a script and a product.

---

## Build Order Summary

The full build order for Neatify is:

1. Basic Downloads organizer
2. Safe `dry_run` mode
3. Helper functions
4. Extension categories
5. Duplicate-safe naming
6. Organize any folder
7. Common folders and external drives
8. Arrange preview
9. History
10. Undo
11. Custom rules
12. Search
13. Search filters
14. PySide6 GUI
15. Three-panel layout
16. Folder and file browser
17. Settings page
18. Themes
19. History page
20. Undo page
21. Code split into modules
22. App-data paths
23. Temporary logo
24. macOS `.app`
25. macOS `.dmg`

---

## Project Overview

**Neatify** is a desktop file organizer built with Python and PySide6.

The goal is to help users clean folders like Downloads, Desktop, Documents, Pictures, Music, Movies, and external drives by previewing where files will go before actually moving them.

The project began as a simple command-line program and grew into a full GUI app with:

- Folder browsing
- File previews
- File organization
- Custom rules
- Search filters
- History
- Undo
- Themes
- macOS packaging

This project connects directly to computer science because it uses algorithms, data structures, state, file systems, event-driven programming, and software design.

---

## Key Idea: File Organization

File organization means taking files from one folder and moving them into better folders based on some rule.

Example:

```text
report.pdf       -> Documents/report.pdf
photo.png        -> Images/photo.png
lecture.mp4      -> Videos/lecture.mp4
main.py          -> Code/main.py
```

The computer science idea here is **classification**.

Classification means:

1. Look at an item.
2. Extract useful information from it.
3. Use rules to decide which group it belongs to.
4. Place it in that group.

In Neatify, the item is a file, and the useful information can be:

- The file extension, such as `pdf`, `png`, or `mp4`
- A keyword in the name, such as `econ`, `cs`, or `resume`

---

## Core Algorithm

An **algorithm** is a step-by-step process for solving a problem.

Neatify's main organize algorithm is:

1. Choose a folder.
2. Check if the folder exists.
3. Look at each item inside the folder.
4. Skip folders and hidden files.
5. For each file, find its category.
6. Create the destination folder if needed.
7. Check if a file with the same name already exists.
8. Create a unique name if needed.
9. Move the file.
10. Write the move into history.

In code, this kind of thinking appears inside `organize_folder()`.

```python
for file in system.listdir(folder):
    full_path = paths.join(folder, file)

    if paths.isfile(full_path):
        category = get_category_for_file(file)
```

The loop means: "visit every item in the folder one by one."

The `if` statement means: "only organize it if it is a file."

---

## Data Structures Used

A **data structure** is a way of organizing information in memory.

### 1. Lists

Lists are used when order matters or when we need to store multiple values.

Example:

```python
folders_to_organize = [
    "~/Downloads",
    "~/Desktop",
    "~/Documents",
]
```

This is useful because the program can loop through every folder.

### 2. Dictionaries

Dictionaries store key-value pairs.

Example:

```python
extension_categories = {
    "pdf": "Documents",
    "png": "Images",
    "mp4": "Videos",
}
```

The key is the extension.

The value is the folder category.

This is like a table:

| Extension | Category |
|----------|----------|
| pdf | Documents |
| png | Images |
| mp4 | Videos |

Dictionaries are powerful because lookup is fast. Instead of checking every possible extension one by one, Python can quickly ask:

```python
category = extension_categories.get(extension, "Other")
```

This means:

"Find the category for this extension. If it does not exist, use `Other`."

---

## Helper Functions

A **helper function** is a smaller function that helps a bigger function do its job.

Instead of putting everything inside one huge function, Neatify uses helpers.

Example:

```python
def get_extension(file_name):
    if "." in file_name:
        parts = file_name.split(".")
        extension = parts[-1].lower()
    else:
        extension = "other"

    return extension
```

This function only has one job: find the extension of a file.

This makes the program easier to:

- Read
- Test
- Fix
- Reuse

This is called **decomposition** in computer science.

Decomposition means breaking a large problem into smaller problems.

---

## Duplicate Handling

If a file already exists in the destination folder, Neatify should not overwrite it.

Example:

```text
Documents/report.pdf already exists
```

So Neatify creates a new name:

```text
Documents/report_1.pdf
Documents/report_2.pdf
Documents/report_3.pdf
```

The algorithm is:

1. Check if the destination exists.
2. If it does not exist, use it.
3. If it exists, add `_1`.
4. If that exists, try `_2`.
5. Keep going until a free name is found.

This uses a **while loop** because we do not know how many tries we need before the program starts.

---

## History

History records what happened after files are moved.

Example:

```text
2026-08-30 18:45:12 | move_20260830184512000123 | Moved | old/path/report.pdf -> new/path/report.pdf
```

This line stores:

- When the move happened
- Which batch the move belongs to
- What action happened
- Where the file came from
- Where the file went

This is important because undo needs memory.

Without history, the program would not know how to reverse the move.

---

## Undo

Undo means reversing a previous operation.

If Neatify moved this:

```text
Downloads/report.pdf -> Downloads/Documents/report.pdf
```

Undo moves it back:

```text
Downloads/Documents/report.pdf -> Downloads/report.pdf
```

The algorithm for undo is:

1. Read the history file.
2. Find the selected move batch.
3. Check if it was already undone.
4. Check that the moved file still exists.
5. Check that the original location is free.
6. Move the file back.
7. Write an `UNDONE` record to history.

This is related to a common CS idea called **reversibility**.

A reversible operation is one where we store enough information to go backward.

---

## Search

Search means looking through folders to find matching files or folders.

Neatify can search by:

- File name
- Folder name
- Extension
- Category

The key Python tool is:

```python
for current_folder, folders, files in os.walk(search_path):
```

This means Python walks through a folder tree.

Each step gives:

- `current_folder`: the folder we are currently inside
- `folders`: the folders inside the current folder
- `files`: the files inside the current folder

This is similar to **tree traversal** in CS.

A file system is shaped like a tree:

```text
Downloads
  Documents
    report.pdf
  Images
    photo.png
```

Searching subfolders is like walking through the branches of a tree.

---

## GUI Programming

GUI means **Graphical User Interface**.

Instead of typing commands in the terminal, users click buttons, type in boxes, and see visual results.

Neatify uses PySide6, which is a Python library for building desktop apps.

### Important GUI Objects

| Object | Meaning |
|--------|---------|
| `QApplication` | The whole app manager |
| `QMainWindow` | The main app window |
| `QWidget` | A visual container |
| `QLabel` | Text on the screen |
| `QPushButton` | A clickable button |
| `QLineEdit` | A text input box |
| `QTreeWidget` | A list/tree display |
| `QVBoxLayout` | Arranges items top to bottom |
| `QHBoxLayout` | Arranges items left to right |
| `QGridLayout` | Arranges items in rows and columns |

---

## Event-Driven Programming

In terminal programs, the code often runs from top to bottom.

In GUI programs, the app waits for events.

An **event** is something the user does:

- Clicks a button
- Presses Enter
- Selects a folder
- Double-clicks a file

Example:

```python
self.arrange_button.clicked.connect(self.start_arrange_command)
```

This means:

"When the Arrange button is clicked, run `start_arrange_command()`."

This is called **event-driven programming**.

The app does not organize files immediately. It waits until the user gives an event.

---

## Classes and State

A **class** is a blueprint for creating objects.

In Neatify, the main class is:

```python
class NeatifyWindow(QMainWindow):
```

This means:

`NeatifyWindow` is our custom window, and it inherits features from `QMainWindow`.

### What `self` Means

Inside a class, `self` means "this object."

Example:

```python
self.state = AppState()
```

This means:

"This Neatify window has its own state."

State is information the app remembers while running.

Examples:

- Which folder is selected
- Which folder is being viewed
- Which folder is being previewed for arrange
- Which theme is selected

---

## Separation of Concerns

Separation of concerns means each file has a clear job.

Neatify is split into multiple files:

| File | Job |
|------|-----|
| `gui.py` | Starts the app |
| `window.py` | Builds and controls the main window |
| `style.py` | Stores the app styling |
| `state.py` | Stores app state |
| `components.py` | Creates reusable UI pieces |
| `neatify.py` | Handles core file actions |
| `rules.py` | Handles custom rules and search |
| `app_settings.py` | Saves and loads preferences |
| `app_paths.py` | Handles project paths and user-data paths |

This makes the project more professional because each part is easier to understand and improve.

---

## Packaging

Packaging means turning code into an app that users can run without opening the terminal.

For macOS, Neatify uses:

- PyInstaller to create `Neatify.app`
- `hdiutil` to create `Neatify-macOS.dmg`

The `.dmg` is like a container that users download and open.

The `.app` is the actual application.

This matters because normal users should not need to:

- Install Python
- Create a virtual environment
- Run `python gui.py`
- Install packages manually

---

## Applications of These Concepts

The same ideas used in Neatify appear in many real software systems:

- File managers use tree traversal.
- Search engines use searching and filtering.
- Operating systems use paths and file metadata.
- Apps use event-driven programming.
- Professional software uses settings files and app-data folders.
- Undo systems require history and reversible operations.
- Installers require packaging and distribution.

---

## Current Project Status

Neatify currently has:

- A working PySide6 GUI
- Folder browsing
- File listing
- Arrange preview
- Proceed and cancel actions
- Custom extension rules
- Custom keyword rules
- Search filters
- History page
- Batch undo
- Themes
- Temporary logo
- macOS `.app` build
- macOS `.dmg` installer

---

## Remaining Ideas

- Add stronger automated tests.
- Improve public installer polish.
- Add code signing and notarization for macOS.
- Add Windows and Linux packaging.
- Add optional anonymous install or launch analytics.
- Add AI commands later after user feedback.

---

## Big Lesson

Neatify shows that software grows in layers.

First, we solved the basic algorithm:

```text
file -> category -> destination folder
```

Then we added safety:

```text
preview -> move -> history -> undo
```

Then we added usability:

```text
GUI -> buttons -> search -> settings -> themes
```

Then we added distribution:

```text
source code -> app bundle -> DMG installer
```

This is how real software engineering works: start small, make it correct, make it usable, then make it shippable.
