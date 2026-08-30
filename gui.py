"""Creates the application, window, shows the window and starts the event loop."""

import sys  # Imports tools for talking to the operating system

from PySide6.QtGui import QIcon  # Imports the app icon tool
from PySide6.QtWidgets import QApplication  # Imports the main PySide6 app tool

from window import NeatifyWindow  # Imports our custom Neatify window


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/temp-logo.svg"))

    window = NeatifyWindow()
    window.show()

    return app.exec()


# Entry point
if __name__ == "__main__":
    sys.exit(main())
