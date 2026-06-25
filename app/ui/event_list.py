"""Scrollable event list with sorting, empty state, and action buttons.

Manages:
  - Rendering EventCard widgets in a sorted order
  - Adding / removing / re-sorting cards
  - Empty state display when no events exist
  - Real-time countdown updates (delegated to each card)
"""
from datetime import datetime, date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QSizePolicy, QFrame,
)

from app.config import (
    FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_NORMAL, FONT_SIZE_SMALL,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_SECONDARY,
    COLOR_BG, COLOR_CARD_BG, COLOR_BORDER,
    PADDING_LG, PADDING_MD, PADDING_SM, BORDER_RADIUS,
)
from app.data.models import Event, EventStatus
from app.data.event_store import EventStore
from app.logic.event_sorter import sort_events
from app.ui.event_card import EventCard
from app.ui.event_dialog import EventDialog


class EventList(QWidget):
    """The countdown event list panel.

    Signals:
      event_count_changed(int) — emitted after any add/delete
      event_dates_changed(dict) — dict[date, (count, has_imminent)]
    """

    event_count_changed = Signal(int)
    event_dates_changed = Signal(dict)

    def __init__(self, event_store: EventStore, parent=None) -> None:
        super().__init__(parent)
        self._store = event_store
        self._events: list[Event] = []
        self._cards: dict[str, EventCard] = {}
        self._sort_mode = "date"  # "date" | "created"

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._setup_ui()

        # Load initial data
        self._load_and_render()

    # ── Setup ─────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top toolbar ───────────────────────────────────────
        toolbar = QWidget()
        toolbar.setStyleSheet(f"""
            QWidget {{
                background: {COLOR_BG};
                border-bottom: 1px solid {COLOR_BORDER};
            }}
        """)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(PADDING_MD, PADDING_SM, PADDING_MD, PADDING_SM)
        tb_layout.setSpacing(PADDING_SM)

        # Title
        title = QLabel("倒计时事件")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_TITLE}px;
                font-weight: bold;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        tb_layout.addWidget(title)

        tb_layout.addStretch()

        # Add event button
        add_btn = QPushButton("＋ 新增倒计时")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: {FONT_SIZE_NORMAL}px;
                font-weight: bold;
                background: {COLOR_PRIMARY};
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                background: {COLOR_PRIMARY_HOVER};
            }}
        """)
        add_btn.clicked.connect(self._on_add_event)
        tb_layout.addWidget(add_btn)

        root.addWidget(toolbar)

        # ── Scroll area ───────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)

        # Container widget inside scroll area
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(
            PADDING_MD, PADDING_SM, PADDING_MD, PADDING_MD
        )
        self.container_layout.setSpacing(4)
        self.container_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.container)
        root.addWidget(self.scroll_area, stretch=1)

        # ── Empty state ───────────────────────────────────────
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_icon = QLabel("📅")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_icon.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                background: transparent;
            }}
        """)
        empty_layout.addWidget(empty_icon)

        empty_text = QLabel("暂无倒计时事件")
        empty_text.setAlignment(Qt.AlignCenter)
        empty_text.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_TITLE}px;
                font-weight: bold;
                color: {COLOR_TEXT_SECONDARY};
                background: transparent;
                margin-top: 8px;
            }}
        """)
        empty_layout.addWidget(empty_text)

        empty_hint = QLabel("点击「＋ 新增倒计时」创建")
        empty_hint.setAlignment(Qt.AlignCenter)
        empty_hint.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL}px;
                color: {COLOR_TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        empty_layout.addWidget(empty_hint)

        self.empty_widget.setVisible(False)
        self.container_layout.addWidget(self.empty_widget)

    # ── Event CRUD ────────────────────────────────────────────

    def _load_and_render(self) -> None:
        """Load events from store and rebuild the list."""
        self._events = self._store.load_all()
        self._render_all()

    def _render_all(self) -> None:
        """Rebuild the entire card list, preserving empty state."""
        # Remove all cards (keep empty widget last)
        for card in list(self._cards.values()):
            self.container_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        # Sort events
        sorted_events = sort_events(self._events)

        # Create cards for sorted events
        for event in sorted_events:
            card = self._create_card(event)
            self._cards[event.id] = card
            self.container_layout.insertWidget(
                self.container_layout.count() - 1, card
            )

        # Toggle empty state + emit event dates for calendar dots
        self._update_empty_state()
        self._emit_event_dates()

    def _create_card(self, event: Event) -> EventCard:
        """Create and wire an EventCard."""
        card = EventCard(event)
        card.edit_requested.connect(self._on_edit_event)
        card.delete_requested.connect(self._on_delete_event)
        card.pin_toggled.connect(self._on_pin_toggled)
        return card

    def _on_add_event(self) -> None:
        """Open dialog to add a new event."""
        dialog = EventDialog(self.window())
        if dialog.exec() == EventDialog.Accepted:
            event = dialog.get_event()
            self._events = self._store.add(event)
            self._render_all()
            self.event_count_changed.emit(len(self._events))

    def _on_edit_event(self, event: Event) -> None:
        """Open dialog to edit an existing event."""
        dialog = EventDialog(self.window(), event)
        if dialog.exec() == EventDialog.Accepted:
            updated = dialog.get_event()
            self._events = self._store.update(updated)
            self._render_all()
            self.event_count_changed.emit(len(self._events))

    def _on_delete_event(self, event: Event) -> None:
        """Delete an event after confirmation."""
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self.window(),
            "确认删除",
            f"确定要删除事件「{event.name}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._events = self._store.delete(event.id)
            self._render_all()
            self.event_count_changed.emit(len(self._events))

    def _on_pin_toggled(self, event: Event) -> None:
        """Persist pin state change and re-sort."""
        self._events = self._store.update(event)
        self._render_all()

    def _update_empty_state(self) -> None:
        """Show/hide the empty state widget."""
        has_events = len(self._events) > 0
        self.empty_widget.setVisible(not has_events)

    # ── Real-Time Refresh ─────────────────────────────────────

    def update_countdowns(self, now: datetime) -> None:
        """Refresh countdowns on all visible cards.

        Called every second by the global timer.
        """
        for card in self._cards.values():
            card.update_countdown(now)

    def recheck_statuses(self, now: datetime) -> None:
        """Check if any events crossed a status boundary and re-sort if needed.

        Called once per minute.
        """
        needs_resort = False
        for event in self._events:
            card = self._cards.get(event.id)
            if card:
                old_status = card.event.status(now)
                if old_status != event.status(now):
                    needs_resort = True
                    break
        if needs_resort:
            self._render_all()

    # ── Event Dates Mapping ───────────────────────────────────

    def _emit_event_dates(self) -> None:
        """Build a mapping of date → (count, has_imminent) and emit it.

        This feeds the calendar widget's event-dot indicators.
        """
        mapping: dict[date, tuple[int, bool]] = {}
        now = datetime.now()
        for event in self._events:
            d = event.target_date
            status = event.status(now)
            has_imminent = (status == EventStatus.IMMINENT)
            if d in mapping:
                prev_count, prev_imminent = mapping[d]
                mapping[d] = (prev_count + 1, prev_imminent or has_imminent)
            else:
                mapping[d] = (1, has_imminent)
        self.event_dates_changed.emit(mapping)
