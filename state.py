"""App State - what the app remembers while running"""

import os

class AppState:
    def __init__(self):
        self.selected_folder_name = "Downloads"
        self.selected_folder_path = os.path.expanduser("~/Downloads")
        self.current_view_folder_path = os.path.expanduser("~/Downloads")
        self.current_preview = {}
