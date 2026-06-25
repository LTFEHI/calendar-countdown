"""Custom frameless title bar widget with SVG icons.

Handles:
  - Window drag-to-move (mouse press + move on the title bar)
  - Double-click to maximize/restore
  - Minimize, maximize/restore, close, always-on-top toggle buttons
  - Lunar/Solar calendar toggle button (left side)
"""
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QToolButton,
)

from app.data.models import CalendarMode
from app.ui.styles import TITLE_BAR_STYLE
from app.config import APP_NAME, TITLE_BAR_HEIGHT
from app.resources.icons import (
    sun, moon, minimize, maximize, restore, close, pin_filled, pin,
)


class TitleBar(QWidget):
    """Custom title bar replacing the OS-native one (frameless window)."""

    # Signals
    calendar_mode_changed = Signal(CalendarMode)
    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()
    always_on_top_toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(TITLE_BAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._drag_pos: QPoint | None = None
        self._calendar_mode = CalendarMode.SOLAR
        self._is_always_on_top = False

        self._setup_ui()
        self.setStyleSheet(TITLE_BAR_STYLE)

    # ── Public ──────────────────────────────────────────────

    @property
    def calendar_mode(self) -> CalendarMode:
        return self._calendar_mode

    # ── Setup ───────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 4, 0)
        layout.setSpacing(6)

        btn_style = """
            QToolButton {
                border: none;
                border-radius: 0;
                padding: 4px 6px;
                background: transparent;
                min-width: 28px;
                max-height: 28px;
            }
            QToolButton:hover {
                background: #E8ECF1;
                border-radius: 4px;
            }
        """
        close_btn_style = """
            QToolButton {
                border: none;
                border-radius: 0;
                padding: 4px 6px;
                background: transparent;
                min-width: 28px;
                max-height: 28px;
            }
            QToolButton:hover {
                background: #F5222D;
                border-radius: 4px;
            }
        """

        # ── Left: lunar/solar toggle ────────────────────────
        self.lunar_btn = QPushButton()
        self.lunar_btn.setIcon(sun(18))
        self.lunar_btn.setText(" 公历")
        self.lunar_btn.setObjectName("titleBarBtn")
        self.lunar_btn.setToolTip("切换公历/农历显示")
        self.lunar_btn.setCheckable(True)
        self.lunar_btn.setCursor(Qt.PointingHandCursor)
        self.lunar_btn.toggled.connect(self._on_lunar_toggled)
        layout.addWidget(self.lunar_btn)

        # ── Center: app name ────────────────────────────────
        layout.addStretch()
        self.title_label = QLabel(APP_NAME)
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        layout.addStretch()

        # ── Right: window control buttons ───────────────────
        # Always-on-top
        self.pin_btn = QToolButton()
        self.pin_btn.setIcon(pin(16))
        self.pin_btn.setToolTip("窗口置顶")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setCursor(Qt.PointingHandCursor)
        self.pin_btn.setStyleSheet(btn_style)
        self.pin_btn.toggled.connect(self._on_pin_toggled)
        layout.addWidget(self.pin_btn)

        # Minimize
        self.min_btn = QToolButton()
        self.min_btn.setIcon(minimize(16))
        self.min_btn.setToolTip("最小化")
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.minimize_requested.emit)
        layout.addWidget(self.min_btn)

        # Maximize / Restore
        self.max_btn = QToolButton()
        self.max_btn.setIcon(maximize(16))
        self.max_btn.setToolTip("最大化")
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.setStyleSheet(btn_style)
        self.max_btn.clicked.connect(self.maximize_requested.emit)
        layout.addWidget(self.max_btn)

        # Close
        self.close_btn = QToolButton()
        self.close_btn.setIcon(close(16))
        self.close_btn.setToolTip("关闭")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet(close_btn_style)
        self.close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.close_btn)

    # ── Slots ───────────────────────────────────────────────

    def _on_lunar_toggled(self, checked: bool) -> None:
        self._calendar_mode = CalendarMode.LUNAR if checked else CalendarMode.SOLAR
        if checked:
            self.lunar_btn.setIcon(moon(18))
            self.lunar_btn.setText(" 农历")
        else:
            self.lunar_btn.setIcon(sun(18))
            self.lunar_btn.setText(" 公历")
        self.calendar_mode_changed.emit(self._calendar_mode)

    def _on_pin_toggled(self, checked: bool) -> None:
        self._is_always_on_top = checked
        self.pin_btn.setIcon(pin_filled(16) if checked else pin(16))
        self.always_on_top_toggled.emit(checked)

    # ── Mouse events (window dragging) ──────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            window = self.window()
            if window:
                window.move(window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.maximize_requested.emit()
        super().mouseDoubleClickEvent(event)

    def set_maximized_state(self, maximized: bool) -> None:
        """Update the maximize button icon between maximize/restore."""
        self.max_btn.setIcon(restore(16) if maximized else maximize(16))
        self.max_btn.setToolTip("还原" if maximized else "最大化")
