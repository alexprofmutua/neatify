"""Builds the window"""

import csv
import os   # Imports Python's file and folder tools
import re
from datetime import datetime
from app_paths import get_project_path
from app_settings import load_app_settings, save_app_settings
from style import APP_STYLE
from state import AppState
from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QCheckBox, QComboBox, QDialog, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QHeaderView, QLineEdit, QMainWindow, QPushButton, QScrollArea, QSizePolicy, QStackedWidget, QStyle, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from components import create_folder_button
from neatify import create_move_id, get_common_folders, get_history_path, get_unique_destination, move_file, open_item, preview_organize_folder, undo_last_move, undo_move_by_id
from rules import add_extension_rule, add_keyword_rule, find_with_filters, get_arrangement_for_file, get_category_for_file, load_rules, remove_extension_rule, remove_keyword_rule

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
except ImportError:
    QPdfDocument = None
    QPdfView = None


class NeatifyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.app_settings = load_app_settings()
        self.editing_rule_type = None
        self.editing_rule_match = None
        self.editing_rule_scope = None
        self.folder_buttons = []
        self.folder_button_paths = {}
        self.folder_back_stack = []
        self.help_dialog = None
        self.setWindowTitle("Neatify")
        self.setWindowIcon(QIcon(get_project_path("assets", "neatify-logo.svg")))
        self.setStyleSheet(APP_STYLE)
        self.build_interface()
        self.apply_theme(self.app_settings["theme"], save_choice=False)
        self.resize_to_screen()

    def resize_to_screen(self):
        screen = self.screen()

        if screen is None:
            self.resize(1200, 780)
            return

        available_geometry = screen.availableGeometry()
        width = int(available_geometry.width() * 0.75)
        height = int(available_geometry.height() * 0.75)
        self.setMinimumSize(980, 640)
        self.resize(width, height)
        self.move(
            available_geometry.x() + int((available_geometry.width() - width) / 2),
            available_geometry.y() + int((available_geometry.height() - height) / 2),
        )

    def build_interface(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        self.app_layout = QHBoxLayout()
        central_widget.setLayout(self.app_layout)

        self.page_layout = QVBoxLayout()
        self.commands_layout = QHBoxLayout()
        self.ask_layout = QHBoxLayout()
        self.main_layout = QHBoxLayout()

        self.setup_layout_spacing()

        self.page_layout.addLayout(self.commands_layout)
        self.page_layout.addLayout(self.ask_layout)
        self.page_layout.addLayout(self.main_layout)
        self.app_layout.addLayout(self.page_layout, 1)

        self.create_command_bar()
        self.create_ask_bar()
        self.create_panels()

    def setup_layout_spacing(self):
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.app_layout.setSpacing(0)

        self.page_layout.setContentsMargins(18, 14, 18, 18)
        self.page_layout.setSpacing(12)

        self.commands_layout.setSpacing(8)
        self.ask_layout.setSpacing(10)
        self.main_layout.setSpacing(0)

    def create_command_bar(self):
        self.arrange_button = QPushButton("Arrange")
        self.find_button = QPushButton("Find")
        self.undo_button = QPushButton("Undo")
        self.history_button = QPushButton("History")
        self.command_buttons = []

        self.arrange_button.setObjectName("primaryCommand")
        self.find_button.setObjectName("commandButton")
        self.undo_button.setObjectName("commandButton")
        self.history_button.setObjectName("commandButton")
        self.command_buttons = [
            self.arrange_button,
            self.find_button,
            self.undo_button,
            self.history_button,
        ]

        self.commands_layout.addWidget(self.arrange_button)
        self.commands_layout.addWidget(self.find_button)
        self.commands_layout.addWidget(self.undo_button)
        self.commands_layout.addWidget(self.history_button)
        self.commands_layout.addStretch()

        self.arrange_button.clicked.connect(self.start_arrange_command)
        self.find_button.clicked.connect(lambda: self.start_command("find "))
        self.undo_button.clicked.connect(lambda: self.start_command("undo"))
        self.history_button.clicked.connect(lambda: self.start_command("show history"))

    def create_ask_bar(self):
        self.ask_input = QLineEdit()
        self.ask_input.setPlaceholderText("Ask Neatify: show me all PDFs in this folder...")
        self.ask_input.returnPressed.connect(self.process_ask_command)
        self.ask_layout.addWidget(self.ask_input)

    def start_command(self, command_text):
        self.ask_input.setText(command_text)
        self.ask_input.setFocus()

        if command_text.startswith("arrange "):
            self.set_active_command_button(self.arrange_button)
            self.show_browser_view()
            self.show_output("Arrange", ["Press Enter to preview this folder, or edit the path first."])
        elif command_text == "find ":
            self.set_active_command_button(self.find_button)
            self.show_browser_view()
            self.show_output("Find", ["Type the file or folder name, then press Enter."])
        elif command_text == "undo":
            self.set_active_command_button(self.undo_button)
            self.show_undo_page()
        elif command_text == "show history":
            self.set_active_command_button(self.history_button)
            self.show_history()
        elif command_text == "settings":
            self.clear_active_command_button()
            self.show_settings()

    def start_arrange_command(self):
        folder_path = self.state.current_view_folder_path
        self.start_command("arrange " + folder_path)

    def set_active_command_button(self, active_button):
        for button in self.command_buttons:
            if button == active_button:
                button.setObjectName("primaryCommand")
            else:
                button.setObjectName("commandButton")

            self.refresh_style(button)

    def clear_active_command_button(self):
        for button in self.command_buttons:
            button.setObjectName("commandButton")
            self.refresh_style(button)

    def set_active_sidebar_footer_button(self, active_button):
        footer_buttons = [
            self.sidebar_settings_button,
            self.sidebar_help_button,
        ]

        for button in footer_buttons:
            if button == active_button:
                button.setObjectName("activeSidebarFooterButton")
            else:
                button.setObjectName("sidebarFooterButton")

            self.refresh_style(button)

    def clear_active_sidebar_footer_button(self):
        self.set_active_sidebar_footer_button(None)

    def set_active_folder_button(self, active_button):
        for button in self.folder_buttons:
            if button == active_button:
                button.setObjectName("activeFolder")
            else:
                button.setObjectName("folderItem")

            self.refresh_style(button)

    def restore_active_folder_button(self):
        selected_path = os.path.abspath(os.path.expanduser(self.state.selected_folder_path))
        self.set_active_folder_button(self.folder_button_paths.get(selected_path))

    def clear_active_folder_button(self):
        self.set_active_folder_button(None)

    def create_panels(self):
        self.left_panel = QWidget()
        self.center_panel = QWidget()
        self.right_panel = QWidget()

        self.left_panel.setObjectName("leftPanel")
        self.center_panel.setObjectName("centerPanel")
        self.right_panel.setObjectName("rightPanel")

        self.left_panel.setMinimumWidth(280)
        self.left_panel.setMaximumWidth(300)
        self.right_panel.setMinimumWidth(300)
        self.right_panel.setMaximumWidth(360)

        self.left_layout = QVBoxLayout()
        self.center_panel_layout = QVBoxLayout()
        self.center_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.left_layout.setContentsMargins(22, 34, 20, 28)
        self.center_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setContentsMargins(24, 24, 24, 24)
        self.right_layout.setContentsMargins(20, 28, 20, 24)

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

        self.app_layout.insertWidget(0, self.left_panel)
        self.main_layout.addWidget(self.center_panel, 2)
        self.main_layout.addWidget(self.right_panel, 1)

        self.create_folder_panel()
        self.create_center_panel()
        self.create_preview_panel()
        self.create_settings_panel()
        self.create_history_panel()

    def create_folder_panel(self):
        brand_button = QPushButton("Neatify")
        brand_button.setObjectName("sidebarBrand")
        brand_button.setIcon(self.get_sidebar_icon("brand"))
        brand_button.setIconSize(QSize(32, 32))
        brand_button.setEnabled(False)
        self.left_layout.addWidget(brand_button)

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

        self.custom_folders_title = QLabel("Selected Folders")
        self.custom_folders_title.setObjectName("foldersTitle")
        self.custom_folders_title.hide()
        self.left_layout.addWidget(self.custom_folders_title)

        self.left_layout.addStretch()
        self.sidebar_footer_start_index = self.left_layout.count()

        self.sidebar_settings_button = QPushButton("Settings")
        self.sidebar_settings_button.setObjectName("sidebarFooterButton")
        self.sidebar_settings_button.setIcon(self.get_sidebar_icon("settings"))
        self.sidebar_settings_button.setIconSize(QSize(26, 26))
        self.sidebar_settings_button.clicked.connect(lambda: self.start_command("settings"))

        self.sidebar_help_button = QPushButton("Help")
        self.sidebar_help_button.setObjectName("sidebarFooterButton")
        self.sidebar_help_button.setIcon(self.get_sidebar_icon("help"))
        self.sidebar_help_button.setIconSize(QSize(26, 26))
        self.sidebar_help_button.clicked.connect(self.show_help)

        footer_divider = QLabel("")
        footer_divider.setObjectName("sidebarFooterDivider")
        self.left_layout.addWidget(footer_divider)
        self.left_layout.addWidget(self.sidebar_settings_button)
        self.left_layout.addWidget(self.sidebar_help_button)

    def add_left_folder_button(self, folder_path, active=False):
        normalized_path = os.path.abspath(os.path.expanduser(folder_path))

        if normalized_path in self.folder_button_paths:
            return self.folder_button_paths[normalized_path]

        folder_name = self.get_folder_display_name(folder_path)
        folder_button = create_folder_button(folder_name, active=active)
        folder_button.setIcon(self.get_sidebar_icon(folder_name))
        folder_button.setIconSize(QSize(26, 26))
        folder_button.clicked.connect(lambda checked=False, name=folder_name, path=normalized_path, button=folder_button: self.select_folder(name, path, button))

        self.folder_buttons.append(folder_button)
        self.folder_button_paths[normalized_path] = folder_button

        if hasattr(self, "sidebar_footer_start_index"):
            self.left_layout.insertWidget(self.sidebar_footer_start_index, folder_button)
            self.sidebar_footer_start_index = self.sidebar_footer_start_index + 1
        else:
            self.left_layout.addWidget(folder_button)

        return folder_button

    def create_center_panel(self):
        self.folder_name_label = QLabel(self.state.selected_folder_name)
        self.folder_summary_label = QLabel(self.get_folder_status(self.state.selected_folder_path))

        self.folder_name_label.setObjectName("folderName")
        self.folder_summary_label.setObjectName("folderSummary")

        self.breadcrumb_layout = QHBoxLayout()
        self.breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumb_layout.setSpacing(6)

        self.breadcrumb_root_button = QPushButton(self.state.selected_folder_name)
        self.breadcrumb_root_button.setObjectName("breadcrumbButton")
        self.breadcrumb_root_button.clicked.connect(self.go_to_selected_root_folder)

        self.breadcrumb_separator_label = QLabel(">")
        self.breadcrumb_separator_label.setObjectName("breadcrumbSeparator")

        self.breadcrumb_current_label = QLabel("")
        self.breadcrumb_current_label.setObjectName("breadcrumbCurrent")

        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.go_back_folder)

        self.breadcrumb_layout.addWidget(self.breadcrumb_root_button)
        self.breadcrumb_layout.addWidget(self.breadcrumb_separator_label)
        self.breadcrumb_layout.addWidget(self.breadcrumb_current_label)
        self.breadcrumb_layout.addStretch()
        self.breadcrumb_layout.addWidget(self.back_button)
        self.folder_contents_list = QTreeWidget()
        self.folder_contents_list.setObjectName("folderContentsList")
        self.folder_contents_list.setColumnCount(4)
        self.folder_contents_list.setHeaderLabels(["Name", "Kind", "Size", "Modified"])
        self.folder_contents_list.setRootIsDecorated(False)
        self.folder_contents_list.setMinimumHeight(420)
        self.folder_contents_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.folder_contents_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.folder_contents_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.folder_contents_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.folder_contents_list.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.folder_contents_list.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.folder_contents_list.itemClicked.connect(self.handle_browser_item_clicked)
        self.folder_contents_list.itemDoubleClicked.connect(self.open_browser_item)
        self.folder_contents_list.installEventFilter(self)

        self.folders_title_label = QLabel("Contents")
        self.folders_title_label.setObjectName("sectionTitle")

        self.center_layout.addWidget(self.folder_name_label)
        self.center_layout.addLayout(self.breadcrumb_layout)
        self.center_layout.addWidget(self.folder_summary_label)
        self.center_layout.addWidget(self.folders_title_label)
        self.center_layout.addWidget(self.folder_contents_list, 1)

        self.create_arrange_preview_view()

        self.center_layout.addStretch()

        self.update_folder_contents_list(self.state.selected_folder_path)
        self.update_breadcrumb_controls()

    def create_arrange_preview_view(self):
        self.preview_title_label = QLabel("Arrange Preview")
        self.preview_title_label.setObjectName("arrangePreviewTitle")

        self.preview_help_label = QLabel("Review every file before anything moves")
        self.preview_help_label.setObjectName("arrangePreviewHelp")

        self.preview_warning_label = QLabel("Preview only. No files move until you confirm.")
        self.preview_warning_label.setObjectName("arrangePreviewWarning")

        self.preview_table = QTreeWidget()
        self.preview_table.setObjectName("arrangePreviewTable")
        self.preview_table.setColumnCount(6)
        self.preview_table.setHeaderLabels(["", "File name", "From", "", "To", "Status"])
        self.preview_table.setRootIsDecorated(False)
        self.preview_table.setWordWrap(True)
        self.preview_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.preview_table.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.preview_table.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.preview_table.header().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.setColumnWidth(2, 310)
        self.preview_table.setColumnWidth(4, 330)
        self.preview_table.itemDoubleClicked.connect(self.open_output_item)
        self.preview_table.itemChanged.connect(self.update_arrange_confirm_state)
        self.preview_table.installEventFilter(self)

        self.preview_actions_layout = QHBoxLayout()
        self.preview_cancel_button = QPushButton("Cancel")
        self.preview_cancel_button.setObjectName("dangerActionButton")
        self.preview_cancel_button.clicked.connect(self.cancel_preview)

        self.preview_confirm_button = QPushButton("Confirm Arrange")
        self.preview_confirm_button.setObjectName("confirmArrangeButton")
        self.preview_confirm_button.clicked.connect(self.organize_selected_folder)

        self.preview_actions_layout.addWidget(self.preview_cancel_button)
        self.preview_actions_layout.addStretch()
        self.preview_actions_layout.addWidget(self.preview_confirm_button)

        self.center_layout.addWidget(self.preview_title_label)
        self.center_layout.addWidget(self.preview_help_label)
        self.center_layout.addWidget(self.preview_warning_label)
        self.center_layout.addWidget(self.preview_table)
        self.center_layout.addLayout(self.preview_actions_layout)
        self.set_arrange_preview_visible(False)

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
        self.output_list.installEventFilter(self)

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

        self.summary_panel = QWidget()
        self.summary_panel.setObjectName("summaryPanel")
        self.summary_layout = QVBoxLayout()
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        self.summary_layout.setSpacing(7)
        self.summary_panel.setLayout(self.summary_layout)
        self.summary_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.summary_panel.hide()

        self.right_layout.addWidget(self.summary_panel, 0, Qt.AlignmentFlag.AlignTop)
        self.right_layout.addWidget(self.output_list, 1)
        self.right_layout.addWidget(self.open_selected_button)
        self.right_layout.addWidget(self.cancel_preview_button)
        self.right_layout.addWidget(self.proceed_button)

        self.show_details_panel()

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
        self.back_to_files_button.clicked.connect(self.return_to_files)

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
        finder_light_button = QPushButton("Light Mode")

        midnight_button.setObjectName("secondaryActionButton")
        ocean_button.setObjectName("secondaryActionButton")
        amber_button.setObjectName("secondaryActionButton")
        rose_button.setObjectName("secondaryActionButton")
        violet_button.setObjectName("secondaryActionButton")
        finder_light_button.setObjectName("secondaryActionButton")

        midnight_button.clicked.connect(lambda: self.apply_theme("midnight"))
        ocean_button.clicked.connect(lambda: self.apply_theme("ocean"))
        amber_button.clicked.connect(lambda: self.apply_theme("amber"))
        rose_button.clicked.connect(lambda: self.apply_theme("rose"))
        violet_button.clicked.connect(lambda: self.apply_theme("violet"))
        finder_light_button.clicked.connect(lambda: self.apply_theme("finder_light"))

        theme_buttons_layout.addWidget(midnight_button, 0, 0)
        theme_buttons_layout.addWidget(ocean_button, 0, 1)
        theme_buttons_layout.addWidget(amber_button, 0, 2)
        theme_buttons_layout.addWidget(rose_button, 1, 0)
        theme_buttons_layout.addWidget(violet_button, 1, 1)
        theme_buttons_layout.addWidget(finder_light_button, 1, 2)

        self.theme_message_label = QLabel("Current theme: Light Mode")
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

        my_rules_help = QLabel("Create rules like pdf -> Documents, keyword rules like econ -> Economics, or nested folders like invoice -> Finance/Invoices.")
        my_rules_help.setObjectName("settingsHelp")

        rule_form_layout = QHBoxLayout()
        self.rule_type_input = QComboBox()
        self.rule_type_input.addItems(["Extension", "Keyword"])

        self.rule_match_input = QLineEdit()
        self.rule_match_input.setPlaceholderText("pdf or econ")

        self.rule_category_input = QLineEdit()
        self.rule_category_input.setPlaceholderText("Documents, Econ, or Finance/Invoices")

        self.rule_scope_input = QComboBox()
        self.rule_scope_input.addItems(["Everywhere", "This folder only"])

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
        rule_form_layout.addWidget(self.rule_scope_input)
        rule_form_layout.addWidget(self.add_rule_button)
        rule_form_layout.addWidget(self.remove_rule_button)
        rule_form_layout.addWidget(self.clear_rule_form_button)

        self.settings_message_label = QLabel("")
        self.settings_message_label.setObjectName("settingsMessage")

        self.settings_rules_table = QTreeWidget()
        self.settings_rules_table.setObjectName("settingsRulesTable")
        self.settings_rules_table.setColumnCount(4)
        self.settings_rules_table.setHeaderLabels(["Rule", "Match", "Folder", "Scope"])
        self.settings_rules_table.setRootIsDecorated(False)
        self.settings_rules_table.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_rules_table.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_rules_table.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.settings_rules_table.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_rules_table.itemClicked.connect(self.load_selected_rule_into_form)

        structure_title = QLabel("Arrangement Structure")
        structure_title.setObjectName("settingsSectionTitle")

        structure_help = QLabel("Choose whether arranged files go by rule only, year first, or rule first with year/month folders.")
        structure_help.setObjectName("settingsHelp")
        structure_help.setWordWrap(True)

        structure_layout = QHBoxLayout()
        self.arrangement_structure_input = QComboBox()
        self.arrangement_structure_input.addItems(["Rule Only", "Year > Rule", "Year > Month > Rule", "Rule > Year", "Rule > Year > Month"])
        self.arrangement_structure_input.setCurrentText(self.app_settings["arrangement_structure"])

        self.arrangement_date_source_input = QComboBox()
        self.arrangement_date_source_input.addItems(["Modified Date", "Created/Added Date"])
        self.arrangement_date_source_input.setCurrentText(self.app_settings["arrangement_date_source"])

        self.save_arrangement_settings_button = QPushButton("Save Arrangement Settings")
        self.save_arrangement_settings_button.setObjectName("primaryCommand")
        self.save_arrangement_settings_button.clicked.connect(self.save_arrangement_settings)

        structure_layout.addWidget(self.arrangement_structure_input)
        structure_layout.addWidget(self.arrangement_date_source_input)
        structure_layout.addWidget(self.save_arrangement_settings_button)

        my_rules_layout.addWidget(my_rules_title)
        my_rules_layout.addWidget(my_rules_help)
        my_rules_layout.addLayout(rule_form_layout)
        my_rules_layout.addWidget(self.settings_message_label)
        my_rules_layout.addWidget(self.settings_rules_table, 1)
        my_rules_layout.addWidget(structure_title)
        my_rules_layout.addWidget(structure_help)
        my_rules_layout.addLayout(structure_layout)

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
        self.back_from_history_button.clicked.connect(self.return_to_files)

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
        self.undo_selected_history_button.setObjectName("secondaryActionButton")
        self.undo_selected_history_button.setEnabled(False)
        self.undo_selected_history_button.clicked.connect(self.undo_selected_history_move)

        self.export_history_button = QPushButton("Export History")
        self.export_history_button.setObjectName("secondaryActionButton")
        self.export_history_button.clicked.connect(self.export_history)

        history_actions_layout.addWidget(self.open_history_item_button)
        history_actions_layout.addWidget(self.open_history_destination_button)
        history_actions_layout.addWidget(self.undo_selected_history_button)
        history_actions_layout.addWidget(self.export_history_button)
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
        self.history_table.itemSelectionChanged.connect(self.update_history_action_buttons)

        self.history_layout.addLayout(history_top_layout)
        self.history_layout.addWidget(self.history_help_label)
        self.history_layout.addLayout(history_actions_layout)
        self.history_layout.addWidget(self.history_table, 1)

        self.main_layout.addWidget(self.history_panel, 1)
        self.history_panel.hide()

    def select_folder(self, folder_name, folder_path, selected_button):
        self.clear_active_command_button()
        self.clear_active_sidebar_footer_button()
        self.clear_search_bar()
        self.state.selected_folder_name = folder_name
        self.state.selected_folder_path = os.path.expanduser(folder_path)
        self.state.current_view_folder_path = self.state.selected_folder_path
        self.folder_back_stack = []

        self.folder_name_label.setText(self.state.selected_folder_name)
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_contents_list(self.state.selected_folder_path)
        self.update_breadcrumb_controls()
        self.show_details_panel()

        self.set_active_folder_button(selected_button)

    def choose_folder(self):
        self.clear_active_command_button()
        start_folder = self.state.current_view_folder_path

        if not os.path.isdir(start_folder):
            start_folder = os.path.expanduser("~")

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Choose a folder",
            start_folder,
            QFileDialog.Option.ShowDirsOnly,
        )

        if folder_path == "":
            return

        self.select_custom_folder(folder_path)

    def select_custom_folder(self, folder_path):
        normalized_path = os.path.abspath(os.path.expanduser(folder_path))

        if not os.path.isdir(normalized_path):
            self.show_output("Open", ["Path is not a folder: " + normalized_path])
            return

        folder_button = self.folder_button_paths.get(normalized_path)

        if folder_button is None:
            self.custom_folders_title.show()
            folder_button = self.add_left_folder_button(normalized_path)

        self.select_folder(self.get_folder_display_name(normalized_path), normalized_path, folder_button)

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
        preview_plan = self.get_arrange_preview_plan(folder_path)
        self.state.current_preview = preview_plan
        self.set_arrange_preview_visible(True)
        self.preview_confirm_button.setEnabled(len(preview_plan["moves"]) > 0)
        self.populate_arrange_preview_table(preview_plan["moves"])
        self.populate_arrange_preview_summary(preview_plan)
        self.update_arrange_confirm_state()

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
        self.right_panel.show()
        self.output_title.show()
        self.output_title.setText(title)
        self.output_list.clear()
        self.summary_panel.hide()
        self.output_list.show()
        self.output_list.setColumnCount(1)
        self.output_list.setHeaderLabels(["Message"])
        self.output_list.setRootIsDecorated(False)
        self.output_list.header().hide()
        self.proceed_button.setVisible(show_proceed)
        self.cancel_preview_button.setVisible(False)
        self.open_selected_button.setVisible(True)

        for line in lines:
            list_item = QTreeWidgetItem([line.strip()])
            self.output_list.addTopLevelItem(list_item)

    def show_details_panel(self):
        self.right_panel.hide()
        self.output_title.hide()
        self.output_list.hide()
        self.summary_panel.hide()
        self.clear_layout(self.summary_layout)
        self.proceed_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        self.open_selected_button.setVisible(False)

    def show_help(self):
        self.clear_active_command_button()
        self.set_active_sidebar_footer_button(self.sidebar_help_button)
        self.clear_search_bar()

        if self.help_dialog is not None and self.help_dialog.isVisible():
            self.help_dialog.raise_()
            self.help_dialog.activateWindow()
            return

        self.help_dialog = QDialog(self)
        self.help_dialog.setWindowTitle("Neatify Help")
        self.help_dialog.setObjectName("previewDialog")
        self.help_dialog.resize(820, 680)
        self.help_dialog.setMinimumSize(680, 520)
        self.help_dialog.setModal(False)
        self.help_dialog.finished.connect(lambda result: self.clear_active_sidebar_footer_button())

        help_layout = QVBoxLayout()
        help_layout.setContentsMargins(22, 22, 22, 22)
        help_layout.setSpacing(12)
        self.help_dialog.setLayout(help_layout)

        title_label = QLabel("How to Use Neatify")
        title_label.setObjectName("previewDialogTitle")

        subtitle_label = QLabel("Keep this window open while you practice in the app.")
        subtitle_label.setObjectName("previewDialogPath")

        help_text = QTextEdit()
        help_text.setObjectName("helpText")
        help_text.setReadOnly(True)
        help_text.setHtml(self.get_help_html())

        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setObjectName("primaryCommand")
        close_button.clicked.connect(self.help_dialog.close)

        button_layout.addStretch()
        button_layout.addWidget(close_button)

        help_layout.addWidget(title_label)
        help_layout.addWidget(subtitle_label)
        help_layout.addWidget(help_text, 1)
        help_layout.addLayout(button_layout)

        self.help_dialog.show()

    def get_help_html(self):
        return """
        <h2>Basic workflow</h2>
        <ol>
            <li>Choose a folder from the left sidebar.</li>
            <li>Press <b>Arrange</b> to preview where files will go.</li>
            <li>Read the preview. Nothing moves yet.</li>
            <li>Press <b>Confirm Arrange</b> only when the preview looks right.</li>
            <li>Use <b>History</b> if you need to review, export, or undo a batch.</li>
        </ol>

        <h2>Preview files</h2>
        <p>Select a file in the list, then press <b>Space</b>. Neatify previews supported files in front of the app.</p>

        <h2>Search</h2>
        <p>Press <b>Find</b>, type what you want to find, then press Enter. Search settings can be changed in <b>Settings &gt; Search</b>.</p>

        <h2>Rules</h2>
        <p>Open <b>Settings &gt; My Rules</b> to teach Neatify where files should go.</p>
        <ul>
            <li><b>Extension rule:</b> <code>pdf</code> to <code>Documents</code></li>
            <li><b>Keyword rule:</b> <code>economics</code> to <code>Econ</code></li>
            <li><b>Nested folder:</b> <code>invoice</code> to <code>Finance/Invoices</code></li>
        </ul>

        <h2>Year and month sorting</h2>
        <p>In <b>Settings &gt; My Rules</b>, use <b>Arrangement Structure</b> to choose rule-only sorting, year-first sorting, or year/month folders.</p>

        <h2>Safety</h2>
        <ul>
            <li>Neatify previews before moving files.</li>
            <li>It renames duplicates instead of overwriting them.</li>
            <li>It records history for each arrange batch.</li>
            <li>You can undo previous arrange batches from History.</li>
        </ul>
        """

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
        self.update_folder_contents_list(self.state.current_view_folder_path)

    def open_from_command(self, item_name):
        if item_name == "":
            self.choose_folder()
            return

        expanded_path = os.path.expanduser(item_name)

        if os.path.exists(expanded_path):
            if os.path.isdir(expanded_path):
                self.select_custom_folder(expanded_path)
                return

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
            if os.path.isdir(results[0]):
                self.select_custom_folder(results[0])
                return

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
            "finder_light": {
                "name": "Light Mode",
                "main_background": "#F5F5F7",
                "app_background": "#F5F5F7",
                "panel_background": "#FFFFFF",
                "left_panel": "#F1F2F4",
                "right_panel": "#FFFFFF",
                "input_background": "#FFFFFF",
                "button_background": "#FFFFFF",
                "hover_background": "#E9EAED",
                "selected_background": "#DDE3EC",
                "border": "#C9CDD3",
                "soft_border": "#E3E5E8",
                "text": "#1D1D1F",
                "muted_text": "#5F6368",
                "quiet_text": "#7C828A",
                "accent": "#0A84FF",
                "accent_hover": "#339CFF",
                "accent_text": "#FFFFFF",
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
            "#20242B": theme["button_background"],
            "#2A2B29": theme["hover_background"],
            "#252624": theme["hover_background"],
            "#3B3C38": theme["selected_background"],
            "#2C3340": theme["selected_background"],
            "#40413F": theme["border"],
            "#313330": theme["soft_border"],
            "#30312F": theme["soft_border"],
            "#2C2D2B": theme["soft_border"],
            "#30343B": theme["soft_border"],
            "rgba(60, 72, 88, 0.55)": theme["soft_border"],
            "#F6F3ED": theme["text"],
            "#FFFFFF": theme["text"],
            "#D8D5CD": theme["text"],
            "#DCE3EF": theme["text"],
            "#E8EDF7": theme["text"],
            "#AAA9A1": theme["muted_text"],
            "#979890": theme["muted_text"],
            "#AEB4BF": theme["muted_text"],
            "#B8C0CE": theme["muted_text"],
            "#8E9088": theme["quiet_text"],
            "#8D95A3": theme["quiet_text"],
            "#8F98A8": theme["quiet_text"],
            "#9098A6": theme["quiet_text"],
            "#6F7784": theme["quiet_text"],
            "#29D85F": theme["accent"],
            "#34E96C": theme["accent_hover"],
            "#19E241": theme["accent"],
            "#07150B": theme["accent_text"],
            "#08290D": theme["input_background"],
            "#222321": theme["hover_background"],
            "#343841": theme["selected_background"],
        }

        color_pattern = re.compile("|".join(re.escape(color) for color in color_replacements))
        theme_style = color_pattern.sub(lambda match: color_replacements[match.group(0)], theme_style)

        return theme_style

    def add_rule_from_form(self):
        rule_type = self.rule_type_input.currentText()
        match_text = self.rule_match_input.text().strip()
        category = self.rule_category_input.text().strip()
        scope = ""

        if rule_type == "Keyword" and self.rule_scope_input.currentText() == "This folder only":
            scope = self.state.selected_folder_path

        if match_text == "" or category == "":
            self.settings_message_label.setText("Type both a match and a folder name.")
            return

        if self.editing_rule_type is not None:
            if self.editing_rule_type == "Extension":
                remove_extension_rule(self.editing_rule_match)
            elif self.editing_rule_type == "Keyword":
                remove_keyword_rule(self.editing_rule_match, self.editing_rule_scope)

        if rule_type == "Extension":
            add_extension_rule(match_text, category)
            self.settings_message_label.setText("Saved extension rule: " + match_text + " -> " + category)
        else:
            add_keyword_rule(match_text, category, scope)
            scope_text = "everywhere"

            if scope != "":
                scope_text = self.get_folder_display_name(scope)

            self.settings_message_label.setText("Saved keyword rule: " + match_text + " -> " + category + " (" + scope_text + ")")

        self.clear_rule_form()
        self.populate_settings_table()
        self.refresh_after_rules_change()

    def load_selected_rule_into_form(self, selected_rule, column=0):
        rule_type = selected_rule.text(0)
        match_text = selected_rule.text(1)
        category = selected_rule.text(2)
        scope_text = selected_rule.text(3)
        scope_path = selected_rule.data(0, Qt.UserRole)

        self.rule_type_input.setCurrentText(rule_type)
        self.rule_match_input.setText(match_text)
        self.rule_category_input.setText(category)
        self.rule_scope_input.setCurrentText("Everywhere" if scope_path in [None, ""] else "This folder only")
        self.editing_rule_type = rule_type
        self.editing_rule_match = match_text
        self.editing_rule_scope = scope_path
        self.add_rule_button.setText("Save Rule")
        self.settings_message_label.setText("Editing rule: " + match_text + " (" + scope_text + ")")

    def clear_rule_form(self):
        self.rule_match_input.clear()
        self.rule_category_input.clear()
        self.rule_scope_input.setCurrentText("Everywhere")
        self.editing_rule_type = None
        self.editing_rule_match = None
        self.editing_rule_scope = None
        self.add_rule_button.setText("Add Rule")

    def remove_selected_rule(self):
        selected_items = self.settings_rules_table.selectedItems()

        if len(selected_items) == 0:
            self.settings_message_label.setText("Select a rule first.")
            return

        selected_rule = selected_items[0]
        rule_type = selected_rule.text(0)
        match_text = selected_rule.text(1)
        scope_path = selected_rule.data(0, Qt.UserRole)

        if rule_type == "Extension":
            remove_extension_rule(match_text)
        elif rule_type == "Keyword":
            remove_keyword_rule(match_text, scope_path)

        self.settings_message_label.setText("Removed rule: " + match_text)
        self.clear_rule_form()
        self.populate_settings_table()
        self.refresh_after_rules_change()

    def save_search_settings(self):
        self.app_settings["search_type"] = self.search_type_input.currentText()
        self.app_settings["include_subfolders"] = self.include_subfolders_checkbox.isChecked()
        save_app_settings(self.app_settings)
        self.search_message_label.setText("Search settings saved.")

    def save_arrangement_settings(self):
        self.app_settings["arrangement_structure"] = self.arrangement_structure_input.currentText()
        self.app_settings["arrangement_date_source"] = self.arrangement_date_source_input.currentText()
        save_app_settings(self.app_settings)
        self.settings_message_label.setText("Arrangement settings saved.")

    def show_settings(self):
        self.clear_active_command_button()
        self.clear_active_folder_button()
        self.set_active_sidebar_footer_button(self.sidebar_settings_button)
        self.hide_browser_panels()
        self.history_panel.hide()
        self.settings_panel.show()
        self.populate_settings_table()
        self.show_settings_page(0)
        self.rule_match_input.setFocus()

    def return_to_files(self):
        self.clear_active_command_button()
        self.clear_active_sidebar_footer_button()
        self.restore_active_folder_button()
        self.clear_search_bar()
        self.show_browser_view()

    def show_browser_view(self):
        self.settings_panel.hide()
        self.history_panel.hide()
        self.ask_input.show()
        self.left_panel.show()
        self.center_panel.show()
        self.show_details_panel()

    def clear_search_bar(self):
        self.ask_input.clear()
        self.ask_input.setPlaceholderText("Ask Neatify: show me all PDFs in this folder...")

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
            list_item = QTreeWidgetItem(["Extension", extension, category, "Everywhere"])
            list_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            list_item.setData(0, Qt.UserRole, "")
            self.settings_rules_table.addTopLevelItem(list_item)

        for rule in sorted(rules["keyword_rules"], key=lambda item: (item.get("keyword", ""), item.get("scope", ""))):
            keyword = rule.get("keyword", "")
            category = rule.get("destination", "")
            scope_path = rule.get("scope", "")
            scope_text = "Everywhere"

            if scope_path != "":
                scope_text = self.get_folder_display_name(scope_path)

            list_item = QTreeWidgetItem(["Keyword", keyword, category, scope_text])
            list_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
            list_item.setData(0, Qt.UserRole, scope_path)
            self.settings_rules_table.addTopLevelItem(list_item)

    def process_settings_command(self):
        self.add_rule_from_form()

    def open_output_item(self, item, column=0):
        item_path = item.data(0, Qt.UserRole)

        if item_path is None:
            return

        if os.path.isdir(item_path):
            self.select_center_folder(item_path, None)
            return

        self.preview_item(item_path)

    def open_browser_item(self, item, column=0):
        item_path = item.data(0, Qt.UserRole)

        if item_path is None:
            return

        if os.path.isdir(item_path):
            self.select_center_folder(item_path, None)
            return

        self.preview_item(item_path)

    def handle_browser_item_clicked(self, item, column=0):
        item_path = item.data(0, Qt.UserRole)

        if item_path is None:
            return

        if os.path.isdir(item_path):
            self.select_center_folder(item_path, None)

    def open_selected_item(self):
        item = self.get_selected_path_item()

        if item is None:
            self.show_output("Open Selected", ["Select a file or search result first."])
            return

        item_path = item.data(0, Qt.UserRole)
        open_item(item_path)
        self.show_output("Open", ["Opened: " + item_path])

    def get_selected_path_item(self):
        focused_widget = self.focusWidget()
        focused_item = self.get_selected_item_from_widget(focused_widget)

        if focused_item is not None:
            return focused_item

        if self.preview_table.isVisible():
            preview_item = self.get_selected_item_from_widget(self.preview_table)

            if preview_item is not None:
                return preview_item

        if self.folder_contents_list.isVisible():
            folder_item = self.get_selected_item_from_widget(self.folder_contents_list)

            if folder_item is not None:
                return folder_item

        if self.output_list.isVisible():
            output_item = self.get_selected_item_from_widget(self.output_list)

            if output_item is not None:
                return output_item

        return None

    def get_selected_item_from_widget(self, widget):
        if widget not in [self.output_list, self.preview_table, self.folder_contents_list]:
            return None

        selected_items = widget.selectedItems()

        if len(selected_items) == 0:
            return None

        item = selected_items[0]
        item_path = item.data(0, Qt.UserRole)

        if item_path is None:
            return None

        return item

    def show_path_results(self, title, paths):
        self.right_panel.show()
        self.output_title.show()
        self.output_title.setText(title)
        self.output_list.clear()
        self.summary_panel.hide()
        self.output_list.show()
        self.output_list.setColumnCount(2)
        self.output_list.setHeaderLabels(["Name", "Location"])
        self.output_list.setRootIsDecorated(False)
        self.output_list.header().show()
        self.output_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.output_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proceed_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        self.open_selected_button.setVisible(True)

        for item_path in paths:
            item_name = os.path.basename(item_path)
            parent_folder = os.path.dirname(item_path)
            list_item = QTreeWidgetItem([item_name, parent_folder])
            list_item.setIcon(0, self.get_path_icon(item_path))
            list_item.setData(0, Qt.UserRole, item_path)
            self.output_list.addTopLevelItem(list_item)

    def organize_selected_folder(self):
        checked_moves = self.get_checked_arrange_moves()

        if len(checked_moves) == 0:
            self.preview_confirm_button.setEnabled(False)
            self.preview_help_label.setText("Choose at least one file to arrange")
            return

        folder_path = self.state.current_arrange_folder_path
        batch_id = create_move_id()
        moved_count = 0
        errors = []

        for move in checked_moves:
            old_path = move["old_path"]
            new_path = move["new_path"]

            if not os.path.exists(old_path):
                errors.append("Missing: " + old_path)
                continue

            destination_folder = os.path.dirname(new_path)

            try:
                os.makedirs(destination_folder, exist_ok=True)
                safe_destination = get_unique_destination(new_path)
                move_file(old_path, safe_destination, dry_run=False, move_id=batch_id)
                moved_count = moved_count + 1
            except OSError as error:
                errors.append(os.path.basename(old_path) + ": " + str(error))

        self.state.current_arrange_folder_path = ""
        self.state.current_preview = {}
        self.set_arrange_preview_visible(False)
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_contents_list(self.state.current_view_folder_path)

        lines = [
            "Organized: " + folder_path,
            "Moved files: " + str(moved_count),
        ]

        if len(errors) > 0:
            lines.append("Some files could not be moved:")
            lines.extend(errors[:8])

            if len(errors) > 8:
                lines.append("+" + str(len(errors) - 8) + " more errors")

        self.show_output("Done", lines)

    def cancel_preview(self):
        self.state.current_preview = {}
        self.set_arrange_preview_visible(False)
        self.proceed_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        self.show_output("Output", ["Preview cancelled."])

    def show_history(self):
        self.set_active_command_button(self.history_button)
        self.clear_active_sidebar_footer_button()
        self.restore_active_folder_button()
        self.hide_browser_panels()
        self.settings_panel.hide()
        self.history_title.setText("History")
        self.history_help_label.setText("Recent move and undo operations.")
        self.history_panel.show()
        self.populate_history_table()

    def show_undo_page(self):
        self.set_active_command_button(self.undo_button)
        self.clear_active_sidebar_footer_button()
        self.restore_active_folder_button()
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
            self.update_history_action_buttons()
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

        self.update_history_action_buttons()

    def update_history_action_buttons(self):
        selected_item = self.get_selected_history_item()
        selected_batches = self.get_selected_history_batches()
        has_selection = selected_item is not None
        has_active_undo = any(not batch["undone"] for batch in selected_batches)

        self.open_history_item_button.setEnabled(has_selection)
        self.open_history_destination_button.setEnabled(has_selection)
        self.undo_selected_history_button.setEnabled(has_active_undo)

        if has_active_undo:
            self.undo_selected_history_button.setObjectName("primaryCommand")
        else:
            self.undo_selected_history_button.setObjectName("secondaryActionButton")

        self.refresh_style(self.open_history_item_button)
        self.refresh_style(self.open_history_destination_button)
        self.refresh_style(self.undo_selected_history_button)

    def get_history_batches(self):
        history_path = get_history_path()

        if not os.path.exists(history_path):
            return []

        with open(history_path, "r", encoding="utf-8") as history_file:
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

        active_batches = [batch for batch in selected_batches if not batch["undone"]]

        if len(active_batches) == 0:
            self.history_help_label.setText("Selected batches are already undone.")
            return

        if not self.show_undo_preview_dialog(active_batches):
            self.history_help_label.setText("Undo cancelled.")
            return

        undone_count = 0
        messages = []

        for batch in active_batches:
            result = undo_move_by_id(batch["move_id"])
            messages.append(result)

            if result.startswith("Undone"):
                undone_count = undone_count + 1

        self.populate_history_table()
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_contents_list(self.state.current_view_folder_path)

        if undone_count == 1:
            self.history_help_label.setText(messages[0])
        else:
            self.history_help_label.setText("Undone " + str(undone_count) + " selected batches.")

    def undo_last_gui_move(self):
        active_batch = self.get_last_active_history_batch()

        if active_batch is None:
            self.show_output("Undo", ["No move history found."])
            return

        if not self.show_undo_preview_dialog([active_batch]):
            self.show_output("Undo", ["Undo cancelled."])
            return

        result = undo_move_by_id(active_batch["move_id"])
        self.folder_summary_label.setText(self.get_folder_status(self.state.selected_folder_path))
        self.update_folder_contents_list(self.state.current_view_folder_path)
        self.show_output("Undo", [result])

    def get_last_active_history_batch(self):
        for batch in self.get_history_batches():
            if not batch["undone"]:
                return batch

        return None

    def show_undo_preview_dialog(self, batches):
        undo_moves = self.get_undo_preview_moves(batches)

        if len(undo_moves) == 0:
            return False

        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Undo Preview")
        preview_dialog.setObjectName("previewDialog")
        preview_dialog.resize(980, 680)
        preview_dialog.setMinimumSize(820, 560)

        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(22, 22, 22, 22)
        preview_layout.setSpacing(12)
        preview_dialog.setLayout(preview_layout)

        title_label = QLabel("Undo Preview")
        title_label.setObjectName("arrangePreviewTitle")

        help_label = QLabel("Review every file before Neatify moves it back")
        help_label.setObjectName("arrangePreviewHelp")

        warning_label = QLabel("Preview only. Files move back only after you confirm.")
        warning_label.setObjectName("arrangePreviewWarning")

        undo_table = QTreeWidget()
        undo_table.setObjectName("arrangePreviewTable")
        undo_table.setColumnCount(5)
        undo_table.setHeaderLabels(["File name", "Current location", "", "Restore to", "Status"])
        undo_table.setRootIsDecorated(False)
        undo_table.setWordWrap(True)
        undo_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        undo_table.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        undo_table.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        undo_table.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        undo_table.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        undo_table.header().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        undo_table.setColumnWidth(1, 330)
        undo_table.setColumnWidth(3, 330)

        for move in undo_moves:
            list_item = QTreeWidgetItem([
                move["file_name"],
                move["current_path"],
                "→",
                move["restore_path"],
                "Restore",
            ])
            list_item.setIcon(0, self.get_file_icon(move["file_name"]))
            list_item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)
            list_item.setToolTip(1, move["current_path"])
            list_item.setToolTip(3, move["restore_path"])
            undo_table.addTopLevelItem(list_item)

        action_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("dangerActionButton")
        cancel_button.clicked.connect(preview_dialog.reject)

        confirm_button = QPushButton("Confirm Undo (" + str(len(undo_moves)) + ")")
        confirm_button.setObjectName("confirmArrangeButton")
        confirm_button.clicked.connect(preview_dialog.accept)

        action_layout.addWidget(cancel_button)
        action_layout.addStretch()
        action_layout.addWidget(confirm_button)

        preview_layout.addWidget(title_label)
        preview_layout.addWidget(help_label)
        preview_layout.addWidget(warning_label)
        preview_layout.addWidget(undo_table, 1)
        preview_layout.addLayout(action_layout)

        return preview_dialog.exec() == QDialog.DialogCode.Accepted

    def get_undo_preview_moves(self, batches):
        undo_moves = []

        for batch in batches:
            for move in batch["moves"]:
                undo_moves.append({
                    "file_name": move["item"],
                    "current_path": move["new_path"],
                    "restore_path": move["old_path"],
                })

        return undo_moves

    def export_history(self):
        batches = self.get_history_batches()

        if len(batches) == 0:
            self.history_help_label.setText("No history to export yet.")
            return

        default_name = "neatify-history-" + datetime.now().strftime("%Y-%m-%d") + ".csv"
        export_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export history",
            default_name,
            "CSV files (*.csv);;Text files (*.txt)",
        )

        if export_path == "":
            self.history_help_label.setText("Export cancelled.")
            return

        try:
            if selected_filter.startswith("Text") or export_path.lower().endswith(".txt"):
                self.write_history_text_export(export_path, batches)
            else:
                if not export_path.lower().endswith(".csv"):
                    export_path = export_path + ".csv"

                self.write_history_csv_export(export_path, batches)
        except OSError as error:
            self.history_help_label.setText("Could not export history: " + str(error))
            return

        self.history_help_label.setText("Exported history: " + export_path)

    def write_history_csv_export(self, export_path, batches):
        with open(export_path, "w", newline="", encoding="utf-8") as export_file:
            writer = csv.writer(export_file)
            writer.writerow(["Batch ID", "Time", "Batch status", "Action", "Item", "From", "To", "Original path", "New path"])

            for batch in batches:
                batch_status = "Undone" if batch["undone"] else "Active"

                for move in batch["moves"]:
                    writer.writerow([
                        batch["move_id"],
                        move["time"],
                        batch_status,
                        move["action"],
                        move["item"],
                        move["from"],
                        move["to"],
                        move["old_path"],
                        move["new_path"],
                    ])

    def write_history_text_export(self, export_path, batches):
        with open(export_path, "w", encoding="utf-8") as export_file:
            export_file.write("Neatify History Export\n")
            export_file.write("Created: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")

            for batch in batches:
                batch_status = "Undone" if batch["undone"] else "Active"
                export_file.write(batch["time"] + " | " + batch["move_id"] + " | " + batch_status + "\n")

                for move in batch["moves"]:
                    export_file.write("  - " + move["item"] + "\n")
                    export_file.write("    From: " + move["old_path"] + "\n")
                    export_file.write("    To:   " + move["new_path"] + "\n")

                export_file.write("\n")

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

    def select_center_folder(self, folder_path, selected_button):
        current_path = self.state.current_view_folder_path

        if current_path != folder_path:
            self.folder_back_stack.append(current_path)

        self.navigate_to_folder(folder_path)

    def navigate_to_folder(self, folder_path):
        self.state.current_view_folder_path = folder_path
        self.folder_name_label.setText(self.get_folder_display_name(folder_path))
        self.folder_summary_label.setText(self.get_folder_status(folder_path))
        self.output_list.clearSelection()
        self.preview_table.clearSelection()
        self.update_folder_contents_list(folder_path)
        self.update_breadcrumb_controls()
        self.show_details_panel()

    def go_to_selected_root_folder(self):
        if self.state.current_view_folder_path == self.state.selected_folder_path:
            return

        self.folder_back_stack.append(self.state.current_view_folder_path)
        self.navigate_to_folder(self.state.selected_folder_path)

    def go_back_folder(self):
        if len(self.folder_back_stack) == 0:
            return

        previous_folder = self.folder_back_stack.pop()
        self.navigate_to_folder(previous_folder)

    def update_breadcrumb_controls(self):
        selected_path = self.state.selected_folder_path
        current_path = self.state.current_view_folder_path

        self.breadcrumb_root_button.setText(self.state.selected_folder_name)

        if current_path == selected_path:
            self.breadcrumb_separator_label.hide()
            self.breadcrumb_current_label.hide()
        else:
            self.breadcrumb_separator_label.show()
            self.breadcrumb_current_label.show()
            self.breadcrumb_current_label.setText(self.get_folder_display_name(current_path))

        self.back_button.setEnabled(len(self.folder_back_stack) > 0)

    def update_folder_contents_list(self, folder_path):
        self.folder_contents_list.clear()
        self.folders_title_label.setText("Contents")

        folder_name = os.path.basename(folder_path)

        if folder_name != "":
            self.folders_title_label.setText("Contents in " + folder_name)

        if not os.path.exists(folder_path):
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["Folder not found", "", "", ""]))
            return

        if not os.path.isdir(folder_path):
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["Path is not a folder", "", "", ""]))
            return

        try:
            folder_items = sorted(os.listdir(folder_path), key=str.lower)
        except PermissionError:
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["Neatify does not have permission to read this folder", "", "", ""]))
            return
        except OSError as error:
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["Could not read folder: " + str(error), "", "", ""]))
            return

        for item in folder_items:
            full_path = os.path.join(folder_path, item)

            if os.path.isdir(full_path):
                list_item = QTreeWidgetItem([
                    item,
                    "Folder",
                    "-",
                    self.get_modified_text(full_path),
                ])
                list_item.setIcon(0, self.get_folder_icon())
                list_item.setData(0, Qt.UserRole, full_path)
                self.folder_contents_list.addTopLevelItem(list_item)
            elif os.path.isfile(full_path):
                list_item = QTreeWidgetItem([
                    item,
                    self.get_file_kind_text(item),
                    self.get_file_size_text(full_path),
                    self.get_modified_text(full_path),
                ])
                list_item.setIcon(0, self.get_file_icon(item))
                list_item.setData(0, Qt.UserRole, full_path)
                self.folder_contents_list.addTopLevelItem(list_item)

        if self.folder_contents_list.topLevelItemCount() == 0:
            self.folder_contents_list.addTopLevelItem(QTreeWidgetItem(["No items found", "", "", ""]))

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Space:
            if watched == self.folder_contents_list or watched == self.output_list or watched == self.preview_table:
                self.preview_selected_item()
                return True

        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            focused_widget = self.focusWidget()

            if isinstance(focused_widget, (QLineEdit, QTextEdit)):
                super().keyPressEvent(event)
                return

            item = self.get_selected_path_item()

            if item is not None:
                self.preview_selected_item()
                return

        super().keyPressEvent(event)

    def preview_selected_item(self):
        item = self.get_selected_path_item()

        if item is None:
            self.show_output("Preview", ["Select a file first."])
            return

        item_path = item.data(0, Qt.UserRole)

        if item_path is None:
            self.show_output("Preview", ["Select a file first."])
            return

        if os.path.isdir(item_path):
            self.select_center_folder(item_path, None)
            return

        self.preview_item(item_path)

    def preview_item(self, item_path):
        if not os.path.exists(item_path):
            self.show_output("Preview", ["File not found: " + item_path])
            return

        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Preview - " + os.path.basename(item_path))
        preview_dialog.setObjectName("previewDialog")
        preview_dialog.resize(980, 720)
        preview_dialog.setMinimumSize(820, 600)

        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(22, 22, 22, 22)
        preview_layout.setSpacing(12)
        preview_dialog.setLayout(preview_layout)

        title_label = QLabel(os.path.basename(item_path))
        title_label.setObjectName("previewDialogTitle")

        path_label = QLabel(item_path)
        path_label.setObjectName("previewDialogPath")
        path_label.setWordWrap(True)

        preview_layout.addWidget(title_label)
        preview_layout.addWidget(path_label)

        extension = os.path.splitext(item_path)[1].lower()

        if extension in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]:
            image_label = QLabel("")
            image_label.setObjectName("previewImage")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            pixmap = QPixmap(item_path)

            if pixmap.isNull():
                image_label.setText("This image could not be previewed.")
            else:
                image_label.setPixmap(pixmap.scaled(
                    QSize(920, 540),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))

            preview_layout.addWidget(image_label, 1)
        elif extension == ".pdf":
            if QPdfDocument is None or QPdfView is None:
                error_label = QLabel("PDF preview is not available in this PySide6 install.")
                error_label.setObjectName("previewUnsupported")
                error_label.setWordWrap(True)
                preview_layout.addWidget(error_label, 1)
            else:
                pdf_document = QPdfDocument(preview_dialog)
                load_error = pdf_document.load(item_path)

                if load_error == QPdfDocument.Error.None_:
                    pdf_view = QPdfView()
                    pdf_view.setObjectName("previewPdf")
                    pdf_view.setDocument(pdf_document)
                    pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
                    pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
                    pdf_view.setPageSpacing(8)
                    preview_dialog.pdf_document = pdf_document
                    preview_layout.addWidget(pdf_view, 1)
                else:
                    error_label = QLabel("This PDF could not be previewed inside Neatify.")
                    error_label.setObjectName("previewUnsupported")
                    error_label.setWordWrap(True)
                    preview_layout.addWidget(error_label, 1)
        elif extension in [".txt", ".md", ".csv", ".py", ".js", ".html", ".css", ".json", ".xml", ".log"]:
            text_preview = QTextEdit()
            text_preview.setObjectName("previewText")
            text_preview.setReadOnly(True)
            text_preview.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

            try:
                with open(item_path, "r", encoding="utf-8") as preview_file:
                    text_preview.setPlainText(preview_file.read(200000))
            except UnicodeDecodeError:
                try:
                    with open(item_path, "r", encoding="latin-1") as preview_file:
                        text_preview.setPlainText(preview_file.read(200000))
                except OSError as error:
                    text_preview.setPlainText("Could not read this file: " + str(error))
            except OSError as error:
                text_preview.setPlainText("Could not read this file: " + str(error))

            preview_layout.addWidget(text_preview, 1)
        else:
            details_label = QLabel(
                "Neatify cannot preview this file type inside the app yet.\n\n"
                + "Kind: " + self.get_file_kind_text(os.path.basename(item_path)) + "\n"
                + "Size: " + self.get_file_size_text(item_path) + "\n"
                + "Modified: " + self.get_modified_text(item_path)
            )
            details_label.setObjectName("previewUnsupported")
            details_label.setWordWrap(True)
            preview_layout.addWidget(details_label, 1)

        button_layout = QHBoxLayout()
        open_button = QPushButton("Open")
        open_button.setObjectName("secondaryActionButton")
        open_button.clicked.connect(lambda: open_item(item_path))

        close_button = QPushButton("Close")
        close_button.setObjectName("primaryCommand")
        close_button.clicked.connect(preview_dialog.accept)

        button_layout.addWidget(open_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        preview_layout.addLayout(button_layout)

        preview_dialog.exec()

    def set_arrange_preview_visible(self, visible):
        browser_widgets = [
            self.folder_name_label,
            self.breadcrumb_root_button,
            self.breadcrumb_separator_label,
            self.breadcrumb_current_label,
            self.back_button,
            self.folder_summary_label,
            self.folders_title_label,
            self.folder_contents_list,
        ]

        preview_widgets = [
            self.preview_title_label,
            self.preview_help_label,
            self.preview_warning_label,
            self.preview_table,
            self.preview_cancel_button,
            self.preview_confirm_button,
        ]

        for widget in browser_widgets:
            widget.setVisible(not visible)

        for widget in preview_widgets:
            widget.setVisible(visible)

        if not visible:
            self.preview_confirm_button.setText("Confirm Arrange")
            self.preview_help_label.setText("Review every file before anything moves")
            self.update_breadcrumb_controls()

    def get_arrange_preview_plan(self, folder_path):
        moves = []
        destination_counts = {}
        skipped_count = 0

        try:
            folder_items = sorted(os.listdir(folder_path), key=str.lower)
        except PermissionError:
            return {
                "folder_path": folder_path,
                "moves": moves,
                "destination_counts": destination_counts,
                "duplicate_count": 0,
                "skipped_count": 1,
            }
        except OSError:
            return {
                "folder_path": folder_path,
                "moves": moves,
                "destination_counts": destination_counts,
                "duplicate_count": 0,
                "skipped_count": 1,
            }

        for item in folder_items:
            full_path = os.path.join(folder_path, item)

            if item[:1] == ".":
                skipped_count = skipped_count + 1
                continue

            if not os.path.isfile(full_path):
                skipped_count = skipped_count + 1
                continue

            arrangement = get_arrangement_for_file(item, folder_path)
            category = arrangement["destination"]
            destination_folder = self.build_arrange_destination_folder(folder_path, category, full_path)
            destination = os.path.join(destination_folder, item)
            unique_destination = get_unique_destination(destination)
            destination_name = os.path.basename(unique_destination)
            status = "Move"

            if destination_name != item:
                status = "Duplicate renamed"

            moves.append({
                "file_name": item,
                "old_path": full_path,
                "new_path": unique_destination,
                "category": category,
                "rule_reason": arrangement["reason"],
                "status": status,
            })

            destination_counts[category] = destination_counts.get(category, 0) + 1

        return {
            "folder_path": folder_path,
            "moves": moves,
            "destination_counts": destination_counts,
            "duplicate_count": sum(1 for move in moves if move["status"] == "Duplicate renamed"),
            "skipped_count": skipped_count,
        }

    def populate_arrange_preview_table(self, moves):
        self.preview_table.blockSignals(True)
        self.preview_table.clear()

        if len(moves) == 0:
            self.preview_table.addTopLevelItem(QTreeWidgetItem(["", "No files ready to move", "", "", "", ""]))
            self.preview_table.blockSignals(False)
            return

        for move in moves:
            list_item = QTreeWidgetItem([
                "",
                move["file_name"],
                self.format_preview_path(move["old_path"]),
                "→",
                self.format_preview_path(move["new_path"]),
                "",
            ])
            list_item.setCheckState(0, Qt.CheckState.Checked)
            list_item.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)
            list_item.setIcon(1, self.get_file_icon(move["file_name"]))
            list_item.setData(0, Qt.UserRole, move["old_path"])
            list_item.setData(0, Qt.UserRole + 1, move)
            list_item.setData(1, Qt.UserRole, move["old_path"])
            list_item.setToolTip(1, move["file_name"])
            list_item.setToolTip(2, move["old_path"])
            list_item.setToolTip(4, move["new_path"])
            list_item.setToolTip(5, move["rule_reason"])
            self.preview_table.addTopLevelItem(list_item)

            status_badge = QLabel(move["status"])

            if move["status"] == "Duplicate renamed":
                status_badge.setObjectName("duplicateStatusBadge")
            else:
                status_badge.setObjectName("moveStatusBadge")

            status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.preview_table.setItemWidget(list_item, 5, status_badge)

        self.preview_table.blockSignals(False)

    def get_checked_arrange_moves(self):
        checked_moves = []

        for index in range(self.preview_table.topLevelItemCount()):
            item = self.preview_table.topLevelItem(index)

            if item.checkState(0) != Qt.CheckState.Checked:
                continue

            move = item.data(0, Qt.UserRole + 1)

            if move is not None:
                checked_moves.append(move)

        return checked_moves

    def update_arrange_confirm_state(self, item=None, column=0):
        checked_count = len(self.get_checked_arrange_moves())
        self.preview_confirm_button.setEnabled(checked_count > 0)

        if checked_count == 0:
            self.preview_confirm_button.setText("Confirm Arrange")
            return

        self.preview_confirm_button.setText("Confirm Arrange (" + str(checked_count) + ")")

    def format_preview_path(self, item_path):
        return item_path

    def build_arrange_destination_folder(self, base_folder, rule_destination, file_path):
        date_parts = self.get_arrangement_date_parts(file_path)
        clean_destination = rule_destination
        structure = self.app_settings["arrangement_structure"]

        if structure == "Rule Only":
            parts = [clean_destination]
        elif structure == "Year > Rule":
            parts = [date_parts["year"], clean_destination]
        elif structure == "Year > Month > Rule":
            parts = [date_parts["year"], date_parts["month"], clean_destination]
        elif structure == "Rule > Year":
            parts = [clean_destination, date_parts["year"]]
        elif structure == "Rule > Year > Month":
            parts = [clean_destination, date_parts["year"], date_parts["month"]]
        else:
            parts = [clean_destination]

        destination_folder = base_folder

        for part in parts:
            for clean_part in str(part).replace("\\", "/").split("/"):
                if clean_part.strip() in ["", ".", ".."]:
                    continue

                destination_folder = os.path.join(destination_folder, clean_part.strip())

        return destination_folder

    def get_arrangement_date_parts(self, file_path):
        date_source = self.app_settings["arrangement_date_source"]

        try:
            if date_source == "Created/Added Date":
                timestamp = os.path.getctime(file_path)
            else:
                timestamp = os.path.getmtime(file_path)
        except OSError:
            timestamp = datetime.now().timestamp()

        file_date = datetime.fromtimestamp(timestamp)

        return {
            "year": file_date.strftime("%Y"),
            "month": file_date.strftime("%B"),
        }

    def populate_arrange_preview_summary(self, preview_plan):
        self.right_panel.show()
        self.output_title.hide()
        self.output_list.hide()
        self.summary_panel.show()
        self.clear_layout(self.summary_layout)
        self.proceed_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        self.open_selected_button.setVisible(False)

        self.summary_layout.addWidget(self.create_summary_title("Summary"))
        self.summary_layout.addWidget(self.create_summary_metric_row(str(len(preview_plan["moves"])) + " files ready", "file"))
        self.summary_layout.addWidget(self.create_summary_metric_row(str(preview_plan["duplicate_count"]) + " duplicates renamed", "duplicate"))
        self.summary_layout.addWidget(self.create_summary_metric_row(str(preview_plan["skipped_count"]) + " skipped", "skipped"))
        self.add_summary_divider()

        self.summary_layout.addWidget(self.create_summary_section_header("Destination folders"))

        for category in sorted(preview_plan["destination_counts"]):
            count = preview_plan["destination_counts"][category]
            file_word = "file"

            if count != 1:
                file_word = "files"

            self.summary_layout.addWidget(self.create_summary_row(category, str(count) + " " + file_word, category))

        if len(preview_plan["destination_counts"]) == 0:
            self.summary_layout.addWidget(self.create_summary_note("No destination folders yet."))

    def add_summary_divider(self):
        divider = QLabel("")
        divider.setObjectName("summaryDivider")
        self.summary_layout.addWidget(divider)

    def create_summary_title(self, title_text):
        title_label = QLabel(title_text)
        title_label.setObjectName("summaryCardTitle")
        title_label.setFixedHeight(32)

        return title_label

    def create_summary_metric_row(self, text, icon_name="file"):
        row_widget = QWidget()
        row_widget.setObjectName("summaryMetricRow")
        row_widget.setFixedHeight(38)
        row_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.setSpacing(12)
        row_widget.setLayout(row_layout)

        icon_label = QLabel("")
        icon_label.setObjectName("summaryIcon")
        icon_label.setFixedSize(28, 28)
        icon_label.setPixmap(self.get_summary_icon(icon_name).pixmap(24, 24))

        text_label = QLabel(text)
        text_label.setObjectName("summaryMetricText")

        row_layout.addWidget(icon_label)
        row_layout.addWidget(text_label)
        row_layout.addStretch()

        return row_widget

    def create_summary_section_header(self, text):
        row_widget = QWidget()
        row_widget.setObjectName("summarySectionRow")
        row_widget.setFixedHeight(36)
        row_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(12)
        row_widget.setLayout(row_layout)

        icon_label = QLabel("")
        icon_label.setObjectName("summaryIcon")
        icon_label.setFixedSize(28, 28)
        icon_label.setPixmap(QIcon(get_project_path("assets", "icons", "folder-gray.svg")).pixmap(24, 24))

        title_label = QLabel(text)
        title_label.setObjectName("summarySectionTitle")

        row_layout.addWidget(icon_label)
        row_layout.addWidget(title_label)
        row_layout.addStretch()

        return row_widget

    def create_summary_row(self, label_text, value_text, icon_name="folder"):
        row_widget = QWidget()
        row_widget.setObjectName("summaryRow")
        row_widget.setFixedHeight(37)
        row_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.setSpacing(12)
        row_widget.setLayout(row_layout)

        icon_label = QLabel("")
        icon_label.setObjectName("summaryIcon")
        icon_label.setFixedSize(28, 28)
        icon_label.setPixmap(self.get_summary_icon(icon_name).pixmap(24, 24))

        text_label = QLabel(label_text)
        text_label.setObjectName("summaryText")

        value_label = QLabel(value_text)
        value_label.setObjectName("summaryValue")

        row_layout.addWidget(icon_label)
        row_layout.addWidget(text_label)
        row_layout.addStretch()
        row_layout.addWidget(value_label)

        return row_widget

    def create_summary_note(self, note_text):
        note_label = QLabel(note_text)
        note_label.setObjectName("summaryNote")
        note_label.setWordWrap(True)

        return note_label

    def get_breadcrumb_text(self):
        selected_path = self.state.selected_folder_path
        current_path = self.state.current_view_folder_path

        if current_path == selected_path:
            return selected_path

        selected_name = self.state.selected_folder_name
        current_name = os.path.basename(current_path)

        return selected_name + " > " + current_name

    def get_folder_icon(self):
        return QIcon(get_project_path("assets", "icons", "center-folder.svg"))

    def get_sidebar_icon(self, name):
        icon_names = {
            "brand": "sidebar-folder.svg",
            "downloads": "sidebar-download.svg",
            "desktop": "sidebar-desktop.svg",
            "documents": "sidebar-document.svg",
            "pictures": "sidebar-image.svg",
            "music": "sidebar-music.svg",
            "movies": "sidebar-video.svg",
            "videos": "sidebar-video.svg",
            "settings": "sidebar-settings.svg",
            "help": "sidebar-help.svg",
        }
        icon_file = icon_names.get(name.lower(), "sidebar-folder.svg")

        return QIcon(get_project_path("assets", "icons", icon_file))

    def get_path_icon(self, item_path):
        if os.path.isdir(item_path):
            return self.get_folder_icon()

        return self.get_file_icon(os.path.basename(item_path))

    def get_summary_icon(self, icon_name):
        clean_name = icon_name.lower()

        if clean_name in ["images", "image"]:
            return QIcon(get_project_path("assets", "icons", "folder-purple.svg"))

        if clean_name in ["documents", "document"]:
            return QIcon(get_project_path("assets", "icons", "folder-blue.svg"))

        if clean_name in ["file", "ready"]:
            return QIcon(get_project_path("assets", "icons", "file-generic.svg"))

        if clean_name in ["spreadsheets", "spreadsheet"]:
            return QIcon(get_project_path("assets", "icons", "folder-green.svg"))

        if clean_name in ["archives", "archive"]:
            return QIcon(get_project_path("assets", "icons", "folder-gray.svg"))

        if clean_name in ["audio", "music"]:
            return QIcon(get_project_path("assets", "icons", "folder-pink.svg"))

        if clean_name in ["videos", "video"]:
            return QIcon(get_project_path("assets", "icons", "folder-orange.svg"))

        if clean_name == "duplicate":
            return QIcon(get_project_path("assets", "icons", "sidebar-copy.svg"))

        if clean_name == "skipped":
            return QIcon(get_project_path("assets", "icons", "sidebar-minus.svg"))

        return self.get_folder_icon()

    def get_file_icon(self, file_name):
        category = get_category_for_file(file_name)

        if category == "Images":
            return QIcon(get_project_path("assets", "icons", "file-image.svg"))

        if category == "Videos":
            return QIcon(get_project_path("assets", "icons", "file-video.svg"))

        if category == "Audio":
            return QIcon(get_project_path("assets", "icons", "file-audio.svg"))

        if category == "Documents":
            extension = os.path.splitext(file_name)[1].lower()

            if extension == ".pdf":
                return QIcon(get_project_path("assets", "icons", "file-pdf.svg"))

            return QIcon(get_project_path("assets", "icons", "file-generic.svg"))

        if category == "Spreadsheets":
            return QIcon(get_project_path("assets", "icons", "file-spreadsheet.svg"))

        if category == "Archives":
            return QIcon(get_project_path("assets", "icons", "file-archive.svg"))

        return QIcon(get_project_path("assets", "icons", "file-generic.svg"))

    def get_file_size_text(self, file_path):
        try:
            size = os.path.getsize(file_path)
        except OSError:
            return "-"

        if size < 1024:
            return str(size) + " B"

        if size < 1024 * 1024:
            return str(round(size / 1024, 1)) + " KB"

        if size < 1024 * 1024 * 1024:
            return str(round(size / (1024 * 1024), 1)) + " MB"

        return str(round(size / (1024 * 1024 * 1024), 1)) + " GB"

    def get_file_kind_text(self, file_name):
        category = get_category_for_file(file_name)

        if category != "Other":
            return category[:-1] if category.endswith("s") else category

        extension = os.path.splitext(file_name)[1].replace(".", "").upper()

        if extension == "":
            return "File"

        return extension + " file"

    def get_modified_text(self, item_path):
        try:
            modified_time = os.path.getmtime(item_path)
        except OSError:
            return "Unknown"

        return datetime.fromtimestamp(modified_time).strftime("%b %d, %Y").replace(" 0", " ")

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

    def clear_layout(self, layout):
        while layout.count() > 0:
            layout_item = layout.takeAt(0)
            widget = layout_item.widget()
            child_layout = layout_item.layout()

            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)
