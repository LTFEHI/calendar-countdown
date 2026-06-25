"""Right panel container: event list with toolbar.

Wraps EventList and forwards relevant signals.
"""
from datetime import datetime, date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from app.data.event_store import EventStore
from app.ui.event_list import EventList
from app.ui.styles import RIGHT_PANEL_STYLE


class RightPanel(QWidget):
    """Right panel (60%): countdown event list.

    Contains the EventList widget and forwards signals.
    """

    event_count_changed = Signal(int)
    event_dates_changed = Signal(dict)   # dict[date, (count, has_imminent)]

    def __init__(self, event_store: EventStore, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(RIGHT_PANEL_STYLE)

        self._setup_ui(event_store)

    def _setup_ui(self, event_store: EventStore) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.event_list = EventList(event_store)
        self.event_list.event_count_changed.connect(self.event_count_changed.emit)
        self.event_list.event_dates_changed.connect(self.event_dates_changed.emit)

        layout.addWidget(self.event_list, stretch=1)

        # Emit initial event dates after construction
        self.event_list._emit_event_dates()

    def on_refresh(self, now: datetime) -> None:
        """Called every second by MainWindow.refresh_tick."""
        self.event_list.update_countdowns(now)
