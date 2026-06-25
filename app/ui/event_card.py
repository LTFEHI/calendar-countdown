"""Single countdown event card widget with SVG icons.

Displays: event name, target date, remaining time countdown,
status badge (normal/imminent/expired), action buttons (edit/delete/pin).
"""
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QToolButton,
)

from app.config import (
    FONT_FAMILY, FONT_SIZE_EVENT_NAME, FONT_SIZE_NORMAL,
    FONT_SIZE_COUNTDOWN, FONT_SIZE_SMALL, FONT_SIZE_BADGE,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    COLOR_CARD_BG, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT,
    COLOR_WARNING, COLOR_DANGER, COLOR_SUCCESS,
    PADDING_MD, PADDING_SM, BORDER_RADIUS, CARD_MARGIN,
)
from app.data.models import Event, EventStatus
from app.logic.countdown import format_remaining
from app.resources.icons import edit as edit_icon, trash as trash_icon
from app.resources.icons import pin as pin_icon, pin_filled as pin_filled_icon


_ACTION_BTN_STYLE = """
    QToolButton {
        border: none;
        background: transparent;
        padding: 2px;
        min-width: 24px;
        min-height: 24px;
        border-radius: 4px;
    }
    QToolButton:hover {
        background: #E8F0FE;
    }
"""

_DELETE_BTN_STYLE = """
    QToolButton {
        border: none;
        background: transparent;
        padding: 2px;
        min-width: 24px;
        min-height: 24px;
        border-radius: 4px;
    }
    QToolButton:hover {
        background: #FFE8E8;
    }
"""


class EventCard(QFrame):
    """A card widget representing one countdown event.

    Emits:
      edit_requested(Event)  — user clicked edit
      delete_requested(Event) — user clicked delete
      pin_toggled(Event)     — user toggled pin state
    """

    edit_requested = Signal(object)    # Event
    delete_requested = Signal(object)  # Event
    pin_toggled = Signal(object)       # Event

    def __init__(self, event: Event, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("eventCard")
        self._event = event
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        self._setup_ui()
        self._refresh_display()

    # ── Setup ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setStyleSheet(f"""
            QFrame#eventCard {{
                background: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: {BORDER_RADIUS}px;
                margin: {CARD_MARGIN // 2}px 0px;
            }}
            QFrame#eventCard:hover {{
                border-color: {COLOR_PRIMARY};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(PADDING_MD, PADDING_SM + 2, PADDING_MD, PADDING_SM + 2)
        root.setSpacing(4)

        # ── Row 1: Event name + action buttons ─────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.name_label = QLabel(self._event.name or "（未命名事件）")
        self.name_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_EVENT_NAME}px;
                font-weight: bold;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        top_row.addWidget(self.name_label, stretch=1)

        # -- Pin button --
        self.pin_btn = QToolButton()
        self.pin_btn.setIcon(pin_filled_icon(16) if self._event.is_pinned else pin_icon(16))
        self.pin_btn.setToolTip("取消置顶" if self._event.is_pinned else "置顶")
        self.pin_btn.setCursor(Qt.PointingHandCursor)
        self.pin_btn.setStyleSheet(_ACTION_BTN_STYLE)
        self.pin_btn.clicked.connect(self._on_pin_clicked)
        top_row.addWidget(self.pin_btn)

        # -- Edit button --
        edit_btn = QToolButton()
        edit_btn.setIcon(edit_icon(16))
        edit_btn.setToolTip("编辑")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet(_ACTION_BTN_STYLE)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._event))
        top_row.addWidget(edit_btn)

        # -- Delete button --
        del_btn = QToolButton()
        del_btn.setIcon(trash_icon(16))
        del_btn.setToolTip("删除")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet(_DELETE_BTN_STYLE)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._event))
        top_row.addWidget(del_btn)

        root.addLayout(top_row)

        # ── Row 2: Target date ─────────────────────────────
        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL}px;
                color: {COLOR_TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        root.addWidget(self.date_label)

        # ── Row 3: Countdown + status badge ────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        self.countdown_label = QLabel("--天 --时 --分 --秒")
        self.countdown_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_COUNTDOWN}px;
                font-weight: bold;
                font-family: "Consolas", "Cascadia Code", "Fira Code", monospace;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        bottom_row.addWidget(self.countdown_label, stretch=1)

        # Status badge
        self.status_badge = QLabel("正常")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedHeight(22)
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_BADGE}px;
                font-weight: bold;
                padding: 2px 8px;
                border-radius: 10px;
                color: #FFFFFF;
            }}
        """)
        bottom_row.addWidget(self.status_badge)

        root.addLayout(bottom_row)

        # ── Row 4: Note (if present) ───────────────────────
        self.note_label = QLabel()
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL}px;
                color: {COLOR_TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        self.note_label.setVisible(bool(self._event.note))
        root.addWidget(self.note_label)

    # ── Public Refresh ─────────────────────────────────────

    def update_countdown(self, now: datetime) -> None:
        """Refresh the countdown display and status badge.

        Called every second by the global timer.
        """
        status = self._event.status(now)
        remaining = self._event.remaining(now)
        formatted = format_remaining(remaining)
        self.countdown_label.setText(formatted)
        self._update_status_badge(status)

    def _refresh_display(self) -> None:
        """Full display refresh (name, date, note, status)."""
        self.name_label.setText(self._event.name or "（未命名事件）")

        # Target date
        if self._event.target_time:
            self.date_label.setText(
                f"目标：{self._event.target_date} {self._event.target_time.strftime('%H:%M:%S')}"
            )
        else:
            self.date_label.setText(f"目标：{self._event.target_date}")

        # Note
        if self._event.note:
            self.note_label.setText(self._event.note)
            self.note_label.setVisible(True)
        else:
            self.note_label.setVisible(False)

        # Pin icon
        self.pin_btn.setIcon(
            pin_filled_icon(16) if self._event.is_pinned else pin_icon(16)
        )
        self.pin_btn.setToolTip(
            "取消置顶" if self._event.is_pinned else "置顶"
        )

        # Status badge
        status = self._event.status()
        self._update_status_badge(status)

    def _update_status_badge(self, status: EventStatus) -> None:
        """Update the status badge color and text."""
        if status == EventStatus.EXPIRED:
            self.status_badge.setText("已过期")
            self.status_badge.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_BADGE}px;
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 10px;
                    color: #FFFFFF;
                    background: {COLOR_DANGER};
                }}
            """)
            self.countdown_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_COUNTDOWN}px;
                    font-weight: bold;
                    font-family: "Consolas", "Cascadia Code", "Fira Code", monospace;
                    color: {COLOR_DANGER};
                    background: transparent;
                }}
            """)
        elif status == EventStatus.IMMINENT:
            self.status_badge.setText("即将到期")
            self.status_badge.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_BADGE}px;
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 10px;
                    color: #FFFFFF;
                    background: {COLOR_WARNING};
                }}
            """)
            self.countdown_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_COUNTDOWN}px;
                    font-weight: bold;
                    font-family: "Consolas", "Cascadia Code", "Fira Code", monospace;
                    color: {COLOR_WARNING};
                    background: transparent;
                }}
            """)
        else:
            self.status_badge.setText("正常")
            self.status_badge.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_BADGE}px;
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 10px;
                    color: #FFFFFF;
                    background: {COLOR_SUCCESS};
                }}
            """)
            self.countdown_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_COUNTDOWN}px;
                    font-weight: bold;
                    font-family: "Consolas", "Cascadia Code", "Fira Code", monospace;
                    color: {COLOR_TEXT};
                    background: transparent;
                }}
            """)

    # ── Slots ──────────────────────────────────────────────

    def _on_pin_clicked(self) -> None:
        self._event.is_pinned = not self._event.is_pinned
        self.pin_btn.setIcon(
            pin_filled_icon(16) if self._event.is_pinned else pin_icon(16)
        )
        self.pin_toggled.emit(self._event)

    # ── Accessor ───────────────────────────────────────────

    @property
    def event(self) -> Event:
        return self._event
