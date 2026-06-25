"""Custom month calendar widget with lunar calendar support and event dots.

Renders a 6×7 grid (42 cells) for any month.
Supports:
  - Previous/next month navigation (SVG chevron icons)
  - "Today" shortcut button (jumps to current month)
  - Today highlighting (blue background)
  - Weekend dimming (grey text)
  - Past-date dimming within current month
  - Lunar date overlay (small text below solar date)
  - Event indicator dots on dates that have countdown events
  - Day click signal

Built from scratch rather than using QCalendarWidget, because
QCalendarWidget cannot render two date systems (solar + lunar)
per cell simultaneously.
"""
import calendar
from datetime import date

from PySide6.QtCore import Qt, Signal, QSize, QPoint
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPaintEvent, QMouseEvent,
    QEnterEvent,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QSizePolicy, QFrame, QToolButton,
)

from app.config import (
    FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_SMALL, FONT_SIZE_LUNAR,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_TEXT_DIM,
    COLOR_PRIMARY, COLOR_BORDER, COLOR_TODAY, COLOR_WEEKEND,
    COLOR_CARD_BG, COLOR_WARNING, COLOR_SUCCESS,
    PADDING_SM, PADDING_MD, BORDER_RADIUS, COLOR_PRIMARY_LIGHT,
)
from app.data.models import CalendarMode
from app.logic.lunar_converter import format_lunar_day_only
from app.resources.icons import (
    chevron_left, chevron_right, calendar as calendar_icon,
    event_dot, chevron_double_left, chevron_double_right,
)


WEEKDAY_LABELS = ["一", "二", "三", "四", "五", "六", "日"]


class DayCell(QPushButton):
    """A single day cell in the calendar grid.

    Draws:
      - The day number (solar)
      - Lunar day text below (when in lunar mode)
      - Today highlight circle
      - Event indicator dot(s) below the number
    """

    clicked_with_date = Signal(date)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date: date | None = None
        self._is_today = False
        self._is_current_month = True
        self._is_weekend = False
        self._has_events = False
        self._event_count = 0
        self._event_imminent = False  # at least one event is imminent → orange dot

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(34, 34)
        self.setCursor(Qt.PointingHandCursor)

        # Base style — no borders, transparent bg; today is handled via property
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                background: transparent;
                text-align: center;
                font-size: 13px;
                padding: 2px;
            }
            QPushButton:hover {
                background: #E8F0FE;
            }
            QPushButton[today="true"] {
                background: #4A90D9;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton[today="true"]:hover {
                background: #357ABD;
            }
        """)
        self.clicked.connect(self._on_click)

    # ── Properties ─────────────────────────────────────────

    @property
    def cell_date(self) -> date | None:
        return self._date

    # ── Public methods ─────────────────────────────────────

    def configure(
        self,
        cell_date: date,
        is_today: bool = False,
        is_current_month: bool = True,
        has_events: bool = False,
        event_count: int = 0,
        event_imminent: bool = False,
    ) -> None:
        self._date = cell_date
        self._is_today = is_today
        self._is_current_month = is_current_month
        self._is_weekend = cell_date.weekday() >= 5
        self._has_events = has_events
        self._event_count = event_count
        self._event_imminent = event_imminent

        self.setText(str(cell_date.day))
        self.setProperty("today", is_today)
        self.setEnabled(is_current_month)
        self.setToolTip(str(cell_date))

        # Refresh style (forces Qt to re-evaluate property selectors)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # ── Paint event dots ───────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        if not self._has_events or not self._date:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        dot_y = h - 8          # near the bottom
        dot_radius = 2.5
        spacing = 7

        # Determine color: orange if any event is imminent, else primary-blue
        dot_color = QColor(COLOR_WARNING if self._event_imminent else COLOR_PRIMARY)

        # Show up to 3 dots
        count = min(self._event_count, 3)
        total_width = (count - 1) * spacing
        start_x = w / 2.0 - total_width / 2.0

        for i in range(count):
            painter.setPen(Qt.NoPen)
            painter.setBrush(dot_color)
            cx = start_x + i * spacing
            painter.drawEllipse(QPoint(int(cx), dot_y), dot_radius, dot_radius)

        painter.end()

    # ── Internal ───────────────────────────────────────────

    def _on_click(self) -> None:
        if self._date:
            self.clicked_with_date.emit(self._date)


# ═══════════════════════════════════════════════════════════════
#  Calendar Widget
# ═══════════════════════════════════════════════════════════════

class CalendarWidget(QWidget):
    """Custom month calendar with lunar overlay and event indicators.

    Emits:
      day_clicked(date) — when the user clicks a calendar day
    """

    day_clicked = Signal(date)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._display_year: int = date.today().year
        self._display_month: int = date.today().month
        self._calendar_mode = CalendarMode.SOLAR
        self._today = date.today()

        # Event date → (count, has_imminent) mapping
        self._event_dates: dict[date, tuple[int, bool]] = {}

        self._day_cells: list[list[DayCell]] = []
        self._lunar_labels: list[list[QLabel]] = []

        self._setup_ui()
        self._build_grid()

    # ── Setup ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(PADDING_MD, PADDING_SM + 4, PADDING_MD, PADDING_MD)
        root.setSpacing(4)

        # ── Month navigation ───────────────────────────────
        nav = QHBoxLayout()
        nav.setSpacing(4)

        # -- Today button --
        self.today_btn = QToolButton()
        self.today_btn.setIcon(calendar_icon(18))
        self.today_btn.setToolTip("回到今天")
        self.today_btn.setFixedSize(30, 30)
        self.today_btn.setCursor(Qt.PointingHandCursor)
        self.today_btn.clicked.connect(self.go_to_today)
        self.today_btn.setStyleSheet(f"""
            QToolButton {{
                border: 1px solid {COLOR_BORDER};
                border-radius: {BORDER_RADIUS // 2}px;
                background: {COLOR_CARD_BG};
            }}
            QToolButton:hover {{ background: {COLOR_PRIMARY_LIGHT}; }}
        """)
        nav.addWidget(self.today_btn)

        # -- Prev-month button --
        self.prev_btn = QToolButton()
        self.prev_btn.setIcon(chevron_left(20))
        self.prev_btn.setToolTip("上一月")
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self._go_prev_month)
        self.prev_btn.setStyleSheet(self.today_btn.styleSheet())
        nav.addWidget(self.prev_btn)

        # -- Month label --
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                font-weight: bold;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        nav.addWidget(self.month_label, stretch=1)

        # -- Next-month button --
        self.next_btn = QToolButton()
        self.next_btn.setIcon(chevron_right(20))
        self.next_btn.setToolTip("下一月")
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._go_next_month)
        self.next_btn.setStyleSheet(self.today_btn.styleSheet())
        nav.addWidget(self.next_btn)

        # -- Year-jump buttons (double chevrons) --
        self.prev_year_btn = QToolButton()
        self.prev_year_btn.setIcon(chevron_double_left(18))
        self.prev_year_btn.setToolTip("上一年")
        self.prev_year_btn.setFixedSize(28, 30)
        self.prev_year_btn.setCursor(Qt.PointingHandCursor)
        self.prev_year_btn.clicked.connect(self._go_prev_year)
        self.prev_year_btn.setStyleSheet(self.today_btn.styleSheet())
        nav.addWidget(self.prev_year_btn)

        self.next_year_btn = QToolButton()
        self.next_year_btn.setIcon(chevron_double_right(18))
        self.next_year_btn.setToolTip("下一年")
        self.next_year_btn.setFixedSize(28, 30)
        self.next_year_btn.setCursor(Qt.PointingHandCursor)
        self.next_year_btn.clicked.connect(self._go_next_year)
        self.next_year_btn.setStyleSheet(self.today_btn.styleSheet())
        nav.addWidget(self.next_year_btn)

        root.addLayout(nav)

        # ── Weekday header ─────────────────────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        for i, name in enumerate(WEEKDAY_LABELS):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            color = COLOR_WEEKEND if i >= 5 else COLOR_TEXT_SECONDARY
            lbl.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_SMALL}px;
                    color: {color};
                    background: transparent;
                    padding: 4px;
                    font-weight: bold;
                }}
            """)
            header_layout.addWidget(lbl)
        root.addLayout(header_layout)

        # ── Day grid ───────────────────────────────────────
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(1)
        root.addWidget(self.grid_widget, stretch=1)

    # ── Grid Building ──────────────────────────────────────

    def _build_grid(self) -> None:
        """Rebuild the 6×7 day grid for the current display month."""
        # Clear existing grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._day_cells = []
        self._lunar_labels = []

        year, month = self._display_year, self._display_month
        self.month_label.setText(f"{year}年 {month}月")

        first_day = date(year, month, 1)
        start_weekday = first_day.weekday()  # 0=Monday .. 6=Sunday
        days_in_month = calendar.monthrange(year, month)[1]

        # Previous month tail
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
        prev_days = calendar.monthrange(prev_year, prev_month)[1]

        for week in range(6):
            row_cells: list[DayCell] = []
            row_lunar: list[QLabel] = []
            for day_col in range(7):
                idx = week * 7 + day_col
                day_num = idx - start_weekday + 1

                # ── Container for day button + lunar label ──
                container = QWidget()
                container.setSizePolicy(
                    QSizePolicy.Expanding, QSizePolicy.Expanding
                )
                container.setMinimumSize(34, 36)
                vbox = QVBoxLayout(container)
                vbox.setContentsMargins(1, 2, 1, 2)
                vbox.setSpacing(0)
                vbox.setAlignment(Qt.AlignCenter)

                day_btn = DayCell()
                lunar_label = QLabel("")
                lunar_label.setAlignment(Qt.AlignCenter)
                lunar_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: {FONT_SIZE_LUNAR}px;
                        color: {COLOR_TEXT_SECONDARY};
                        background: transparent;
                    }}
                """)

                vbox.addWidget(day_btn, alignment=Qt.AlignCenter)
                vbox.addWidget(lunar_label, alignment=Qt.AlignCenter)

                # ── Determine which date this cell represents ──
                if day_num < 1 or day_num > days_in_month:
                    # Adjacent month cell
                    ctrl_month = prev_month if day_num < 1 else (
                        month + 1 if month < 12 else 1
                    )
                    ctrl_year = prev_year if day_num < 1 else (
                        year if month < 12 else year + 1
                    )
                    adj_num = (prev_days + day_num) if day_num < 1 else (
                        day_num - days_in_month
                    )
                    cell_date = date(ctrl_year, ctrl_month, adj_num)
                    is_current = False
                else:
                    cell_date = date(year, month, day_num)
                    is_current = True

                # ── Event info for this date ────────────────
                ev_info = self._event_dates.get(cell_date, (0, False))

                day_btn.configure(
                    cell_date,
                    is_today=(cell_date == self._today),
                    is_current_month=is_current,
                    has_events=(ev_info[0] > 0),
                    event_count=ev_info[0],
                    event_imminent=ev_info[1],
                )
                day_btn.clicked_with_date.connect(self.day_clicked.emit)

                # ── Per-cell color styling ──────────────────
                self._apply_cell_colors(day_btn, cell_date, is_current)

                self.grid_layout.addWidget(container, week, day_col)
                row_cells.append(day_btn)
                row_lunar.append(lunar_label)

            self._day_cells.append(row_cells)
            self._lunar_labels.append(row_lunar)

        # Always show lunar day text below each solar date
        self._update_lunar_overlay()

    def _apply_cell_colors(self, btn: DayCell, cell_date: date,
                           is_current: bool) -> None:
        """Apply text color: only adjacent-month dates are dimmed.

        Within the current month, all dates (past, today, future) use
        their normal color (weekend=red, weekday=normal).
        """
        base = btn.styleSheet()
        if not is_current:
            # Dates from prev/next month → grey
            btn.setStyleSheet(base + f" QPushButton {{ color: {COLOR_TEXT_DIM}; }}")
        elif cell_date.weekday() >= 5:
            # Weekend in current month → red
            btn.setStyleSheet(base + f" QPushButton {{ color: {COLOR_WEEKEND}; }}")
        else:
            # Weekday in current month → normal
            btn.setStyleSheet(base + f" QPushButton {{ color: {COLOR_TEXT}; }}")

    # ── Lunar Overlay ──────────────────────────────────────

    def _update_lunar_overlay(self) -> None:
        """Set lunar day text on each cell's label."""
        for week in range(6):
            for col in range(7):
                btn = self._day_cells[week][col]
                lbl = self._lunar_labels[week][col]
                if btn.cell_date:
                    lunar = format_lunar_day_only(btn.cell_date)
                    lbl.setText(lunar)
                    lbl.setVisible(True)
                else:
                    lbl.setVisible(False)

# ── Navigation ─────────────────────────────────────────

    def _go_prev_month(self) -> None:
        if self._display_month == 1:
            self._display_month = 12
            self._display_year -= 1
        else:
            self._display_month -= 1
        self._build_grid()

    def _go_next_month(self) -> None:
        if self._display_month == 12:
            self._display_month = 1
            self._display_year += 1
        else:
            self._display_month += 1
        self._build_grid()

    def _go_prev_year(self) -> None:
        self._display_year -= 1
        self._build_grid()

    def _go_next_year(self) -> None:
        self._display_year += 1
        self._build_grid()

    # ── Public ─────────────────────────────────────────────

    def set_calendar_mode(self, mode: CalendarMode) -> None:
        self._calendar_mode = mode
        self._update_lunar_overlay()

    def go_to_today(self) -> None:
        """Reset display to today's month and rebuild."""
        self._display_year = self._today.year
        self._display_month = self._today.month
        self._build_grid()

    def set_event_dates(self, event_dates: dict[date, tuple[int, bool]]) -> None:
        """Supply a mapping of date → (event_count, has_imminent).

        Dates with count > 0 will display an indicator dot.
        has_imminent=True → orange dot; otherwise → blue dot.

        Call this whenever the event list changes, then _build_grid()
        is automatically invoked.
        """
        self._event_dates = event_dates
        self._build_grid()

    def refresh_event_dots(self, event_dates: dict[date, tuple[int, bool]]) -> None:
        """Refresh event dots without fully rebuilding the grid.

        Faster than set_event_dates() — only updates existing cells.
        """
        self._event_dates = event_dates
        for week in range(6):
            for col in range(7):
                btn = self._day_cells[week][col]
                if btn.cell_date:
                    ev_info = event_dates.get(btn.cell_date, (0, False))
                    btn.configure(
                        btn.cell_date,
                        is_today=(btn.cell_date == self._today),
                        is_current_month=btn.isEnabled(),
                        has_events=(ev_info[0] > 0),
                        event_count=ev_info[0],
                        event_imminent=ev_info[1],
                    )
