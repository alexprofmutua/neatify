"""Builds the window"""

import os   # Imports Python's file and folder tools
from style import APP_STYLE
from state import AppState
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QHeaderView, QLineEdit, QMainWindow, QPushButton, QScrollArea, QStyle, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from components import create_folder_button
from neatify import find_item, get_common_folders, get_extension, open_item, organize_folder, undo_last_move, extension_categories


class NeatifyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.folder_buttons = []
        self.center_folder_buttons = []
        self.setWindowTitle("Neatify")
        self.setStyleSheet(APP_STYLE)
        self.resize(920, 560)
        self.build_interface()

    def build_interface(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        self.page_layout = QVBoxLayout()
        central_widget.setLayout(self.page_layout)

        self.commands_layout = QHBoxLayout()
        self.ask_layout = QHBoxLayout()
        self.main_layout = QHBoxLayout()

        self.setup_layout_spacing()

        self.page_layout.addLayout(self.commands_layout)
        self.page_layout.addLayout(self.ask_layout)
        self.page_layout.addLayout(self.main_layout)

        self.create_command_bar()
        self.create_ask_bar()
        self.create_panels()

    def setup_layout_spacing(self):
        self.page_layout.setContentsMargins(18, 18, 18, 18)
        self.page_layout.setSpacing(14)

        self.commands_layout.setSpacing(10)
        self.ask_layout.setSpacing(10)
        self.main_layout.setSpacing(0)

    def create_command_bar(self):
        self.arrange_button = QPushButton("Arrange")
        self.find_button = QPushButton("Find")
        self.open_button = QPushButton("Open")
        self.undo_button = QPushButton("Undo")
        self.history_button = QPushButton("History")

        self.arrange_button.setObjectName("primaryCommand")
        self.find_button.setObjectName("commandButton")
        self.open_button.setObjectName("commandButton")
        self.undo_button.setObjectName("commandButton")
        self.history_button.setObjectName("commandButton")

        self.commands_layout.addWidget(self.arrange_button)
        self.commands_layout.addWidget(self.find_button)
        self.commands_layout.addWidget(self.open_button)
        self.commands_layout.addWidget(self.undo_button)
        self.commands_layout.addWidget(self.history_button)
        self.commands_layout.addStretch()

        self.arrange_button.clicked.connect(lambda: self.start_command("arrange "))
        self.find_button.clicked.connect(lambda: self.start_command("find "))
        self.open_button.clicked.connect(lambda: self.start_command("open "))
        self.undo_button.clicked.connect(lambda: self.start_command("undo last move"))
        self.history_button.clicked.connect(lambda: self.start_command("show history"))

    def create_ask_bar(self):
        self.ask_input = QLineEdit()
        self.ask_input.setPlaceholderText("Ask Neatify: show me all PDFs in this folder...")
        self.ask_input.returnPressed.connect(self.process_ask_command)
        self.ask_layout.addWidget(self.ask_input)

    def start_command(self, command_text):
        self.ask_input.setText(command_text)
        self.ask_input.setFocus()

        if command_text == "arrange ":
            self.show_output("Arrange", ["Press Enter to preview the selected folder."])
        elif command_text == "find ":
            self.show_output("Find", ["Type the file or folder name, then press Enter."])
        elif command_text == "open ":
            self.show_output("Open", ["Type the file or folder path, then press Enter."])
        elif command_text == "undo last move":
            self.undo_last_gui_move()
        elif command_text == "show history":
            self.show_history()

    def create_panels(self):
        self.left_panel = QWidget()
        self.center_panel = QWidget()
        self.right_panel = QWidget()

        self.left_panel.setObjectName("leftPanel")
        self.center_panel.setObjectName("centerPanel")
        self.right_panel.setObjectName("rightPanel")

        self.left_panel.setMinimumWidth(190)
        self.right_panel.setMinimumWidth(260)

        self.left_layout = QVBoxLayout()
        self.center_panel_layout = QVBoxLayout()
        self.center_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.left_layout.setContentsMargins(16, 20, 16, 20)
        self.center_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setContentsMargins(24, 24, 24, 24)
        self.right_layout.setContentsMargins(18, 24, 18, 24)

        self.left_layout.setSpacing(8)
        self.center_panel_layout.setSpacing(0)
        self.center_layout.setSpacing(14)
        self.right_layout.setSpacing(14)

        self.left_panel.setLayout(self.left_layout)
        self.center_panel.setLayout(self.center_panel_layout)
        self.right_panel.setLayout(self.right_layout)

        self.center_content = QWidget()
        self.center_content.setObjectName("centerContent")
        self.center_content.setLayout(self.center_layout)

        self.center_scroll_area = QScrollArea()
        self.center_scroll_area.setObjectName("centerScrollArea")
        self.center_scroll_area.setWidgetResizable(True)
        self.center_scroll_area.setWidget(self.center_content)

        self.center_panel_layout.addWidget(self.center_scroll_area)

        self.main_layout.addWidget(self.left_panel, 1)
        self.main_layout.addWidget(self.center_panel, 2)
        self.main_layout.addWidget(self.right_panel, 1)

        self.create_folder_panel()
        self.create_center_panel()
        self.create_preview_panel()

    def create_folder_panel(self):
        folders_title = QLabel("Folders")
        folders_title.setObjectName("foldersTitle")

        self.left_layout.addWidget(folders_title)

        folder_paths = get_common_folders()
        drive_paths = self.get_external_drive_paths()

        if len(folder_paths) == 0:
            folder_paths.append(os.path.expanduser("~"))

        self.state.selected_folder_path = folder_paths[0]
        self.state.selected_folder_name = self.get_folder_display_name(folder_paths[0])
        self.state.current_view_folder_path = self.state.selected_folder_path

        for index, folder_path in enumerate(folder_paths):
            self.add_left_folder_button(folder_path, active=index == 0)

        if len(drive_paths) > 0:
            external_title = QLabel("External Drives")
            external_title.setObjectName("foldersTitle")
            self.left_layout.addWidget(external_title)

            for drive_path in drive_paths:
                self.add_left_folder_button(drive_path)

        self.left_layout.addStretch()

    def add_left_folder_button(self, folder_path, active=False):
        folder_name = self.get_folder_display_name(folder_path)
        folder_button = create_folder_button(folder_name, active=active)
        folder_button.setIcon(self.get_folder_icon())
        folder_button.setIconSize(QSize(20, 20))
        folder_button.clicked.connect(lambda checked=False, name=folder_name, path=folder_path, button=folder_button: self.select_folder(name, path, button))

        self.folder_buttons.append(folder_button)
        self.left_layout.addWidget(folder_button)

    def create_center_panel(self):
        self.folder_name_label = QLabel(self.state.selected_folder_name)
        self.breadcrumb_label = QLabel(self.get_breadcrumb_text())
        self.folder_summary_label = QLabel(self.get_folder_status(self.state.selected_folder_path))

        self.folder_name_label.setObjectName("folderName")
        self.breadcrumb_label.setObjectName("breadcrumbLabel")
        self.folder_summary_label.setObjectName("folderSummary")
        self.folder_contents_list = QTreeWidget()
        self.folder_contents_list.setObjectName("folderContentsList")
        self.folder_contents_list.setColumnCount(2)
        self.folder_contents_list.setHeaderLabels(["Name", "Size"])
        self.folder_contents_list.setRootIsDecorated(False)
        self.folder_contents_list.setMinimumHeight(140)
        self.folder_contents_list.setMaximumHeight(200)
        self.folder_contents_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.folder_contents_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.folder_contents_list.itemDoubleClicked.connect(self.open_output_item)

        self.folders_title_label = QLabel("Folders")
        self.folders_title_label.setObjectName("sectionTitle")

        self.files_title_label = QLabel("Files")
        self.files_title_label.setObjectName("sectionTitle")

        self.folder_cards_layout = QGridLayout()
        self.folder_cards_layout.setSpacing(12)

        self.center_layout.addWidget(self.folder_name_label)
        self.center_layout.addWidget(self.breadcrumb_label)
        self.center_layout.addWidget(self.folder_summary_label)
        self.center_layout.addWidget(self.folders_title_label)
        self.center_layout.addLayout(self.folder_cards_layout)
        self.center_layout.addSpacing(24)
        self.center_layout.addWidget(self.files_title_label)
        self.center_layout.addWidget(self.folder_contents_list)
        self.center_layout.addStretch()

        self.update_folder_cards()
        self.update_folder_contents_list(self.state.selected_folder_path)

    def create_preview_panel(self):
        self.output_title = QLabel("Output")

        self.output_list = QTreeWidget()
        self.output_list.setObjectName("outputList")
        self.output_list.setColumnCount(2)
        self.output_list.setHeaderLabels(["Item", "Details"])
        self.output_list.setRootIsDecorated(False)
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.output_list.itemDoubleClicked.connect(self.open_output_item)

        self.proceed_button = QPushButton("Proceed")
        self.proceed_button.setObjectName("proceedButton")
        self.proceed_button.setVisible(False)
        self.proceed_button.clicked.connect(self.organize_selected_folder)

        self.open_selected_button = QPushButton("Open Selected")
        self.open_selected_button.setObjectName("secondaryActionButton")
        self.open_selected_button.clicked.connect(self.open_selected_item)

        self.output_title.setObjectName("previewTitle")

        self.right_layout.addWidget(self.output_title)
        self.right_layout.addWidget(self.output_list, 1)
        self.right_layout.addWidget(self.open_selected_button)
        self.right_layout.addWidget(self.proceed_button)

        self.show_output("Output", ["Choose a command or type in Ask Neatify."])

    def select_folder(self, folder_name, folder_path, selected_button):
        self.state.selected_folder_name = folder_name
        self.state.selected_folder_path = os.path.expanduser(folder_path)
        self.state.current_view_folder_path = self.state.selected_folder_path

        self.folder_name_label.setText(self.state.selected_folder_name)
        self.breadcrumb_label.setText(self.get_breadcrumb_text())
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_cards()
        self.update_folder_contents_list(self.state.selected_folder_path)

        for button in self.folder_buttons:
            button.setObjectName("folderItem")
            self.refresh_style(button)

        selected_button.setObjectName("activeFolder")
        self.refresh_style(selected_button)

    def get_folder_status(self, folder_path):
        if not os.path.exists(folder_path):
            return "Folder not found"

        if not os.path.isdir(folder_path):
            return "Path is not a folder"

        folder_count = 0
        file_count = 0

        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)

            if os.path.isdir(full_path):
                folder_count = folder_count + 1
            elif os.path.isfile(full_path):
                file_count = file_count + 1

        return str(folder_count) + " folders - " + str(file_count) + " files"

    def get_category_counts(self, folder_path):
        counts = {
            "Documents": 0,
            "Images": 0,
            "Videos": 0,
            "Duplicates renamed": 0,
        }

        if not os.path.exists(folder_path):
            return counts

        if not os.path.isdir(folder_path):
            return counts

        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)

            if os.path.isfile(full_path):
                extension = get_extension(item)
                category = extension_categories.get(extension, "Other")

                if category in counts:
                    counts[category] = counts[category] + 1

        return counts

    def get_preview_groups(self, folder_path):
        preview_groups = {
            "Documents": [],
            "Images": [],
            "Videos": [],
        }

        if not os.path.exists(folder_path):
            return preview_groups

        if not os.path.isdir(folder_path):
            return preview_groups

        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)

            if os.path.isfile(full_path):
                extension = get_extension(item)
                category = extension_categories.get(extension, "Other")

                if category in preview_groups:
                    preview_groups[category].append(item)

        return preview_groups

    def format_preview_text(self, category_name, files):
        if len(files) == 0:
            return category_name + "\nNo files found"

        first_files = files[:2]
        preview_text = category_name + "\n" + ", ".join(first_files)

        remaining_count = len(files) - 2

        if remaining_count > 0:
            preview_text = preview_text + " + " + str(remaining_count) + " more"

        return preview_text

    def update_preview_panel(self):
        preview_groups = self.get_preview_groups(self.state.selected_folder_path)

        self.output_title.setText("Arrange Preview")
        self.output_list.clear()
        self.output_list.setColumnCount(2)
        self.output_list.setHeaderLabels(["Move To", "Files"])
        self.output_list.header().show()
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proceed_button.setVisible(True)

        for category_name in preview_groups:
            files = preview_groups[category_name]
            files_text = self.format_short_file_list(files)
            list_item = QTreeWidgetItem([category_name, files_text])
            list_item.setIcon(0, self.get_folder_icon())
            self.output_list.addTopLevelItem(list_item)

    def show_arrange_preview(self):
        self.update_preview_panel()

    def show_output(self, title, lines, show_proceed=False):
        self.output_title.setText(title)
        self.output_list.clear()
        self.output_list.setColumnCount(1)
        self.output_list.setHeaderLabels(["Message"])
        self.output_list.header().hide()
        self.proceed_button.setVisible(show_proceed)

        for line in lines:
            list_item = QTreeWidgetItem([line.strip()])
            self.output_list.addTopLevelItem(list_item)

    def process_ask_command(self):
        command = self.ask_input.text().strip()
        lowered_command = command.lower()

        if lowered_command == "arrange":
            self.show_arrange_preview()
            return

        if lowered_command.startswith("find "):
            item_name = command[5:].strip()
            self.show_find_results(item_name)
            return

        if lowered_command.startswith("open "):
            item_name = command[5:].strip()
            self.open_from_command(item_name)
            return

        if lowered_command == "undo last move":
            self.undo_last_gui_move()
            return

        if lowered_command == "show history":
            self.show_history()
            return

        self.show_output("Output", ["Command not understood yet."])

    def show_find_results(self, item_name):
        if item_name == "":
            self.show_output("Find", ["Type a file or folder name after find."])
            return

        results = find_item(item_name, self.state.selected_folder_path)

        if len(results) == 0:
            self.show_output("Find results", ["No matching item found."])
            return

        self.show_path_results("Find results", results)

    def open_from_command(self, item_name):
        if item_name == "":
            self.show_output("Open", ["Type a file or folder name after open."])
            return

        expanded_path = os.path.expanduser(item_name)

        if os.path.exists(expanded_path):
            open_item(expanded_path)
            self.show_output("Open", ["Opened: " + expanded_path])
            return

        results = find_item(item_name, self.state.selected_folder_path)

        if len(results) == 0:
            self.show_output("Open", ["No matching item found."])
            return

        if len(results) == 1:
            open_item(results[0])
            self.show_output("Open", ["Opened: " + results[0]])
            return

        self.show_path_results("Choose one to open", results)

    def open_output_item(self, item, column=0):
        item_path = item.data(0, Qt.UserRole)

        if item_path is None:
            return

        open_item(item_path)
        self.show_output("Open", ["Opened: " + item_path])

    def open_selected_item(self):
        item = self.get_selected_path_item()

        if item is None:
            self.show_output("Open Selected", ["Select a file or search result first."])
            return

        item_path = item.data(0, Qt.UserRole)
        open_item(item_path)
        self.show_output("Open", ["Opened: " + item_path])

    def get_selected_path_item(self):
        output_items = self.output_list.selectedItems()

        if len(output_items) > 0:
            item_path = output_items[0].data(0, Qt.UserRole)

            if item_path is not None:
                return output_items[0]

        file_items = self.folder_contents_list.selectedItems()

        if len(file_items) > 0:
            item_path = file_items[0].data(0, Qt.UserRole)

            if item_path is not None:
                return file_items[0]

        return None

    def show_path_results(self, title, paths):
        self.output_title.setText(title)
        self.output_list.clear()
        self.output_list.setColumnCount(2)
        self.output_list.setHeaderLabels(["Name", "Location"])
        self.output_list.header().show()
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proceed_button.setVisible(False)

        for item_path in paths:
            item_name = os.path.basename(item_path)
            parent_folder = os.path.dirname(item_path)
            list_item = QTreeWidgetItem([item_name, parent_folder])
            list_item.setIcon(0, self.get_path_icon(item_path))
            list_item.setData(0, Qt.UserRole, item_path)
            self.output_list.addTopLevelItem(list_item)

    def organize_selected_folder(self):
        organize_folder(self.state.selected_folder_path, dry_run=False)
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_cards()
        self.update_folder_contents_list(self.state.selected_folder_path)
        self.show_output("Done", ["Organized: " + self.state.selected_folder_path])

    def show_history(self):
        history_path = "neatify_history.txt"

        if not os.path.exists(history_path):
            self.show_output("History", ["No history found yet."])
            return

        with open(history_path, "r") as history_file:
            lines = history_file.readlines()

        if len(lines) == 0:
            self.show_output("History", ["No history found yet."])
            return

        self.output_title.setText("History")
        self.output_list.clear()
        self.output_list.setColumnCount(4)
        self.output_list.setHeaderLabels(["Time", "Action", "Item", "Destination"])
        self.output_list.header().show()
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.output_list.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.proceed_button.setVisible(False)

        for line in reversed(lines[-20:]):
            history_item = self.parse_history_line(line)

            if history_item is None:
                continue

            list_item = QTreeWidgetItem([
                history_item["time"],
                history_item["action"],
                history_item["item"],
                history_item["destination"],
            ])
            list_item.setIcon(2, self.get_path_icon(history_item["path_for_icon"]))
            self.output_list.addTopLevelItem(list_item)

    def undo_last_gui_move(self):
        result = undo_last_move()
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_cards()
        self.update_folder_contents_list(self.state.current_view_folder_path)
        self.show_output("Undo", [result])

    def parse_history_line(self, line):
        parts = line.strip().split(" | ")

        if len(parts) != 4:
            return None

        timestamp = parts[0]
        action = parts[2]
        paths_part = parts[3]

        if " -> " not in paths_part:
            return None

        old_path, new_path = paths_part.split(" -> ")

        return {
            "time": timestamp,
            "action": action,
            "item": os.path.basename(old_path),
            "destination": os.path.basename(os.path.dirname(new_path)),
            "path_for_icon": new_path,
        }

    def get_external_drive_paths(self):
        drive_paths = []
        volumes_folder = "/Volumes"

        if not os.path.exists(volumes_folder):
            return drive_paths

        if not os.path.isdir(volumes_folder):
            return drive_paths

        home_drive_path = os.path.realpath("/")

        for item in sorted(os.listdir(volumes_folder)):
            full_path = os.path.join(volumes_folder, item)

            if os.path.isdir(full_path) and os.path.realpath(full_path) != home_drive_path:
                drive_paths.append(full_path)

        return drive_paths

    def get_folder_display_name(self, folder_path):
        folder_name = os.path.basename(folder_path)

        if folder_name == "":
            return folder_path

        return folder_name

    def create_center_folder_card(self, folder_name, folder_path):
        button = QPushButton(folder_name)
        button.setObjectName("centerFolderCard")
        button.setIcon(self.get_folder_icon())
        button.setIconSize(QSize(26, 26))
        button.clicked.connect(lambda: self.select_center_folder(folder_path, button))

        return button

    def select_center_folder(self, folder_path, selected_button):
        self.state.current_view_folder_path = folder_path
        self.breadcrumb_label.setText(self.get_breadcrumb_text())
        self.update_folder_contents_list(folder_path)

        for button in self.center_folder_buttons:
            button.setObjectName("centerFolderCard")
            self.refresh_style(button)

        selected_button.setObjectName("activeCenterFolderCard")
        self.refresh_style(selected_button)

    def clear_folder_cards(self):
        while self.folder_cards_layout.count() > 0:
            layout_item = self.folder_cards_layout.takeAt(0)
            widget = layout_item.widget()

            if widget is not None:
                widget.deleteLater()

        self.center_folder_buttons = []

    def update_folder_cards(self):
        self.clear_folder_cards()

        folder_path = self.state.selected_folder_path

        if not os.path.exists(folder_path):
            return

        if not os.path.isdir(folder_path):
            return

        folder_names = []

        for item in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, item)

            if os.path.isdir(full_path):
                folder_names.append(item)

        if len(folder_names) == 0:
            no_folders_label = QLabel("No folders found")
            no_folders_label.setObjectName("emptyMessage")
            self.folder_cards_layout.addWidget(no_folders_label, 0, 0)
            return

        row = 0
        column = 0

        for folder_name in folder_names:
            full_path = os.path.join(folder_path, folder_name)
            folder_card = self.create_center_folder_card(folder_name, full_path)
            self.center_folder_buttons.append(folder_card)
            self.folder_cards_layout.addWidget(folder_card, row, column)

            column = column + 1

            if column == 2:
                column = 0
                row = row + 1

    def update_folder_contents_list(self, folder_path):
        self.folder_contents_list.clear()
        self.files_title_label.setText("Files")

        folder_name = os.path.basename(folder_path)

        if folder_name != "":
            self.files_title_label.setText("Files in " + folder_name)

        if not os.path.exists(folder_path):
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["Folder not found", ""]))
            return

        if not os.path.isdir(folder_path):
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["Path is not a folder", ""]))
            return

        for item in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, item)

            if os.path.isfile(full_path):
                list_item = QTreeWidgetItem([item, self.get_file_size_text(full_path)])
                list_item.setIcon(0, self.get_file_icon(item))
                list_item.setData(0, Qt.UserRole, full_path)
                self.folder_contents_list.addTopLevelItem(list_item)

        if self.folder_contents_list.topLevelItemCount() == 0:
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["No files found", ""]))

    def get_breadcrumb_text(self):
        selected_path = self.state.selected_folder_path
        current_path = self.state.current_view_folder_path

        if current_path == selected_path:
            return selected_path

        selected_name = self.state.selected_folder_name
        current_name = os.path.basename(current_path)

        return selected_name + " > " + current_name

    def get_folder_icon(self):
        return self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)

    def get_path_icon(self, item_path):
        if os.path.isdir(item_path):
            return self.get_folder_icon()

        return self.get_file_icon(os.path.basename(item_path))

    def get_file_icon(self, file_name):
        extension = get_extension(file_name)
        category = extension_categories.get(extension, "Other")

        if category == "Images":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView)

        if category == "Videos":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)

        if category == "Audio":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)

        return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def get_file_size_text(self, file_path):
        size = os.path.getsize(file_path)

        if size < 1024:
            return str(size) + " B"

        if size < 1024 * 1024:
            return str(round(size / 1024, 1)) + " KB"

        if size < 1024 * 1024 * 1024:
            return str(round(size / (1024 * 1024), 1)) + " MB"

        return str(round(size / (1024 * 1024 * 1024), 1)) + " GB"

    def format_short_file_list(self, files):
        if len(files) == 0:
            return "No files"

        first_files = files[:3]
        file_text = ", ".join(first_files)
        remaining_count = len(files) - 3

        if remaining_count > 0:
            file_text = file_text + " +" + str(remaining_count) + " more"

        return file_text

    def refresh_style(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
