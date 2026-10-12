APP_STYLE = """
        QMainWindow {
            background-color: #161716;
        }

        QWidget {
            background-color: #191A19;
            color: #F6F3ED;
            font-family: "Avenir Next", "Helvetica Neue", Arial;
            font-size: 13px;
        }

        QPushButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 8px;
            padding: 7px 12px;
            font-weight: 600;
        }

        QPushButton:hover {
            background-color: #2A2B29;
        }

        QLineEdit {
            background-color: #111211;
            color: #F6F3ED;
            border: 1px solid #313330;
            border-radius: 10px;
            padding: 10px 12px;
        }

        QComboBox {
            background-color: #111211;
            color: #F6F3ED;
            border: 1px solid #313330;
            border-radius: 10px;
            padding: 8px 30px 8px 10px;
            min-width: 110px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: 1px solid #313330;
            width: 26px;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
            background-color: #181918;
        }

        QComboBox::down-arrow {
            image: none;
            width: 0px;
            height: 0px;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #AEB4BF;
            margin-right: 8px;
        }

        QComboBox::drop-down:hover {
            background-color: #222321;
        }

        QComboBox QAbstractItemView {
            background-color: #20211F;
            color: #F6F3ED;
            selection-background-color: #3B3C38;
            border: 1px solid #40413F;
            outline: none;
            padding: 4px;
        }

        QListView#comboPopupList {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 8px;
            padding: 4px;
            outline: none;
            font-size: 13px;
        }

        QListView#comboPopupList::item {
            min-height: 26px;
            padding: 5px 8px;
            border-radius: 6px;
        }

        QListView#comboPopupList::item:selected {
            background-color: #3B3C38;
            color: #FFFFFF;
        }

        QScrollBar:vertical {
            background-color: transparent;
            width: 10px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background-color: #40413F;
            border-radius: 5px;
            min-height: 36px;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
            border: none;
            background-color: transparent;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background-color: transparent;
        }

        QScrollBar:horizontal {
            background-color: transparent;
            height: 10px;
            margin: 0px;
        }

        QScrollBar::handle:horizontal {
            background-color: #40413F;
            border-radius: 5px;
            min-width: 36px;
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
            border: none;
            background-color: transparent;
        }

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {
            background-color: transparent;
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
            padding: 4px;
        }

        QLabel#folderName {
            font-size: 27px;
            font-weight: 720;
            padding: 6px 0px 0px 0px;
        }

        QLabel#folderSummary {
            color: #AEB4BF;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 0px 12px 0px;
        }

        QLabel#breadcrumbLabel {
            color: #9098A6;
            font-size: 15px;
            font-weight: 500;
            padding: 4px 0px 0px 0px;
        }

        QPushButton#breadcrumbButton {
            background-color: transparent;
            color: #AEB4BF;
            border: none;
            border-radius: 8px;
            padding: 4px 0px;
            font-size: 15px;
            font-weight: 650;
            text-align: left;
        }

        QPushButton#breadcrumbButton:hover {
            color: #F6F3ED;
        }

        QLabel#breadcrumbSeparator {
            background-color: transparent;
            color: #6F7784;
            font-size: 15px;
            font-weight: 600;
            padding: 4px 0px;
        }

        QLabel#breadcrumbCurrent {
            background-color: transparent;
            color: #9098A6;
            font-size: 15px;
            font-weight: 550;
            padding: 4px 0px;
        }

        QPushButton#backButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 10px;
            padding: 6px 14px;
            font-size: 14px;
            font-weight: 700;
        }

        QPushButton#backButton:hover {
            background-color: #2A2B29;
        }

        QPushButton#backButton:disabled {
            color: #6F7784;
            border-color: #30312F;
            background-color: transparent;
        }

        QWidget#settingsPanel {
            background-color: #171817;
        }

        QWidget#historyPanel {
            background-color: #171817;
        }

        QLabel#settingsTitle {
            font-size: 26px;
            font-weight: 700;
            padding: 0px;
            background-color: transparent;
        }

        QLabel#settingsSectionTitle {
            font-size: 18px;
            font-weight: 700;
            padding: 0px;
            background-color: transparent;
        }

        QLabel#settingsHelp {
            color: #AAA9A1;
            font-size: 14px;
            padding: 0px;
            background-color: transparent;
        }

        QLabel#settingsMessage {
            color: #29D85F;
            font-size: 14px;
            padding: 0px;
            background-color: transparent;
        }

        QLabel#fieldLabel {
            color: #979890;
            font-size: 12px;
            font-weight: 700;
            padding: 0px;
            background-color: transparent;
        }

        QLabel#rulePreviewLabel {
            background-color: transparent;
            color: #F6F3ED;
            border: none;
            border-left: 3px solid #29D85F;
            border-radius: 0px;
            font-size: 14px;
            font-weight: 600;
            padding: 4px 0px 4px 10px;
        }

        QWidget#settingsMenuPanel {
            background-color: transparent;
        }

        QWidget#settingsFormPanel {
            background-color: transparent;
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

        QScrollArea#settingsPageScroll {
            background-color: transparent;
            border: none;
        }

        QScrollArea#settingsPageScroll QWidget {
            background-color: transparent;
        }

        QPushButton#settingsTabButton {
            background-color: transparent;
            color: #AAA9A1;
            border: none;
            border-radius: 8px;
            padding: 9px 10px;
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
            border-radius: 8px;
            padding: 9px 10px;
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
            background-color: transparent;
            color: #F6F3ED;
            border: none;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 15px;
            font-weight: 650;
            text-align: left;
            min-height: 42px;
        }

        QPushButton#centerFolderCard:hover {
            background-color: #252624;
        }

        QPushButton#activeCenterFolderCard {
            background-color: #2A2B29;
            color: #FFFFFF;
            border: 1px solid #29D85F;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 15px;
            font-weight: 650;
            text-align: left;
            min-height: 42px;
        }

        QLabel#sectionTitle {
            color: #AEB4BF;
            font-size: 12px;
            font-weight: 650;
            text-transform: uppercase;
            padding: 10px 0px 6px 0px;
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
            border-radius: 0px;
            padding: 0px;
            font-size: 13px;
        }

        QTreeWidget#folderContentsList::item {
            padding: 8px 8px;
            border-bottom: 1px solid #30312F;
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
            color: #9098A6;
            border: none;
            border-bottom: 1px solid #30312F;
            padding: 6px 8px 8px 8px;
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
            font-size: 20px;
            font-weight: 760;
            padding: 0px 0px 10px 0px;
        }

        QWidget#summaryPanel {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #20242B, stop:1 #171817);
            border: 1px solid rgba(60, 72, 88, 0.55);
            border-radius: 14px;
            padding: 18px 20px;
        }

        QLabel#summaryCardTitle {
            background-color: transparent;
            color: #F6F3ED;
            font-size: 18px;
            font-weight: 740;
            padding: 0px 0px 8px 0px;
        }

        QWidget#summaryMetricRow {
            background-color: transparent;
            border-radius: 8px;
        }

        QWidget#summaryRow {
            background-color: transparent;
            border-radius: 8px;
        }

        QWidget#summarySectionRow {
            background-color: transparent;
            border-radius: 8px;
        }

        QLabel#summaryIcon {
            background-color: transparent;
            padding: 0px;
        }

        QLabel#summaryMetricText {
            background-color: transparent;
            color: #DCE3EF;
            font-size: 14px;
            font-weight: 590;
            padding: 0px;
        }

        QLabel#summaryText {
            background-color: transparent;
            color: #DCE3EF;
            font-size: 14px;
            font-weight: 560;
            padding: 0px;
        }

        QLabel#summaryValue {
            background-color: transparent;
            color: #8F98A8;
            font-size: 13px;
            font-weight: 550;
            padding: 0px;
        }

        QLabel#summarySectionTitle {
            background-color: transparent;
            color: #F6F3ED;
            font-size: 14px;
            font-weight: 710;
            padding: 0px;
        }

        QLabel#summaryNote {
            background-color: transparent;
            color: #AEB4BF;
            font-size: 14px;
            line-height: 1.35;
            padding: 4px 0px;
        }

        QLabel#summaryDivider {
            background-color: #30343B;
            min-height: 1px;
            max-height: 1px;
            padding: 0px;
            margin-top: 12px;
            margin-bottom: 12px;
        }

        QDialog#previewDialog {
            background-color: #171817;
        }

        QLabel#previewDialogTitle {
            background-color: transparent;
            color: #F6F3ED;
            font-size: 24px;
            font-weight: 760;
            padding: 0px;
        }

        QLabel#previewDialogPath {
            background-color: transparent;
            color: #9098A6;
            font-size: 13px;
            padding: 0px 0px 8px 0px;
        }

        QLabel#previewImage {
            background-color: #111211;
            border: 1px solid #30312F;
            border-radius: 10px;
            padding: 16px;
        }

        QTextEdit#previewText {
            background-color: #111211;
            color: #F6F3ED;
            border: 1px solid #30312F;
            border-radius: 10px;
            padding: 12px;
            font-family: Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
        }

        QTextEdit#helpText {
            background-color: #111211;
            color: #F6F3ED;
            border: 1px solid #30312F;
            border-radius: 10px;
            padding: 18px;
            font-size: 15px;
            line-height: 1.45;
        }

        QPdfView#previewPdf {
            background-color: #111211;
            border: 1px solid #30312F;
            border-radius: 10px;
        }

        QLabel#previewUnsupported {
            background-color: #111211;
            color: #D8D5CD;
            border: 1px solid #30312F;
            border-radius: 10px;
            padding: 18px;
            font-size: 15px;
        }

        QLabel#arrangePreviewTitle {
            font-size: 28px;
            font-weight: 750;
            padding: 0px;
        }

        QLabel#arrangePreviewHelp {
            color: #AAA9A1;
            font-size: 15px;
            font-weight: 550;
            padding: 0px 0px 8px 0px;
        }

        QLabel#arrangePreviewWarning {
            background-color: rgba(245, 185, 66, 0.12);
            color: #FFD166;
            border: 1px solid rgba(245, 185, 66, 0.38);
            border-radius: 10px;
            padding: 14px 16px;
            font-size: 15px;
            font-weight: 650;
        }

        QTreeWidget#arrangePreviewTable {
            background-color: transparent;
            color: #F6F3ED;
            border: 1px solid #30312F;
            border-radius: 10px;
            padding: 0px;
            font-size: 13px;
            min-height: 320px;
        }

        QTreeWidget#arrangePreviewTable::item {
            padding: 14px 8px;
            border-bottom: 1px solid #30312F;
        }

        QTreeWidget#arrangePreviewTable::item:selected {
            background-color: #3B3C38;
            color: #FFFFFF;
        }

        QTreeWidget#arrangePreviewTable::item:hover {
            background-color: #222321;
        }

        QTreeWidget#arrangePreviewTable QHeaderView::section {
            background-color: #20211F;
            color: #D8D5CD;
            border: none;
            border-bottom: 1px solid #30312F;
            padding: 8px 8px;
            font-size: 12px;
            font-weight: 650;
            text-transform: uppercase;
        }

        QTreeWidget#arrangePreviewTable::indicator {
            width: 18px;
            height: 18px;
        }

        QTreeWidget#arrangePreviewTable::indicator:checked {
            background-color: #2489FF;
            border: 1px solid #5CA9FF;
            border-radius: 4px;
        }

        QLabel#moveStatusBadge {
            background-color: #184F2C;
            color: #9AF2B1;
            border-radius: 7px;
            padding: 4px 10px;
            font-size: 13px;
            font-weight: 650;
        }

        QLabel#duplicateStatusBadge {
            background-color: #173D63;
            color: #B7DCFF;
            border-radius: 7px;
            padding: 4px 10px;
            font-size: 13px;
            font-weight: 650;
        }

        QLabel#previewItem {
            border-bottom: 1px solid #30312F;
            padding: 12px;
        }

        QLabel#foldersTitle {
            color: #8D95A3;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            padding: 10px 0px 4px 0px;
        }

        QPushButton#sidebarBrand {
            background-color: transparent;
            color: #F6F3ED;
            border: none;
            border-radius: 10px;
            padding: 2px 0px 8px 0px;
            font-size: 21px;
            font-weight: 720;
            text-align: left;
            min-height: 34px;
        }

        QPushButton#sidebarBrand:disabled {
            color: #F6F3ED;
            background-color: transparent;
        }

        QPushButton#folderItem {
            color: #B8C0CE;
            font-size: 14px;
            font-weight: 500;
            padding: 7px 9px;
            text-align: left;
            border: none;
            background-color: transparent;
            border-radius: 8px;
            min-height: 30px;
        }

        QPushButton#folderItem:hover {
            background-color: #252624;
        }

        QPushButton#activeFolder {
            background-color: #343841;
            color: #E8EDF7;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            padding: 7px 9px;
            text-align: left;
            border: none;
            min-height: 30px;
        }

        QLabel#sidebarFooterDivider {
            background-color: #30343B;
            min-height: 1px;
            max-height: 1px;
            padding: 0px;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        QPushButton#sidebarFooterButton {
            background-color: transparent;
            color: #B8C0CE;
            border: none;
            border-radius: 8px;
            padding: 7px 9px;
            font-size: 14px;
            font-weight: 500;
            text-align: left;
            min-height: 30px;
        }

        QPushButton#sidebarFooterButton:hover {
            background-color: #252624;
            color: #F6F3ED;
        }

        QPushButton#activeSidebarFooterButton {
            background-color: #343841;
            color: #E8EDF7;
            border: none;
            border-radius: 8px;
            padding: 7px 9px;
            font-size: 14px;
            font-weight: 500;
            text-align: left;
            min-height: 30px;
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
            border-radius: 8px;
            padding: 8px 10px;
            font-weight: 650;
        }

        QPushButton#secondaryActionButton:hover {
            background-color: #252624;
        }

        QPushButton#secondaryActionButton:disabled {
            color: #6F7784;
            border-color: #30312F;
            background-color: transparent;
        }

        QPushButton#dangerActionButton {
            background-color: #20211F;
            color: #FF8A8A;
            border: 1px solid #40413F;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            min-width: 120px;
        }

        QPushButton#dangerActionButton:hover {
            background-color: #2A2020;
            border-color: #7A3A3A;
        }

        QPushButton#confirmArrangeButton {
            background-color: #29D85F;
            color: #07150B;
            border: 1px solid #29D85F;
            border-radius: 8px;
            padding: 10px 30px;
            font-weight: bold;
            min-width: 220px;
            min-height: 40px;
        }

        QPushButton#confirmArrangeButton:enabled {
            background-color: #29D85F;
            color: #07150B;
            border: 1px solid #29D85F;
        }

        QPushButton#confirmArrangeButton:hover {
            background-color: #34E96C;
            border: 1px solid #34E96C;
        }

        QPushButton#confirmArrangeButton:disabled {
            background-color: #3B3C38;
            color: #8E9088;
        }

        QPushButton#primaryCommand {
            background-color: #29D85F;
            color: #07150B;
            border: none;
            border-radius: 9px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 700;
            min-height: 30px;
        }

        QPushButton#commandButton {
            background-color: #20211F;
            color: #F6F3ED;
            border: 1px solid #40413F;
            border-radius: 9px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 650;
            min-height: 30px;
        }

        QPushButton#commandButton:hover {
            background-color: #2A2B29;
        }

        QPushButton#primaryCommand:hover {
            background-color: #34E96C;
        }

        QPushButton#primaryCommand:disabled {
            background-color: #3B3C38;
            color: #8E9088;
        }

        QPushButton#addRuleButton {
            background-color: #0A84FF;
            color: #FFFFFF;
            border: none;
            border-radius: 9px;
            padding: 7px 16px;
            font-size: 13px;
            font-weight: 700;
            min-height: 30px;
            min-width: 110px;
        }

        QPushButton#addRuleButton:hover {
            background-color: #339CFF;
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
            border-left: none;
        }
    """
