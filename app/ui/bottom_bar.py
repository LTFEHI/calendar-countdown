"""Bottom status bar: shows current calendar mode and event count."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy

from app.data.models import CalendarMode
from app.ui.styles import BOTTOM_BAR_STYLE
from app.config import BOTTOM_BAR_HEIGHT


class BottomBar(QWidget):
    """Minimal bottom bar displaying time system and event count."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("bottomBar")
        self.setFixedHeight(BOTTOM_BAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._event_count = 0
        self._calendar_mode = CalendarMode.SOLAR

        self._setup_ui()
        self.setStyleSheet(BOTTOM_BAR_STYLE)

    # ── Setup ─────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        # Calendar mode indicator
        self.mode_label = QLabel("公历")
        self.mode_label.setObjectName("bottomBarLabel")
        layout.addWidget(self.mode_label)

        layout.addStretch()

        # Event count
        self.count_label = QLabel("共 0 个事件")
        self.count_label.setObjectName("bottomBarLabel")
        layout.addWidget(self.count_label)

    # ── Public ────────────────────────────────────────────────

    def set_calendar_mode(self, mode: CalendarMode) -> None:
        self._calendar_mode = mode
        self.mode_label.setText("农历" if mode == CalendarMode.LUNAR else "公历")

    def set_event_count(self, count: int) -> None:
        self._event_count = count
        self.count_label.setText(f"共 {count} 个事件")
