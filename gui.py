"""Creates the application, window, shows the window and starts the event loop."""

import sys  # Imports tools for talking to the operating system

from app_paths import get_project_path  # Imports our tool for finding project files
from neatify import recover_incomplete_operations  # Imports crash recovery for incomplete file operations
from PySide6.QtGui import QIcon  # Imports the app icon tool
from PySide6.QtWidgets import QApplication  # Imports the main PySide6 app tool

from window import NeatifyWindow  # Imports our custom Neatify window


def main():
    try:
        recover_incomplete_operations()
    except OSError as error:
        print("Warning: recovery could not complete:", error)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_project_path("assets", "neatify-logo.svg")))

    window = NeatifyWindow()
    window.show()

    return app.exec()


# Entry point
if __name__ == "__main__":
    sys.exit(main())
