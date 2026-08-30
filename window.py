"""Builds the window"""

import os   # Imports Python's file and folder tools
from app_settings import load_app_settings, save_app_settings
from style import APP_STYLE
from state import AppState
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QAbstractItemView, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QHeaderView, QLineEdit, QMainWindow, QPushButton, QScrollArea, QStackedWidget, QStyle, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from components import create_folder_button
from neatify import get_common_folders, open_item, organize_folder, preview_organize_folder, undo_last_move, undo_move_by_id
from rules import add_extension_rule, add_keyword_rule, find_with_filters, get_category_for_file, load_rules, remove_extension_rule, remove_keyword_rule


class NeatifyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.app_settings = load_app_settings()
        self.editing_rule_type = None
        self.editing_rule_match = None
        self.folder_buttons = []
        self.center_folder_buttons = []
        self.setWindowTitle("Neatify")
        self.setStyleSheet(APP_STYLE)
        self.resize(920, 560)
        self.build_interface()
        self.apply_theme(self.app_settings["theme"], save_choice=False)

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
        self.settings_button = QPushButton("Settings")

        self.arrange_button.setObjectName("primaryCommand")
        self.find_button.setObjectName("commandButton")
        self.open_button.setObjectName("commandButton")
        self.undo_button.setObjectName("commandButton")
        self.history_button.setObjectName("commandButton")
        self.settings_button.setObjectName("commandButton")
        self.settings_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.settings_button.setIconSize(QSize(18, 18))

        self.commands_layout.addWidget(self.arrange_button)
        self.commands_layout.addWidget(self.find_button)
        self.commands_layout.addWidget(self.open_button)
        self.commands_layout.addWidget(self.undo_button)
        self.commands_layout.addWidget(self.history_button)
        self.commands_layout.addWidget(self.settings_button)
        self.commands_layout.addStretch()

        self.arrange_button.clicked.connect(self.start_arrange_command)
        self.find_button.clicked.connect(lambda: self.start_command("find "))
        self.open_button.clicked.connect(lambda: self.start_command("open "))
        self.undo_button.clicked.connect(lambda: self.start_command("undo"))
        self.history_button.clicked.connect(lambda: self.start_command("show history"))
        self.settings_button.clicked.connect(lambda: self.start_command("settings"))

    def create_ask_bar(self):
        self.ask_input = QLineEdit()
        self.ask_input.setPlaceholderText("Ask Neatify: show me all PDFs in this folder...")
        self.ask_input.returnPressed.connect(self.process_ask_command)
        self.ask_layout.addWidget(self.ask_input)

    def start_command(self, command_text):
        self.ask_input.setText(command_text)
        self.ask_input.setFocus()

        if command_text.startswith("arrange "):
            self.show_browser_view()
            self.show_output("Arrange", ["Press Enter to preview this folder, or edit the path first."])
        elif command_text == "find ":
            self.show_browser_view()
            self.show_output("Find", ["Type the file or folder name, then press Enter."])
        elif command_text == "open ":
            self.show_browser_view()
            self.show_output("Open", ["Type the file or folder path, then press Enter."])
        elif command_text == "undo":
            self.show_undo_page()
        elif command_text == "show history":
            self.show_history()
        elif command_text == "settings":
            self.show_settings()

    def start_arrange_command(self):
        folder_path = self.state.current_view_folder_path
        self.start_command("arrange " + folder_path)

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
        self.create_settings_panel()
        self.create_history_panel()

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
        self.output_list.setRootIsDecorated(True)
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.output_list.itemDoubleClicked.connect(self.open_output_item)

        self.proceed_button = QPushButton("Proceed")
        self.proceed_button.setObjectName("proceedButton")
        self.proceed_button.setVisible(False)
        self.proceed_button.clicked.connect(self.organize_selected_folder)

        self.cancel_preview_button = QPushButton("Cancel")
        self.cancel_preview_button.setObjectName("secondaryActionButton")
        self.cancel_preview_button.setVisible(False)
        self.cancel_preview_button.clicked.connect(self.cancel_preview)

        self.open_selected_button = QPushButton("Open Selected")
        self.open_selected_button.setObjectName("secondaryActionButton")
        self.open_selected_button.clicked.connect(self.open_selected_item)

        self.output_title.setObjectName("previewTitle")

        self.right_layout.addWidget(self.output_title)
        self.right_layout.addWidget(self.output_list, 1)
        self.right_layout.addWidget(self.open_selected_button)
        self.right_layout.addWidget(self.cancel_preview_button)
        self.right_layout.addWidget(self.proceed_button)

        self.show_output("Output", ["Choose a command or type in Ask Neatify."])

    def create_settings_panel(self):
        self.settings_panel = QWidget()
        self.settings_panel.setObjectName("settingsPanel")

        self.settings_layout = QVBoxLayout()
        self.settings_layout.setContentsMargins(32, 28, 32, 28)
        self.settings_layout.setSpacing(14)
        self.settings_panel.setLayout(self.settings_layout)

        settings_top_layout = QHBoxLayout()

        self.settings_title = QLabel("Settings")
        self.settings_title.setObjectName("settingsTitle")

        self.back_to_files_button = QPushButton("Back to Files")
        self.back_to_files_button.setObjectName("secondaryActionButton")
        self.back_to_files_button.clicked.connect(self.show_browser_view)

        settings_top_layout.addWidget(self.settings_title)
        settings_top_layout.addStretch()
        settings_top_layout.addWidget(self.back_to_files_button)

        self.settings_body_layout = QHBoxLayout()
        self.settings_body_layout.setSpacing(18)

        self.settings_menu_layout = QVBoxLayout()
        self.settings_menu_layout.setSpacing(10)

        self.customization_tab_button = self.create_settings_tab_button("Customization")
        self.my_rules_tab_button = self.create_settings_tab_button("My Rules")
        self.search_tab_button = self.create_settings_tab_button("Search")
        self.safety_tab_button = self.create_settings_tab_button("Safety")

        self.settings_menu_layout.addWidget(self.customization_tab_button)
        self.settings_menu_layout.addWidget(self.my_rules_tab_button)
        self.settings_menu_layout.addWidget(self.search_tab_button)
        self.settings_menu_layout.addWidget(self.safety_tab_button)
        self.settings_menu_layout.addStretch()

        self.settings_stack = QStackedWidget()
        self.settings_stack.setObjectName("settingsStack")

        self.customization_page = QWidget()
        self.customization_page.setObjectName("settingsPage")
        customization_layout = QVBoxLayout()
        customization_layout.setSpacing(14)
        self.customization_page.setLayout(customization_layout)

        customization_title = QLabel("Customization")
        customization_title.setObjectName("settingsSectionTitle")

        customization_help = QLabel("Choose the accent style Neatify uses for important buttons and selected items.")
        customization_help.setObjectName("settingsHelp")

        theme_buttons_layout = QGridLayout()
        theme_buttons_layout.setSpacing(10)
        midnight_button = QPushButton("Midnight Green")
        ocean_button = QPushButton("Ocean Blue")
        amber_button = QPushButton("Amber")
        rose_button = QPushButton("Rose Pink")
        violet_button = QPushButton("Slate Violet")

        midnight_button.setObjectName("secondaryActionButton")
        ocean_button.setObjectName("secondaryActionButton")
        amber_button.setObjectName("secondaryActionButton")
        rose_button.setObjectName("secondaryActionButton")
        violet_button.setObjectName("secondaryActionButton")

        midnight_button.clicked.connect(lambda: self.apply_theme("midnight"))
        ocean_button.clicked.connect(lambda: self.apply_theme("ocean"))
        amber_button.clicked.connect(lambda: self.apply_theme("amber"))
        rose_button.clicked.connect(lambda: self.apply_theme("rose"))
        violet_button.clicked.connect(lambda: self.apply_theme("violet"))

        theme_buttons_layout.addWidget(midnight_button, 0, 0)
        theme_buttons_layout.addWidget(ocean_button, 0, 1)
        theme_buttons_layout.addWidget(amber_button, 0, 2)
        theme_buttons_layout.addWidget(rose_button, 1, 0)
        theme_buttons_layout.addWidget(violet_button, 1, 1)

        self.theme_message_label = QLabel("Current theme: Midnight Green")
        self.theme_message_label.setObjectName("settingsMessage")

        customization_layout.addWidget(customization_title)
        customization_layout.addWidget(customization_help)
        customization_layout.addLayout(theme_buttons_layout)
        customization_layout.addWidget(self.theme_message_label)
        customization_layout.addStretch()

        self.my_rules_page = QWidget()
        self.my_rules_page.setObjectName("settingsPage")
        my_rules_layout = QVBoxLayout()
        my_rules_layout.setSpacing(14)
        self.my_rules_page.setLayout(my_rules_layout)

        my_rules_title = QLabel("My Rules")
        my_rules_title.setObjectName("settingsSectionTitle")

        my_rules_help = QLabel("Create extension rules like pdf -> Documents, or keyword rules like econ -> Economics.")
        my_rules_help.setObjectName("settingsHelp")

        rule_form_layout = QHBoxLayout()
        self.rule_type_input = QComboBox()
        self.rule_type_input.addItems(["Extension", "Keyword"])

        self.rule_match_input = QLineEdit()
        self.rule_match_input.setPlaceholderText("pdf or econ")

        self.rule_category_input = QLineEdit()
        self.rule_category_input.setPlaceholderText("Documents or Economics")

        self.add_rule_button = QPushButton("Add Rule")
        self.add_rule_button.setObjectName("primaryCommand")
        self.add_rule_button.clicked.connect(self.add_rule_from_form)

        self.remove_rule_button = QPushButton("Remove Selected")
        self.remove_rule_button.setObjectName("secondaryActionButton")
        self.remove_rule_button.clicked.connect(self.remove_selected_rule)

        self.clear_rule_form_button = QPushButton("Clear")
        self.clear_rule_form_button.setObjectName("secondaryActionButton")
        self.clear_rule_form_button.clicked.connect(self.clear_rule_form)

        rule_form_layout.addWidget(self.rule_type_input)
        rule_form_layout.addWidget(self.rule_match_input)
        rule_form_layout.addWidget(self.rule_category_input)
        rule_form_layout.addWidget(self.add_rule_button)
        rule_form_layout.addWidget(self.remove_rule_button)
        rule_form_layout.addWidget(self.clear_rule_form_button)

        self.settings_message_label = QLabel("")
        self.settings_message_label.setObjectName("settingsMessage")

        self.settings_rules_table = QTreeWidget()
        self.settings_rules_table.setObjectName("settingsRulesTable")
        self.settings_rules_table.setColumnCount(3)
        self.settings_rules_table.setHeaderLabels(["Rule", "Match", "Folder"])
        self.settings_rules_table.setRootIsDecorated(False)
        self.settings_rules_table.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_rules_table.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_rules_table.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.settings_rules_table.itemClicked.connect(self.load_selected_rule_into_form)

        my_rules_layout.addWidget(my_rules_title)
        my_rules_layout.addWidget(my_rules_help)
        my_rules_layout.addLayout(rule_form_layout)
        my_rules_layout.addWidget(self.settings_message_label)
        my_rules_layout.addWidget(self.settings_rules_table, 1)

        self.search_page = QWidget()
        self.search_page.setObjectName("settingsPage")
        search_layout = QVBoxLayout()
        search_layout.setSpacing(14)
        self.search_page.setLayout(search_layout)

        search_title = QLabel("Search")
        search_title.setObjectName("settingsSectionTitle")

        search_help = QLabel("Choose how Find searches. This affects the Find button and ask commands like find report.")
        search_help.setObjectName("settingsHelp")

        search_form_layout = QHBoxLayout()

        self.search_type_input = QComboBox()
        self.search_type_input.addItems(["All", "Files", "Folders", "Documents", "Images", "Videos", "Audio", "Archives", "Code", "pdf", "jpg", "png", "mp4"])
        self.search_type_input.setCurrentText(self.app_settings["search_type"])

        self.include_subfolders_checkbox = QCheckBox("Include subfolders")
        self.include_subfolders_checkbox.setChecked(self.app_settings["include_subfolders"])

        self.save_search_settings_button = QPushButton("Save Search Settings")
        self.save_search_settings_button.setObjectName("primaryCommand")
        self.save_search_settings_button.clicked.connect(self.save_search_settings)

        search_form_layout.addWidget(self.search_type_input)
        search_form_layout.addWidget(self.include_subfolders_checkbox)
        search_form_layout.addWidget(self.save_search_settings_button)
        search_form_layout.addStretch()

        self.search_message_label = QLabel("")
        self.search_message_label.setObjectName("settingsMessage")

        search_layout.addWidget(search_title)
        search_layout.addWidget(search_help)
        search_layout.addLayout(search_form_layout)
        search_layout.addWidget(self.search_message_label)
        search_layout.addStretch()

        self.safety_page = QWidget()
        self.safety_page.setObjectName("settingsPage")
        safety_layout = QVBoxLayout()
        safety_layout.setSpacing(14)
        self.safety_page.setLayout(safety_layout)

        safety_title = QLabel("Safety")
        safety_title.setObjectName("settingsSectionTitle")

        safety_text = QLabel("Neatify previews before moving files, keeps moved-file history, and supports undo for the last move set.")
        safety_text.setObjectName("settingsHelp")
        safety_text.setWordWrap(True)

        safety_layout.addWidget(safety_title)
        safety_layout.addWidget(safety_text)
        safety_layout.addStretch()

        self.settings_stack.addWidget(self.customization_page)
        self.settings_stack.addWidget(self.my_rules_page)
        self.settings_stack.addWidget(self.search_page)
        self.settings_stack.addWidget(self.safety_page)

        self.settings_body_layout.addLayout(self.settings_menu_layout, 1)
        self.settings_body_layout.addWidget(self.settings_stack, 4)

        self.settings_layout.addLayout(settings_top_layout)
        self.settings_layout.addLayout(self.settings_body_layout, 1)

        self.main_layout.addWidget(self.settings_panel, 1)
        self.settings_panel.hide()

    def create_history_panel(self):
        self.history_panel = QWidget()
        self.history_panel.setObjectName("historyPanel")

        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(32, 28, 32, 28)
        self.history_layout.setSpacing(14)
        self.history_panel.setLayout(self.history_layout)

        history_top_layout = QHBoxLayout()

        self.history_title = QLabel("History")
        self.history_title.setObjectName("settingsTitle")

        self.back_from_history_button = QPushButton("Back to Files")
        self.back_from_history_button.setObjectName("secondaryActionButton")
        self.back_from_history_button.clicked.connect(self.show_browser_view)

        history_top_layout.addWidget(self.history_title)
        history_top_layout.addStretch()
        history_top_layout.addWidget(self.back_from_history_button)

        self.history_help_label = QLabel("Recent move and undo operations.")
        self.history_help_label.setObjectName("settingsHelp")

        history_actions_layout = QHBoxLayout()

        self.open_history_item_button = QPushButton("Open Item")
        self.open_history_item_button.setObjectName("secondaryActionButton")
        self.open_history_item_button.clicked.connect(self.open_selected_history_item)

        self.open_history_destination_button = QPushButton("Open Destination")
        self.open_history_destination_button.setObjectName("secondaryActionButton")
        self.open_history_destination_button.clicked.connect(self.open_selected_history_destination)

        self.undo_selected_history_button = QPushButton("Undo Selected")
        self.undo_selected_history_button.setObjectName("primaryCommand")
        self.undo_selected_history_button.clicked.connect(self.undo_selected_history_move)

        history_actions_layout.addWidget(self.open_history_item_button)
        history_actions_layout.addWidget(self.open_history_destination_button)
        history_actions_layout.addWidget(self.undo_selected_history_button)
        history_actions_layout.addStretch()

        self.history_table = QTreeWidget()
        self.history_table.setObjectName("settingsRulesTable")
        self.history_table.setColumnCount(5)
        self.history_table.setHeaderLabels(["Time", "Action", "Files", "From", "To"])
        self.history_table.setRootIsDecorated(True)
        self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.history_table.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.history_table.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.history_layout.addLayout(history_top_layout)
        self.history_layout.addWidget(self.history_help_label)
        self.history_layout.addLayout(history_actions_layout)
        self.history_layout.addWidget(self.history_table, 1)

        self.main_layout.addWidget(self.history_panel, 1)
        self.history_panel.hide()

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
        counts = {}

        if not os.path.exists(folder_path):
            return counts

        if not os.path.isdir(folder_path):
            return counts

        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)

            if os.path.isfile(full_path):
                category = get_category_for_file(item)
                counts[category] = counts.get(category, 0) + 1

        return counts

    def get_preview_groups(self, folder_path):
        return preview_organize_folder(folder_path)

    def format_preview_text(self, category_name, files):
        if len(files) == 0:
            return category_name + "\nNo files found"

        first_files = files[:2]
        preview_text = category_name + "\n" + ", ".join(first_files)

        remaining_count = len(files) - 2

        if remaining_count > 0:
            preview_text = preview_text + " + " + str(remaining_count) + " more"

        return preview_text

    def update_preview_panel(self, folder_path):
        preview_groups = self.get_preview_groups(folder_path)

        self.output_title.setText("Arrange Preview")
        self.output_list.clear()
        self.output_list.setColumnCount(2)
        self.output_list.setHeaderLabels(["Move To", "Files"])
        self.output_list.setRootIsDecorated(True)
        self.output_list.header().show()
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proceed_button.setVisible(True)
        self.cancel_preview_button.setVisible(True)

        if len(preview_groups) == 0:
            list_item = QTreeWidgetItem(["Nothing to move", folder_path])
            self.output_list.addTopLevelItem(list_item)
            return

        for category_name in preview_groups:
            files = preview_groups[category_name]
            files_text = str(len(files)) + " files - expand to view"
            list_item = QTreeWidgetItem([category_name, files_text])
            list_item.setIcon(0, self.get_folder_icon())
            self.output_list.addTopLevelItem(list_item)

            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                file_item = QTreeWidgetItem([file_name, os.path.join(category_name, file_name)])
                file_item.setIcon(0, self.get_file_icon(file_name))
                file_item.setData(0, Qt.UserRole, file_path)
                list_item.addChild(file_item)

    def show_arrange_preview(self, folder_path=None):
        if folder_path is None or folder_path == "":
            folder_path = self.state.current_view_folder_path

        expanded_folder_path = os.path.expanduser(folder_path)

        if not os.path.exists(expanded_folder_path):
            self.show_output("Arrange Preview", ["Folder not found: " + expanded_folder_path])
            return

        if not os.path.isdir(expanded_folder_path):
            self.show_output("Arrange Preview", ["Path is not a folder: " + expanded_folder_path])
            return

        self.state.current_arrange_folder_path = expanded_folder_path
        self.update_preview_panel(expanded_folder_path)

    def show_output(self, title, lines, show_proceed=False):
        self.output_title.setText(title)
        self.output_list.clear()
        self.output_list.setColumnCount(1)
        self.output_list.setHeaderLabels(["Message"])
        self.output_list.setRootIsDecorated(False)
        self.output_list.header().hide()
        self.proceed_button.setVisible(show_proceed)
        self.cancel_preview_button.setVisible(False)

        for line in lines:
            list_item = QTreeWidgetItem([line.strip()])
            self.output_list.addTopLevelItem(list_item)

    def process_ask_command(self):
        command = self.ask_input.text().strip()
        lowered_command = command.lower()

        if lowered_command == "arrange":
            self.show_arrange_preview(self.state.current_view_folder_path)
            return

        if lowered_command.startswith("arrange "):
            folder_path = command[8:].strip()
            self.show_arrange_preview(folder_path)
            return

        if lowered_command.startswith("find "):
            item_name = command[5:].strip()
            self.show_find_results(item_name)
            return

        if lowered_command.startswith("open "):
            item_name = command[5:].strip()
            self.open_from_command(item_name)
            return

        if lowered_command == "undo" or lowered_command == "undo last move":
            self.show_undo_page()
            return

        if lowered_command == "show history":
            self.show_history()
            return

        if lowered_command == "settings":
            self.show_settings()
            return

        if lowered_command.startswith("rule "):
            message = self.apply_rule_command(command)
            self.show_output("Settings", [message])
            return

        if lowered_command.startswith("remove rule "):
            message = self.apply_rule_command(command)
            self.show_output("Settings", [message])
            return

        self.show_output("Output", ["Command not understood yet."])

    def show_find_results(self, item_name):
        if item_name == "":
            self.show_output("Find", ["Type a file or folder name after find."])
            return

        results = find_with_filters(
            item_name,
            self.state.selected_folder_path,
            self.app_settings["search_type"],
            self.app_settings["include_subfolders"],
        )

        if len(results) == 0:
            self.show_output("Find results", ["No matching item found."])
            return

        self.show_path_results("Find results", results)

    def apply_rule_command(self, command):
        lowered_command = command.lower()

        if lowered_command.startswith("rule "):
            return self.apply_add_rule_command(command)

        if lowered_command.startswith("remove rule "):
            return self.apply_remove_rule_command(command)

        return "Use: rule ext pdf Documents or rule keyword econ Economics"

    def apply_add_rule_command(self, command):
        parts = command.split()

        if len(parts) < 4:
            return "Use: rule ext pdf Documents or rule keyword econ Economics"

        rule_type = parts[1].lower()
        match_text = parts[2]
        category = " ".join(parts[3:])

        if rule_type == "ext":
            add_extension_rule(match_text, category)
            return "Added extension rule: " + match_text + " -> " + category

        if rule_type == "keyword":
            add_keyword_rule(match_text, category)
            return "Added keyword rule: " + match_text + " -> " + category

        return "Rule type must be ext or keyword."

    def apply_remove_rule_command(self, command):
        parts = command.split()

        if len(parts) != 4:
            return "Use: remove rule ext pdf or remove rule keyword econ"

        rule_type = parts[2].lower()
        match_text = parts[3]

        if rule_type == "ext":
            remove_extension_rule(match_text)
            return "Removed extension rule: " + match_text

        if rule_type == "keyword":
            remove_keyword_rule(match_text)
            return "Removed keyword rule: " + match_text

        return "Rule type must be ext or keyword."

    def refresh_after_rules_change(self):
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_cards()
        self.update_folder_contents_list(self.state.current_view_folder_path)

    def open_from_command(self, item_name):
        if item_name == "":
            self.show_output("Open", ["Type a file or folder name after open."])
            return

        expanded_path = os.path.expanduser(item_name)

        if os.path.exists(expanded_path):
            open_item(expanded_path)
            self.show_output("Open", ["Opened: " + expanded_path])
            return

        results = find_with_filters(
            item_name,
            self.state.selected_folder_path,
            self.app_settings["search_type"],
            self.app_settings["include_subfolders"],
        )

        if len(results) == 0:
            self.show_output("Open", ["No matching item found."])
            return

        if len(results) == 1:
            open_item(results[0])
            self.show_output("Open", ["Opened: " + results[0]])
            return

        self.show_path_results("Choose one to open", results)

    def create_settings_tab_button(self, button_text):
        button = QPushButton(button_text)
        button.setObjectName("settingsTabButton")

        if button_text == "Customization":
            button.clicked.connect(lambda: self.show_settings_page(0))
        elif button_text == "My Rules":
            button.clicked.connect(lambda: self.show_settings_page(1))
        elif button_text == "Search":
            button.clicked.connect(lambda: self.show_settings_page(2))
        elif button_text == "Safety":
            button.clicked.connect(lambda: self.show_settings_page(3))

        return button

    def show_settings_page(self, page_number):
        self.settings_stack.setCurrentIndex(page_number)

        tab_buttons = [
            self.customization_tab_button,
            self.my_rules_tab_button,
            self.search_tab_button,
            self.safety_tab_button,
        ]

        for index, button in enumerate(tab_buttons):
            if index == page_number:
                button.setObjectName("activeSettingsTabButton")
            else:
                button.setObjectName("settingsTabButton")

            self.refresh_style(button)

    def apply_theme(self, theme_name, save_choice=True):
        themes = {
            "midnight": {
                "name": "Midnight Green",
                "main_background": "#161716",
                "app_background": "#191A19",
                "panel_background": "#171817",
                "left_panel": "#1B1C1B",
                "right_panel": "#1A1B1A",
                "input_background": "#111211",
                "button_background": "#20211F",
                "hover_background": "#2A2B29",
                "selected_background": "#3B3C38",
                "border": "#40413F",
                "soft_border": "#30312F",
                "text": "#F6F3ED",
                "muted_text": "#AAA9A1",
                "quiet_text": "#8E9088",
                "accent": "#29D85F",
                "accent_hover": "#34E96C",
                "accent_text": "#07150B",
            },
            "ocean": {
                "name": "Ocean Blue",
                "main_background": "#0B141A",
                "app_background": "#101C24",
                "panel_background": "#0E1920",
                "left_panel": "#10202A",
                "right_panel": "#0F1C24",
                "input_background": "#081116",
                "button_background": "#142631",
                "hover_background": "#1D3645",
                "selected_background": "#21485C",
                "border": "#315467",
                "soft_border": "#233B47",
                "text": "#F2FAFD",
                "muted_text": "#A9BBC4",
                "quiet_text": "#8296A0",
                "accent": "#38BDF8",
                "accent_hover": "#7DD3FC",
                "accent_text": "#06131A",
            },
            "amber": {
                "name": "Amber",
                "main_background": "#17130B",
                "app_background": "#1E190F",
                "panel_background": "#1A160D",
                "left_panel": "#211B10",
                "right_panel": "#1D180E",
                "input_background": "#120F08",
                "button_background": "#2A2213",
                "hover_background": "#382D18",
                "selected_background": "#4A3A1B",
                "border": "#5A4825",
                "soft_border": "#3B301A",
                "text": "#FFF8EA",
                "muted_text": "#C8BCA5",
                "quiet_text": "#A59476",
                "accent": "#F5B942",
                "accent_hover": "#FFD166",
                "accent_text": "#1A1204",
            },
            "rose": {
                "name": "Rose Pink",
                "main_background": "#180F15",
                "app_background": "#21161D",
                "panel_background": "#1D131A",
                "left_panel": "#261923",
                "right_panel": "#211720",
                "input_background": "#120B10",
                "button_background": "#2E2029",
                "hover_background": "#3B2A35",
                "selected_background": "#56384A",
                "border": "#68465A",
                "soft_border": "#3D2A35",
                "text": "#FFF5FA",
                "muted_text": "#D2B7C5",
                "quiet_text": "#AE8D9C",
                "accent": "#F472B6",
                "accent_hover": "#FB8FCA",
                "accent_text": "#210614",
            },
            "violet": {
                "name": "Slate Violet",
                "main_background": "#12111A",
                "app_background": "#191824",
                "panel_background": "#161520",
                "left_panel": "#1D1B2A",
                "right_panel": "#191725",
                "input_background": "#0F0E16",
                "button_background": "#252235",
                "hover_background": "#302C45",
                "selected_background": "#403A5E",
                "border": "#514A70",
                "soft_border": "#322E44",
                "text": "#F8F6FF",
                "muted_text": "#BDB7D2",
                "quiet_text": "#9991B2",
                "accent": "#A78BFA",
                "accent_hover": "#C4B5FD",
                "accent_text": "#10091F",
            },
        }

        theme = themes.get(theme_name, themes["midnight"])
        theme_style = self.build_theme_style(theme)
        self.theme_message_label.setText("Current theme: " + theme["name"])

        self.setStyleSheet(theme_style)

        if save_choice:
            self.app_settings["theme"] = theme_name
            save_app_settings(self.app_settings)

        self.show_settings_page(self.settings_stack.currentIndex())

    def build_theme_style(self, theme):
        theme_style = APP_STYLE

        color_replacements = {
            "#161716": theme["main_background"],
            "#191A19": theme["app_background"],
            "#171817": theme["panel_background"],
            "#1B1C1B": theme["left_panel"],
            "#1A1B1A": theme["right_panel"],
            "#111211": theme["input_background"],
            "#20211F": theme["button_background"],
            "#2A2B29": theme["hover_background"],
            "#252624": theme["hover_background"],
            "#3B3C38": theme["selected_background"],
            "#40413F": theme["border"],
            "#313330": theme["soft_border"],
            "#30312F": theme["soft_border"],
            "#2C2D2B": theme["soft_border"],
            "#F6F3ED": theme["text"],
            "#FFFFFF": theme["text"],
            "#D8D5CD": theme["text"],
            "#AAA9A1": theme["muted_text"],
            "#979890": theme["muted_text"],
            "#8E9088": theme["quiet_text"],
            "#29D85F": theme["accent"],
            "#34E96C": theme["accent_hover"],
            "#19E241": theme["accent"],
            "#07150B": theme["accent_text"],
            "#08290D": theme["input_background"],
        }

        for old_color in color_replacements:
            theme_style = theme_style.replace(old_color, color_replacements[old_color])

        return theme_style

    def add_rule_from_form(self):
        rule_type = self.rule_type_input.currentText()
        match_text = self.rule_match_input.text().strip()
        category = self.rule_category_input.text().strip()

        if match_text == "" or category == "":
            self.settings_message_label.setText("Type both a match and a folder name.")
            return

        if self.editing_rule_type is not None:
            if self.editing_rule_type == "Extension":
                remove_extension_rule(self.editing_rule_match)
            elif self.editing_rule_type == "Keyword":
                remove_keyword_rule(self.editing_rule_match)

        if rule_type == "Extension":
            add_extension_rule(match_text, category)
            self.settings_message_label.setText("Saved extension rule: " + match_text + " -> " + category)
        else:
            add_keyword_rule(match_text, category)
            self.settings_message_label.setText("Saved keyword rule: " + match_text + " -> " + category)

        self.clear_rule_form()
        self.populate_settings_table()
        self.refresh_after_rules_change()

    def load_selected_rule_into_form(self, selected_rule, column=0):
        rule_type = selected_rule.text(0)
        match_text = selected_rule.text(1)
        category = selected_rule.text(2)

        self.rule_type_input.setCurrentText(rule_type)
        self.rule_match_input.setText(match_text)
        self.rule_category_input.setText(category)
        self.editing_rule_type = rule_type
        self.editing_rule_match = match_text
        self.add_rule_button.setText("Save Rule")
        self.settings_message_label.setText("Editing rule: " + match_text)

    def clear_rule_form(self):
        self.rule_match_input.clear()
        self.rule_category_input.clear()
        self.editing_rule_type = None
        self.editing_rule_match = None
        self.add_rule_button.setText("Add Rule")

    def remove_selected_rule(self):
        selected_items = self.settings_rules_table.selectedItems()

        if len(selected_items) == 0:
            self.settings_message_label.setText("Select a rule first.")
            return

        selected_rule = selected_items[0]
        rule_type = selected_rule.text(0)
        match_text = selected_rule.text(1)

        if rule_type == "Extension":
            remove_extension_rule(match_text)
        elif rule_type == "Keyword":
            remove_keyword_rule(match_text)

        self.settings_message_label.setText("Removed rule: " + match_text)
        self.clear_rule_form()
        self.populate_settings_table()
        self.refresh_after_rules_change()

    def save_search_settings(self):
        self.app_settings["search_type"] = self.search_type_input.currentText()
        self.app_settings["include_subfolders"] = self.include_subfolders_checkbox.isChecked()
        save_app_settings(self.app_settings)
        self.search_message_label.setText("Search settings saved.")

    def show_settings(self):
        self.hide_browser_panels()
        self.history_panel.hide()
        self.settings_panel.show()
        self.populate_settings_table()
        self.show_settings_page(0)
        self.rule_match_input.setFocus()

    def show_browser_view(self):
        self.settings_panel.hide()
        self.history_panel.hide()
        self.ask_input.show()
        self.left_panel.show()
        self.center_panel.show()
        self.right_panel.show()

    def hide_browser_panels(self):
        self.left_panel.hide()
        self.center_panel.hide()
        self.right_panel.hide()
        self.ask_input.hide()

    def populate_settings_table(self):
        rules = load_rules()
        self.settings_rules_table.clear()

        for extension in sorted(rules["extensions"]):
            category = rules["extensions"][extension]
            list_item = QTreeWidgetItem(["Extension", extension, category])
            list_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            self.settings_rules_table.addTopLevelItem(list_item)

        for keyword in sorted(rules["keywords"]):
            category = rules["keywords"][keyword]
            list_item = QTreeWidgetItem(["Keyword", keyword, category])
            list_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
            self.settings_rules_table.addTopLevelItem(list_item)

    def process_settings_command(self):
        self.add_rule_from_form()

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
        self.output_list.setRootIsDecorated(False)
        self.output_list.header().show()
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proceed_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)

        for item_path in paths:
            item_name = os.path.basename(item_path)
            parent_folder = os.path.dirname(item_path)
            list_item = QTreeWidgetItem([item_name, parent_folder])
            list_item.setIcon(0, self.get_path_icon(item_path))
            list_item.setData(0, Qt.UserRole, item_path)
            self.output_list.addTopLevelItem(list_item)

    def organize_selected_folder(self):
        folder_path = self.state.current_arrange_folder_path
        organize_folder(folder_path, dry_run=False)
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_cards()
        self.update_folder_contents_list(self.state.current_view_folder_path)
        self.show_output("Done", ["Organized: " + folder_path])

    def cancel_preview(self):
        self.state.current_preview = {}
        self.proceed_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        self.show_output("Output", ["Preview cancelled."])

    def show_history(self):
        self.hide_browser_panels()
        self.settings_panel.hide()
        self.history_title.setText("History")
        self.history_help_label.setText("Recent move and undo operations.")
        self.history_panel.show()
        self.populate_history_table()

    def show_undo_page(self):
        self.hide_browser_panels()
        self.settings_panel.hide()
        self.history_title.setText("Undo")
        self.history_help_label.setText("Select a moved row, check From and To, then press Undo Selected.")
        self.history_panel.show()
        self.populate_history_table()

    def populate_history_table(self):
        self.history_table.clear()
        batches = self.get_history_batches()

        if len(batches) == 0:
            self.history_table.addTopLevelItem(QTreeWidgetItem(["", "No history found yet.", "", "", ""]))
            return

        for batch in batches[:20]:
            action = "Arrange"

            if batch["undone"]:
                action = "Undone"

            batch_item = QTreeWidgetItem([
                batch["time"],
                action,
                str(len(batch["moves"])) + " files",
                batch["from"],
                batch["to"],
            ])
            batch_item.setIcon(2, self.get_folder_icon())
            batch_item.setData(0, Qt.UserRole, batch)
            self.history_table.addTopLevelItem(batch_item)

            for move in batch["moves"]:
                file_item = QTreeWidgetItem([
                    "",
                    move["action"],
                    move["item"],
                    move["from"],
                    move["to"],
                ])
                file_item.setIcon(2, self.get_path_icon(move["path_for_icon"]))
                file_item.setData(0, Qt.UserRole, move)
                batch_item.addChild(file_item)

    def get_history_batches(self):
        history_path = "neatify_history.txt"

        if not os.path.exists(history_path):
            return []

        with open(history_path, "r") as history_file:
            lines = history_file.readlines()

        batches = {}
        batch_order = []

        for line in lines:
            history_item = self.parse_history_line(line)

            if history_item is None:
                continue

            move_id = history_item["move_id"]

            if move_id not in batches:
                batches[move_id] = {
                    "move_id": move_id,
                    "time": history_item["time"],
                    "from": history_item["from"],
                    "to": history_item["to"],
                    "moves": [],
                    "undone": False,
                }
                batch_order.append(move_id)

            if history_item["action"] == "Moved":
                batches[move_id]["moves"].append(history_item)
                batches[move_id]["time"] = history_item["time"]
                batches[move_id]["from"] = history_item["from"]
                batches[move_id]["to"] = history_item["to"]
            elif history_item["action"] == "UNDONE":
                batches[move_id]["undone"] = True

        grouped_batches = []

        for move_id in reversed(batch_order):
            batch = batches[move_id]

            if len(batch["moves"]) > 0:
                grouped_batches.append(batch)

        return grouped_batches

    def get_selected_history_item(self):
        selected_items = self.history_table.selectedItems()

        if len(selected_items) == 0:
            return None

        return selected_items[0].data(0, Qt.UserRole)

    def get_selected_history_batches(self):
        selected_items = self.history_table.selectedItems()
        selected_batches = []
        selected_move_ids = []

        for selected_item in selected_items:
            item_data = selected_item.data(0, Qt.UserRole)

            if item_data is None:
                continue

            if "moves" in item_data:
                batch = item_data
            else:
                parent_item = selected_item.parent()

                if parent_item is None:
                    continue

                batch = parent_item.data(0, Qt.UserRole)

            if batch["move_id"] not in selected_move_ids:
                selected_batches.append(batch)
                selected_move_ids.append(batch["move_id"])

        return selected_batches

    def open_selected_history_item(self):
        history_item = self.get_selected_history_item()

        if history_item is None:
            self.history_help_label.setText("Select a history row first.")
            return

        if "moves" in history_item:
            if len(history_item["moves"]) == 0:
                self.history_help_label.setText("This batch has no files to open.")
                return

            history_item = history_item["moves"][0]

        item_path = history_item["new_path"]

        if history_item["action"] == "UNDONE":
            item_path = history_item["old_path"]

        open_item(item_path)
        self.history_help_label.setText("Opened: " + item_path)

    def open_selected_history_destination(self):
        history_item = self.get_selected_history_item()

        if history_item is None:
            self.history_help_label.setText("Select a history row first.")
            return

        if "moves" in history_item:
            destination_folder = history_item["to"]
            open_item(destination_folder)
            self.history_help_label.setText("Opened destination: " + destination_folder)
            return

        destination_folder = os.path.dirname(history_item["new_path"])

        if history_item["action"] == "UNDONE":
            destination_folder = os.path.dirname(history_item["old_path"])

        open_item(destination_folder)
        self.history_help_label.setText("Opened destination: " + destination_folder)

    def undo_selected_history_move(self):
        selected_batches = self.get_selected_history_batches()

        if len(selected_batches) == 0:
            self.history_help_label.setText("Select one or more arrange batches first.")
            return

        undone_count = 0
        messages = []

        for batch in selected_batches:
            if batch["undone"]:
                messages.append("Already undone: " + batch["move_id"])
                continue

            result = undo_move_by_id(batch["move_id"])
            messages.append(result)

            if result.startswith("Undone"):
                undone_count = undone_count + 1

        self.populate_history_table()
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_cards()
        self.update_folder_contents_list(self.state.current_view_folder_path)

        if undone_count == 1:
            self.history_help_label.setText(messages[0])
        else:
            self.history_help_label.setText("Undone " + str(undone_count) + " selected batches.")

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
        move_id = parts[1]
        action = parts[2]
        paths_part = parts[3]

        if " -> " not in paths_part:
            return None

        old_path, new_path = paths_part.split(" -> ")

        return {
            "time": timestamp,
            "move_id": move_id,
            "action": action,
            "item": os.path.basename(old_path),
            "from": os.path.dirname(old_path),
            "to": os.path.dirname(new_path),
            "path_for_icon": new_path,
            "old_path": old_path,
            "new_path": new_path,
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
        category = get_category_for_file(file_name)

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
