"""Real-time clock display widget.

Shows:
  - Large HH:MM:SS (refreshed every second)
  - Current date (YYYY年MM月DD日) + weekday
  - Lunar date (when in lunar mode)
"""
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

from app.config import (
    FONT_FAMILY, FONT_SIZE_CLOCK, FONT_SIZE_DATE, FONT_SIZE_SMALL,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, PADDING_MD,
)
from app.data.models import CalendarMode
from app.logic.lunar_converter import format_lunar_full


WEEKDAY_NAMES = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


class ClockWidget(QWidget):
    """Displays current time, date, weekday, and optionally lunar date."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._calendar_mode = CalendarMode.SOLAR
        self._setup_ui()

    # ── Setup ─────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING_MD, PADDING_MD + 8, PADDING_MD, PADDING_MD)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Clock: large HH:MM:SS
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("clockLabel")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet(f"""
            QLabel#clockLabel {{
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_CLOCK}px;
                font-weight: 300;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        layout.addWidget(self.clock_label)

        # Date: YYYY年MM月DD日 星期X
        self.date_label = QLabel("2026年06月25日 星期四")
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_DATE}px;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        layout.addWidget(self.date_label)

        # Lunar date (small, below main date)
        self.lunar_label = QLabel("")
        self.lunar_label.setAlignment(Qt.AlignCenter)
        self.lunar_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL}px;
                color: {COLOR_TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        layout.addWidget(self.lunar_label)

        layout.addStretch()

    # ── Public ────────────────────────────────────────────────

    def set_calendar_mode(self, mode: CalendarMode) -> None:
        self._calendar_mode = mode

    def update_time(self, now: datetime) -> None:
        """Called every second by the global timer."""
        # Clock
        self.clock_label.setText(now.strftime("%H:%M:%S"))

        # Date + weekday
        weekday = WEEKDAY_NAMES[now.weekday()]
        date_str = f"{now.year}年{now.month:02d}月{now.day:02d}日 {weekday}"
        self.date_label.setText(date_str)

        # Lunar
        if self._calendar_mode == CalendarMode.LUNAR:
            lunar_str = format_lunar_full(now.date())
            self.lunar_label.setText(lunar_str or "（农历超出范围）")
            self.lunar_label.setVisible(True)
        else:
            self.lunar_label.setVisible(False)

    def on_refresh(self, now: datetime) -> None:
        """Slot connected to MainWindow.refresh_tick."""
        self.update_time(now)
