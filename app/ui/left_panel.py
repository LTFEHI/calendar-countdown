"""Left panel container: clock widget + calendar widget."""
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import QDate

from app.config import COLOR_CARD_BG, PADDING_SM
from app.data.models import CalendarMode
from app.ui.clock_widget import ClockWidget
from app.ui.calendar_widget import CalendarWidget
from app.ui.styles import LEFT_PANEL_STYLE


class LeftPanel(QWidget):
    """Left panel (40%): real-time clock on top, calendar below.

    Delegates calendar mode changes to both sub-widgets.
    """

    # Re-export calendar day click for main window routing
    calendar_day_clicked = Signal(QDate)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setStyleSheet(LEFT_PANEL_STYLE)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.clock_widget = ClockWidget()
        self.calendar_widget = CalendarWidget()

        # Forward calendar day click
        self.calendar_widget.day_clicked.connect(
            lambda d: self.calendar_day_clicked.emit(
                QDate(d.year, d.month, d.day)
            )
        )

        layout.addWidget(self.clock_widget)
        layout.addWidget(self.calendar_widget, stretch=1)

    # ── Public ────────────────────────────────────────────────

    def set_calendar_mode(self, mode: CalendarMode) -> None:
        self.clock_widget.set_calendar_mode(mode)
        self.calendar_widget.set_calendar_mode(mode)

    def on_refresh(self, now: datetime) -> None:
        """Called every second by MainWindow.refresh_tick."""
        self.clock_widget.on_refresh(now)
