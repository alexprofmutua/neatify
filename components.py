"""Creates reusable UI builders"""

from PySide6.QtWidgets import QLabel, QPushButton  # Imports text labels and clickable buttons

def create_folder_button(folder_name, active=False):
    """
    Creates one left-side folder button
    """
    button = QPushButton(folder_name)

    if active:
        button.setObjectName("activeFolder")
    else:
        button.setObjectName("folderItem")

    return button


def create_category_card(category_name, count):
    """
    Creates one center category card
    """
    card = QLabel(category_name + "\n" + str(count))
    card.setObjectName("categoryCard")

    return card


def create_preview_item(text):
    """
    Creates one right-side preview item.
    """
    preview_item = QLabel(text)
    preview_item.setObjectName("previewItem")

    return preview_item