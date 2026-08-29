from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QLabel, QGridLayout #QtWidgets contains windows, buttons, labels and text boxes, QApplication is the whole app mamainr, QMainWindow is the main window, #QWidget is nay GUI object, buttons, etc
import sys


def main():
    app = QApplication(sys.argv) # Main GUI application object created

    window = QMainWindow()  # Creates the main window
    window.setWindowTitle("Neatify")
    window.resize(1100, 650)

    central_widget = QWidget()  # Container widget
    window.setCentralWidget(central_widget)

    # Layout
    page_layout = QVBoxLayout() # Creates the vertical layout
    central_widget.setLayout(page_layout) # Attached the above layout to the central widget
    commands_layout = QHBoxLayout()
    ask_layout = QHBoxLayout()
    main_layout = QHBoxLayout()
    left_layout = QVBoxLayout() # Top to bottom folder names
    center_layout = QVBoxLayout()   # title, summary, category cards
    right_layout = QVBoxLayout()    # preview, proceed button

    # Creating margins and spacing
    page_layout.setContentsMargins(18, 18, 18, 18)
    page_layout.setSpacing(14)

    commands_layout.setSpacing(10)
    ask_layout.setSpacing(10)
    main_layout.setSpacing(0)

    left_layout.setContentsMargins(20, 24, 20, 24)
    center_layout.setContentsMargins(28, 28, 28, 28)
    right_layout.setContentsMargins(22, 28, 22, 28)

    left_layout.setSpacing(8)
    center_layout.setSpacing(14)
    right_layout.setSpacing(14)

    # Creation of buttons
    arrange_button = QPushButton("Arrange")
    find_button = QPushButton("Find")
    open_button = QPushButton("Open")
    undo_button = QPushButton("Undo")
    history_button = QPushButton("History")

    arrange_button.setObjectName("primaryCommand")
    find_button.setObjectName("commandButton")
    open_button.setObjectName("commandButton")
    undo_button.setObjectName("commandButton")
    history_button.setObjectName("commandButton")

    page_layout.addLayout(commands_layout)
    page_layout.addLayout(ask_layout)
    page_layout.addLayout(main_layout)

    # Places the buttons inside the top command row
    commands_layout.addWidget(arrange_button)
    commands_layout.addWidget(find_button)
    commands_layout.addWidget(open_button)
    commands_layout.addWidget(undo_button)
    commands_layout.addWidget(history_button)

    # Adds empty flexible space afterthe buttons
    commands_layout.addStretch()

    ask_input = QLineEdit()
    ask_input.setPlaceholderText("Ask Neatify: show me all PDFs in this folder...")
    ask_layout.addWidget(ask_input)

    def start_command(command_text):
        ask_input.setText(command_text)
        ask_input.setFocus()

    arrange_button.clicked.connect(lambda: start_command("arrange "))
    find_button.clicked.connect(lambda: start_command("find "))
    open_button.clicked.connect(lambda: start_command("open "))
    undo_button.clicked.connect(lambda: start_command("undo last move"))
    history_button.clicked.connect(lambda: start_command("show history"))

    # Panels
    left_panel = QWidget()
    center_panel = QWidget()
    right_panel = QWidget()

    left_panel.setMinimumWidth(240)
    right_panel.setMinimumWidth(300)

    main_layout.addWidget(left_panel, 1)
    main_layout.addWidget(center_panel, 2)
    main_layout.addWidget(right_panel, 1)   #  The numbers are stretch factors

    left_panel.setLayout(left_layout)
    center_panel.setLayout(center_layout)
    right_panel.setLayout(right_layout)
    left_panel.setObjectName("leftPanel")
    center_panel.setObjectName("centerPanel")
    right_panel.setObjectName("rightPanel")
    central_widget.setObjectName("centralWidget")

    # Creating text labels on the left panel
    folders_title = QLabel("Folders")
    downloads_label = QPushButton("Downloads")
    desktop_label = QPushButton("Desktop")
    documents_label = QPushButton("Documents")
    pictures_label = QPushButton("Pictures")
    music_label = QPushButton("Music")
    external_label = QPushButton("External Drives")

    folder_buttons = [
        downloads_label,
        desktop_label,
        documents_label,
        pictures_label,
        music_label,
        external_label,
    ]

    folders_title.setObjectName("foldersTitle")
    downloads_label.setObjectName("activeFolder")
    desktop_label.setObjectName("folderItem")
    documents_label.setObjectName("folderItem")
    pictures_label.setObjectName("folderItem")
    music_label.setObjectName("folderItem")
    external_label.setObjectName("folderItem")

    # Creating the text labels in center panel
    folder_name_label = QLabel("Downloads")
    folder_summary_label = QLabel("238 files scanned - preview ready")

    def select_folder(folder_name, selected_button):
        folder_name_label.setText(folder_name)

        for button in folder_buttons:
            button.setObjectName("folderItem")
            button.style().unpolish(button)
            button.style().polish(button)

        selected_button.setObjectName("activeFolder")
        selected_button.style().unpolish(selected_button)
        selected_button.style().polish(selected_button)

    # Callback
    downloads_label.clicked.connect(lambda: select_folder("Downloads", downloads_label))
    desktop_label.clicked.connect(lambda: select_folder("Desktop", desktop_label))
    documents_label.clicked.connect(lambda: select_folder("Documents", documents_label))
    pictures_label.clicked.connect(lambda: select_folder("Pictures", pictures_label))
    music_label.clicked.connect(lambda: select_folder("Music", music_label))
    external_label.clicked.connect(lambda: select_folder("External Drives", external_label))

    # Placing the labels into the left panel
    left_layout.addWidget(folders_title)
    left_layout.addWidget(downloads_label)
    left_layout.addWidget(desktop_label)
    left_layout.addWidget(documents_label)
    left_layout.addWidget(pictures_label)
    left_layout.addWidget(music_label)
    left_layout.addWidget(external_label)

    documents_card = QLabel("Documents\n86")
    images_card = QLabel("Images\n104")
    videos_card = QLabel("Videos\n14")
    duplicates_card = QLabel("Duplicates renamed\n5")

    cards_layout = QGridLayout()

    # Placing the labels in the center panel
    center_layout.addWidget(folder_name_label)
    center_layout.addWidget(folder_summary_label)
    cards_layout.addWidget(documents_card, 0, 0)
    cards_layout.addWidget(images_card, 0, 1)
    cards_layout.addWidget(videos_card, 1, 0)
    cards_layout.addWidget(duplicates_card, 1, 1)

    center_layout.addLayout(cards_layout)
    center_layout.addStretch()

    # Creating the text labels in right panel
    safety_label = QLabel("Nothing deleted, ever.")
    preview_title = QLabel("Preview")

    preview_item_one = QLabel("report.pdf\nDocuments/report_1.pdf")
    preview_item_two = QLabel("photo.JPG\nImages/photo.JPG")
    preview_item_three = QLabel("lecture.mp4\nVideos/lecture.mp4")

    proceed_button = QPushButton("Proceed")

    # Placing the labels in the right panel
    right_layout.addWidget(safety_label)
    right_layout.addWidget(preview_title)
    right_layout.addWidget(preview_item_one)
    right_layout.addWidget(preview_item_two)
    right_layout.addWidget(preview_item_three)
    right_layout.addStretch()
    right_layout.addWidget(proceed_button)

    folder_name_label.setObjectName("folderName")
    folder_summary_label.setObjectName("folderSummary")

    documents_card.setObjectName("categoryCard")
    images_card.setObjectName("categoryCard")
    videos_card.setObjectName("categoryCard")
    duplicates_card.setObjectName("categoryCard")

    safety_label.setObjectName("safetyLabel")
    preview_title.setObjectName("previewTitle")
    preview_item_one.setObjectName("previewItem")
    preview_item_two.setObjectName("previewItem")
    preview_item_three.setObjectName("previewItem")

    proceed_button.setObjectName("proceedButton")

    # Styling the window with color
    window.setStyleSheet("""
        QMainWindow {
            background-color: #161716;
        }

        QWidget {
            background-color: #191A19;
            color: #F6F3ED;
            font-family: Arial;
            font-size: 16px;
        }

        QPushButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #2A2B29;
        }

        QLineEdit {
            background-color: #111211;
            color: #F6F3ED;
            border: 1px solid #313330;
            border-radius: 14px;
            padding: 12px;
        }

        QLabel {
            padding: 8px;
        }

        QLabel#folderName {
            font-size: 32px;
            font-weight: bold;
            padding-top: 18px;
        }

        QLabel#folderSummary {
            color: #AAA9A1;
            font-size: 18px;
        }

        QLabel#categoryCard {
            background-color: #111211;
            border-radius: 16px;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
        }

        QLabel#safetyLabel {
            background-color: #08290D;
            color: #19E241;
            border-radius: 16px;
            padding: 16px;
            font-size: 18px;
            font-weight: bold;
        }

        QLabel#previewTitle {
            font-size: 24px;
            font-weight: bold;
        }

        QLabel#previewItem {
            border-bottom: 1px solid #30312F;
            padding: 12px;
        }

        QLabel#foldersTitle {
            color: #979890;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
        }

        QPushButton#folderItem {
            color: #D8D5CD;
            font-size: 17px;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border: none;
            background-color: transparent;
        }

        QPushButton#folderItem:hover {
            background-color: #252624;
        }

        QPushButton#activeFolder {
            background-color: #3B3C38;
            color: #FFFFFF;
            border-radius: 12px;
            font-size: 17px;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border: none;
        }

        QPushButton#proceedButton {
            background-color: #29D85F;
            color: #07150B;
            border: none;
            border-radius: 14px;
            padding: 16px;
            font-weight: bold;
        }

        QPushButton#primaryCommand {
            background-color: #29D85F;
            color: #07150B;
            border: none;
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: bold;
        }

        QPushButton#commandButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: bold;
        }

        QPushButton#commandButton:hover {
            background-color: #2A2B29;
        }

        QPushButton#primaryCommand:hover {
            background-color: #34E96C;
        }

        QWidget#centralWidget {
            background-color: #161716;
        }

        QWidget#leftPanel {
            background-color: #1B1C1B;
            border-right: 1px solid #2C2D2B;
        }

        QWidget#centerPanel {
            background-color: #171817;
        }

        QWidget#rightPanel {
            background-color: #1A1B1A;
            border-left: 1px solid #2C2D2B;
        }
    """)

    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())