APP_STYLE = """
        QMainWindow {
            background-color: #161716;
        }

        QWidget {
            background-color: #191A19;
            color: #F6F3ED;
            font-family: "Avenir Next", "Helvetica Neue", Arial;
            font-size: 16px;
        }

        QPushButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 12px;
            padding: 8px 14px;
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

        QComboBox {
            background-color: #111211;
            color: #F6F3ED;
            border: 1px solid #313330;
            border-radius: 14px;
            padding: 10px;
            min-width: 110px;
        }

        QComboBox::drop-down {
            border: none;
            width: 24px;
        }

        QComboBox QAbstractItemView {
            background-color: #20211F;
            color: #F6F3ED;
            selection-background-color: #3B3C38;
            border: 1px solid #40413F;
        }

        QCheckBox {
            color: #F6F3ED;
            spacing: 8px;
            font-weight: 600;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }

        QCheckBox::indicator:unchecked {
            background-color: #111211;
            border: 1px solid #40413F;
            border-radius: 5px;
        }

        QCheckBox::indicator:checked {
            background-color: #29D85F;
            border: 1px solid #29D85F;
            border-radius: 5px;
        }

        QLabel {
            padding: 8px;
        }

        QLabel#folderName {
            font-size: 30px;
            font-weight: 700;
            padding-top: 10px;
        }

        QLabel#folderSummary {
            color: #AAA9A1;
            font-size: 16px;
            font-weight: 500;
        }

        QLabel#breadcrumbLabel {
            color: #8E9088;
            font-size: 13px;
            font-weight: 500;
            padding-top: 0px;
        }

        QWidget#settingsPanel {
            background-color: #171817;
        }

        QWidget#historyPanel {
            background-color: #171817;
        }

        QLabel#settingsTitle {
            font-size: 30px;
            font-weight: 700;
            padding: 0px;
        }

        QLabel#settingsSectionTitle {
            font-size: 22px;
            font-weight: 700;
            padding: 0px;
        }

        QLabel#settingsHelp {
            color: #AAA9A1;
            font-size: 14px;
            padding: 0px;
        }

        QLabel#settingsMessage {
            color: #29D85F;
            font-size: 14px;
            padding: 0px;
        }

        QTreeWidget#settingsRulesTable {
            background-color: transparent;
            color: #F6F3ED;
            border: none;
            padding: 0px;
            font-size: 15px;
        }

        QTreeWidget#settingsRulesTable::item {
            padding: 9px;
            border-bottom: 1px solid #30312F;
        }

        QTreeWidget#settingsRulesTable::item:selected {
            background-color: #3B3C38;
            color: #FFFFFF;
        }

        QTreeWidget#settingsRulesTable QHeaderView::section {
            background-color: transparent;
            color: #8E9088;
            border: none;
            border-bottom: 1px solid #30312F;
            padding: 6px 8px;
            font-size: 12px;
            font-weight: 650;
            text-transform: uppercase;
        }

        QStackedWidget#settingsStack {
            background-color: transparent;
            border: none;
        }

        QWidget#settingsPage {
            background-color: transparent;
        }

        QPushButton#settingsTabButton {
            background-color: transparent;
            color: #AAA9A1;
            border: none;
            border-radius: 12px;
            padding: 12px;
            font-weight: 650;
            text-align: left;
        }

        QPushButton#settingsTabButton:hover {
            background-color: #252624;
            color: #F6F3ED;
        }

        QPushButton#activeSettingsTabButton {
            background-color: #3B3C38;
            color: #FFFFFF;
            border: 1px solid #29D85F;
            border-radius: 12px;
            padding: 12px;
            font-weight: 650;
            text-align: left;
        }

        QLabel#categoryCard {
            background-color: #111211;
            border-radius: 16px;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
        }

        QPushButton#centerFolderCard {
            background-color: #111211;
            color: #F6F3ED;
            border: none;
            border-radius: 16px;
            padding: 18px;
            font-size: 16px;
            font-weight: 650;
            text-align: left;
        }

        QPushButton#centerFolderCard:hover {
            background-color: #252624;
        }

        QPushButton#activeCenterFolderCard {
            background-color: #3B3C38;
            color: #FFFFFF;
            border: 1px solid #29D85F;
            border-radius: 16px;
            padding: 18px;
            font-size: 16px;
            font-weight: 650;
            text-align: left;
        }

        QLabel#sectionTitle {
            color: #AAA9A1;
            font-size: 14px;
            font-weight: 650;
            text-transform: uppercase;
            padding-top: 10px;
        }

        QLabel#emptyMessage {
            color: #AAA9A1;
            font-size: 16px;
            padding: 20px;
        }

        QWidget#centerContent {
            background-color: transparent;
        }

        QScrollArea#centerScrollArea {
            background-color: transparent;
            border: none;
        }

        QScrollArea#centerScrollArea QWidget {
            background-color: transparent;
        }

        QTreeWidget#folderContentsList {
            background-color: transparent;
            color: #F6F3ED;
            border: none;
            padding: 0px;
            font-size: 16px;
        }

        QTreeWidget#folderContentsList::item {
            padding: 8px;
            border-radius: 6px;
        }

        QTreeWidget#folderContentsList::item:selected {
            background-color: #3B3C38;
            color: #FFFFFF;
        }

        QTreeWidget#folderContentsList::item:hover {
            background-color: #222321;
        }

        QTreeWidget#folderContentsList::branch {
            background-color: transparent;
        }

        QTreeWidget#folderContentsList QHeaderView::section {
            background-color: transparent;
            color: #8E9088;
            border: none;
            padding: 6px 8px;
            font-size: 12px;
            font-weight: 650;
            text-transform: uppercase;
        }

        QTreeWidget#outputList {
            background-color: transparent;
            color: #F6F3ED;
            border: none;
            padding: 0px;
            font-size: 14px;
        }

        QTreeWidget#outputList::item {
            padding: 8px;
            border-bottom: 1px solid #30312F;
        }

        QTreeWidget#outputList::item:selected {
            background-color: #3B3C38;
            color: #FFFFFF;
        }

        QTreeWidget#outputList::item:hover {
            background-color: #222321;
        }

        QTreeWidget#outputList QHeaderView::section {
            background-color: transparent;
            color: #8E9088;
            border: none;
            border-bottom: 1px solid #30312F;
            padding: 6px 8px;
            font-size: 12px;
            font-weight: 650;
            text-transform: uppercase;
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
            font-size: 22px;
            font-weight: 700;
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
            font-size: 15px;
            font-weight: 600;
            padding: 10px;
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
            font-size: 15px;
            font-weight: 650;
            padding: 10px;
            text-align: left;
            border: none;
        }

        QPushButton#proceedButton {
            background-color: #29D85F;
            color: #07150B;
            border: none;
            border-radius: 14px;
            padding: 12px;
            font-weight: bold;
        }

        QPushButton#secondaryActionButton {
            background-color: transparent;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 14px;
            padding: 10px;
            font-weight: 650;
        }

        QPushButton#secondaryActionButton:hover {
            background-color: #252624;
        }

        QPushButton#primaryCommand {
            background-color: #29D85F;
            color: #07150B;
            border: none;
            border-radius: 12px;
            padding: 8px 14px;
            font-weight: bold;
        }

        QPushButton#commandButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 12px;
            padding: 8px 14px;
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
    """
