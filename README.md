# 📂 Neatify: File Organizer
A lightweight Python automation tool that cleans up your cluttered Downloads folder by automatically sorting files into categorized subfolders (Images, Documents, Videos, Archives, Executables) based on their extensions (e.g, .zip, .gif, .pdf, etc.).

## 🚀 Features
- Smart Sorting: Uses dictionaries to map file extensions to specific folders.
- Cross-Platform: Built using pathlib to work seamlessly on macOS, Windows, and Linux.
- Safe Execution: Includes a "Dry Run" mode to preview changes before moving files.

Freshman Friendly: Written as a first independent project after completing CSCI 134 (Intro to CS) at Williams College.

## 🛠️ Tech Stack
- Language: Python
- Libraries: shutil (file operations), pathlib (path management)

## 📋 How It Works
The script scans your Downloads directory, identifies the suffix (extension) of each file, and moves it to a corresponding folder. If the folder doesn't exist yet, Neatify creates it for you.

## ⚙️ Installation & Usage
Clone the repo:
```
git clone git@github.com:amm22-lab/neatify.git
cd neatify
python3 neatify.py
```
<img width="616" height="224" alt="Screenshot 2025-12-21 at 9 45 08 AM" src="https://github.com/user-attachments/assets/86506d33-f680-417d-85ab-75bc6cb7a24a" />

Developed by Alex M
