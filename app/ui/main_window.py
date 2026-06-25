"""Main application window — frameless, with custom title bar and splitter layout.

This is the top-level window that composes all other widgets.
It owns the global QTimer for real-time refresh.
"""
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRect, QPoint, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QApplication,
)
from PySide6.QtCore import QEvent

from app.config import (
    DEFAULT_WIDTH, DEFAULT_HEIGHT, MIN_WIDTH, MIN_HEIGHT,
    LEFT_RIGHT_RATIO, REFRESH_INTERVAL_MS, APP_NAME,
)
from app.data.models import CalendarMode
from app.data.event_store import EventStore
from app.ui.styles import MAIN_WINDOW_STYLE, GLOBAL_STYLESHEET
from app.ui.title_bar import TitleBar
from app.ui.bottom_bar import BottomBar
from app.ui.left_panel import LeftPanel
from app.ui.right_panel import RightPanel


class MainWindow(QMainWindow):
    """Top-level application window.

    Layout:
      ┌─────────────────────────────────────┐
      │  TitleBar (custom, frameless)       │
      ├───────────────────┬─────────────────┤
      │  LeftPanel (40%)  │ RightPanel (60%)│
      │  - ClockWidget    │ - EventList     │
      │  - CalendarWidget │                 │
      ├───────────────────┴─────────────────┤
      │  BottomBar                          │
      └─────────────────────────────────────┘
    """

    # Signal for global refresh tick
    refresh_tick = Signal(datetime)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        # Frameless + taskbar entry
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # State
        self._calendar_mode = CalendarMode.SOLAR
        self._is_maximized = False
        self._resize_edge = ResizeEdge.NONE
        self._resize_start_pos: QPoint | None = None
        self._resize_start_geom: QRect | None = None

        # Global refresh timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_refresh)
        self._timer.setInterval(REFRESH_INTERVAL_MS)

        # Data store
        self.event_store = EventStore()

        self._setup_ui()
        self._connect_signals()

        # Apply stylesheet
        self.setStyleSheet(GLOBAL_STYLESHEET + MAIN_WINDOW_STYLE)

        # Start the clock
        self._timer.start()

    # ── UI Setup ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Title bar ─────────────────────────────────────────
        self.title_bar = TitleBar()
        root.addWidget(self.title_bar)

        # ── Content area (splitter: left 40% / right 60%) ─────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStretchFactor(0, LEFT_RIGHT_RATIO[0])
        splitter.setStretchFactor(1, LEFT_RIGHT_RATIO[1])

        self.left_panel = LeftPanel()
        self.right_panel = RightPanel(self.event_store)

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([
            int(DEFAULT_WIDTH * LEFT_RIGHT_RATIO[0] / 10),
            int(DEFAULT_WIDTH * LEFT_RIGHT_RATIO[1] / 10),
        ])
        root.addWidget(splitter, stretch=1)

        # ── Bottom bar ────────────────────────────────────────
        self.bottom_bar = BottomBar()
        root.addWidget(self.bottom_bar)

    def _connect_signals(self) -> None:
        # Title bar → window actions
        self.title_bar.minimize_requested.connect(self.showMinimized)
        self.title_bar.maximize_requested.connect(self._toggle_maximize)
        self.title_bar.close_requested.connect(self.close)
        self.title_bar.always_on_top_toggled.connect(self._set_always_on_top)

        # Title bar → calendar mode changes
        self.title_bar.calendar_mode_changed.connect(self._on_calendar_mode_changed)

        # Global timer → left panel real-time updates
        self.refresh_tick.connect(self.left_panel.on_refresh)

        # Global timer → right panel event card updates
        self.refresh_tick.connect(self.right_panel.on_refresh)

        # Right panel → bottom bar event count
        self.right_panel.event_count_changed.connect(self.bottom_bar.set_event_count)

        # Right panel → calendar event dots
        self.right_panel.event_dates_changed.connect(
            self.left_panel.calendar_widget.set_event_dates
        )

        # Initial event count from data store
        self.bottom_bar.set_event_count(self.event_store.count())

    # ── Refresh ───────────────────────────────────────────────

    def _on_refresh(self) -> None:
        now = datetime.now()
        self.refresh_tick.emit(now)

    # ── Calendar Mode ─────────────────────────────────────────

    def _on_calendar_mode_changed(self, mode: CalendarMode) -> None:
        self._calendar_mode = mode
        self.left_panel.set_calendar_mode(mode)
        self.bottom_bar.set_calendar_mode(mode)

    # ── Always On Top ─────────────────────────────────────────

    def _set_always_on_top(self, enabled: bool) -> None:
        if enabled:
            self.setWindowFlags(
                Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window
            )
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.show()  # required on Windows after setWindowFlags

    # ── Maximize / Restore ────────────────────────────────────

    def _toggle_maximize(self) -> None:
        if self._is_maximized:
            self.showNormal()
            self._is_maximized = False
        else:
            self.showMaximized()
            self._is_maximized = True
        self.title_bar.set_maximized_state(self._is_maximized)

    # ── Resizable with custom edges ───────────────────────────

    def event(self, event: QEvent) -> bool:
        """Detect mouse hover at edges for custom resize cursors."""
        if event.type() == QEvent.HoverMove:
            self._update_cursor_for_edge(event.position().toPoint())
        return super().event(event)

    def _update_cursor_for_edge(self, pos: QPoint) -> None:
        edge = self._detect_edge(pos)
        if not self._is_maximized:
            cursor_map = {
                ResizeEdge.LEFT: Qt.SizeHorCursor,
                ResizeEdge.RIGHT: Qt.SizeHorCursor,
                ResizeEdge.TOP: Qt.SizeVerCursor,
                ResizeEdge.BOTTOM: Qt.SizeVerCursor,
                ResizeEdge.TOP_LEFT: Qt.SizeFDiagCursor,
                ResizeEdge.BOTTOM_RIGHT: Qt.SizeFDiagCursor,
                ResizeEdge.TOP_RIGHT: Qt.SizeBDiagCursor,
                ResizeEdge.BOTTOM_LEFT: Qt.SizeBDiagCursor,
            }
            self.setCursor(cursor_map.get(edge, Qt.ArrowCursor))
        else:
            self.setCursor(Qt.ArrowCursor)

    def _detect_edge(self, pos: QPoint) -> "ResizeEdge":
        margin = 8
        r = self.rect()
        x, y = pos.x(), pos.y()
        on_left = x <= margin
        on_right = x >= r.width() - margin
        on_top = y <= margin
        on_bottom = y >= r.height() - margin

        if on_top and on_left:
            return ResizeEdge.TOP_LEFT
        if on_top and on_right:
            return ResizeEdge.TOP_RIGHT
        if on_bottom and on_left:
            return ResizeEdge.BOTTOM_LEFT
        if on_bottom and on_right:
            return ResizeEdge.BOTTOM_RIGHT
        if on_left:
            return ResizeEdge.LEFT
        if on_right:
            return ResizeEdge.RIGHT
        if on_top:
            return ResizeEdge.TOP
        if on_bottom:
            return ResizeEdge.BOTTOM
        return ResizeEdge.NONE

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._resize_edge = self._detect_edge(event.position().toPoint())
            if self._resize_edge != ResizeEdge.NONE:
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geom = self.geometry()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._resize_edge != ResizeEdge.NONE and self._resize_start_pos:
            self._perform_resize(event.globalPosition().toPoint())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._resize_edge = ResizeEdge.NONE
        self._resize_start_pos = None
        self._resize_start_geom = None
        super().mouseReleaseEvent(event)

    def _perform_resize(self, global_pos: QPoint) -> None:
        if not self._resize_start_pos or not self._resize_start_geom:
            return
        delta = global_pos - self._resize_start_pos
        g = self._resize_start_geom
        edge = self._resize_edge

        new_geom = QRect(g)
        if edge in (ResizeEdge.LEFT, ResizeEdge.TOP_LEFT, ResizeEdge.BOTTOM_LEFT):
            new_geom.setLeft(min(g.right() - self.minimumWidth(), g.left() + delta.x()))
        if edge in (ResizeEdge.RIGHT, ResizeEdge.TOP_RIGHT, ResizeEdge.BOTTOM_RIGHT):
            new_geom.setRight(max(g.left() + self.minimumWidth(), g.right() + delta.x()))
        if edge in (ResizeEdge.TOP, ResizeEdge.TOP_LEFT, ResizeEdge.TOP_RIGHT):
            new_geom.setTop(min(g.bottom() - self.minimumHeight(), g.top() + delta.y()))
        if edge in (ResizeEdge.BOTTOM, ResizeEdge.BOTTOM_LEFT, ResizeEdge.BOTTOM_RIGHT):
            new_geom.setBottom(max(g.top() + self.minimumHeight(), g.bottom() + delta.y()))

        self.setGeometry(new_geom)


# ── Resize Edge Enum ─────────────────────────────────────────

from enum import Enum, auto


class ResizeEdge(Enum):
    NONE = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()
