"""Entry point for the Calendar Countdown desktop application.

Usage:
    python main.py
"""
import sys
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> None:
    # High-DPI scaling is enabled by default in PySide6 >= 6.5
    app = QApplication(sys.argv)
    app.setApplicationName("CalendarCountdown")
    app.setOrganizationName("CalendarCountdown")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
