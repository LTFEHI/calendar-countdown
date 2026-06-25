"""Centralized QSS stylesheets and color constants.

All styling lives here so the look-and-feel can be adjusted in one place.
"""
from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_LIGHT,
    COLOR_BG, COLOR_CARD_BG,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_TEXT_DIM,
    COLOR_WARNING, COLOR_DANGER, COLOR_SUCCESS,
    COLOR_BORDER, COLOR_TODAY, COLOR_WEEKEND, COLOR_DISABLED,
    COLOR_TITLE_BAR, COLOR_BOTTOM_BAR,
    FONT_FAMILY, FONT_SIZE_CLOCK, FONT_SIZE_DATE, FONT_SIZE_TITLE,
    FONT_SIZE_NORMAL, FONT_SIZE_SMALL, FONT_SIZE_LUNAR,
    FONT_SIZE_COUNTDOWN, FONT_SIZE_EVENT_NAME, FONT_SIZE_BADGE,
    PADDING_LG, PADDING_MD, PADDING_SM, CARD_MARGIN,
    BORDER_RADIUS, TITLE_BAR_HEIGHT, BOTTOM_BAR_HEIGHT,
)

# ── Global App Stylesheet ────────────────────────────────────

GLOBAL_STYLESHEET = f"""
/* ── Global Reset ─────────────────────────── */
QWidget {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_NORMAL}px;
    color: {COLOR_TEXT};
    background-color: {COLOR_BG};
}}

/* ── Scrollbars ───────────────────────────── */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    width: 6px;
    background: transparent;
    border: none;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_TEXT_DIM};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_SECONDARY};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    border: none;
}}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}

/* ── Scrollbars Horizontal ────────────────── */
QScrollBar:horizontal {{
    height: 6px;
    background: transparent;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {COLOR_TEXT_DIM};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── Buttons (Base) ───────────────────────── */
QPushButton {{
    border: none;
    border-radius: {BORDER_RADIUS // 2}px;
    padding: {PADDING_SM}px {int(PADDING_MD * 1.2)}px;
    background: transparent;
    color: {COLOR_TEXT};
}}
QPushButton:hover {{
    background: {COLOR_PRIMARY_LIGHT};
}}
QPushButton:pressed {{
    background: {COLOR_PRIMARY}30;
}}

/* ── Primary Button ───────────────────────── */
QPushButton[cssClass="primary"] {{
    background: {COLOR_PRIMARY};
    color: #FFFFFF;
    font-weight: bold;
    border-radius: {BORDER_RADIUS // 2}px;
    padding: {PADDING_SM + 2}px {PADDING_LG}px;
}}
QPushButton[cssClass="primary"]:hover {{
    background: {COLOR_PRIMARY_HOVER};
}}

/* ── Input Fields ─────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    border: 1px solid {COLOR_BORDER};
    border-radius: {BORDER_RADIUS // 2}px;
    padding: {PADDING_SM}px;
    background: {COLOR_CARD_BG};
    color: {COLOR_TEXT};
    font-size: {FONT_SIZE_NORMAL}px;
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLOR_PRIMARY};
}}

/* ── Tooltip ──────────────────────────────── */
QToolTip {{
    background: {COLOR_TEXT};
    color: #FFFFFF;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: {FONT_SIZE_SMALL}px;
}}
"""

# ── Widget-Specific Styles ───────────────────────────────────

MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {COLOR_BG};
}}
"""

TITLE_BAR_STYLE = f"""
QWidget#titleBar {{
    background: {COLOR_TITLE_BAR};
    border-bottom: 1px solid {COLOR_BORDER};
    min-height: {TITLE_BAR_HEIGHT}px;
    max-height: {TITLE_BAR_HEIGHT}px;
}}
QLabel#titleLabel {{
    font-size: {FONT_SIZE_TITLE}px;
    font-weight: bold;
    color: {COLOR_TEXT};
    background: transparent;
}}
QPushButton#titleBarBtn {{
    border: none;
    border-radius: 0;
    padding: 6px 10px;
    background: transparent;
    font-size: {FONT_SIZE_NORMAL}px;
    color: {COLOR_TEXT};
    min-width: 28px;
    max-height: 28px;
}}
QPushButton#titleBarBtn:hover {{
    background: {COLOR_BORDER};
}}
QPushButton#closeBtn {{
    border: none;
    border-radius: 0;
    padding: 6px 10px;
    background: transparent;
    font-size: {FONT_SIZE_NORMAL}px;
    color: {COLOR_TEXT};
    min-width: 28px;
    max-height: 28px;
}}
QPushButton#closeBtn:hover {{
    background: {COLOR_DANGER};
    color: #FFFFFF;
}}
"""

BOTTOM_BAR_STYLE = f"""
QWidget#bottomBar {{
    background: {COLOR_BOTTOM_BAR};
    border-top: 1px solid {COLOR_BORDER};
    min-height: {BOTTOM_BAR_HEIGHT}px;
    max-height: {BOTTOM_BAR_HEIGHT}px;
}}
QLabel#bottomBarLabel {{
    background: transparent;
    font-size: {FONT_SIZE_SMALL}px;
    color: {COLOR_TEXT_SECONDARY};
}}
"""

LEFT_PANEL_STYLE = f"""
QWidget#leftPanel {{
    background: {COLOR_CARD_BG};
    border-right: 1px solid {COLOR_BORDER};
    border-radius: 0;
}}
"""

RIGHT_PANEL_STYLE = f"""
QWidget#rightPanel {{
    background: {COLOR_BG};
    border: none;
}}
"""

EVENT_CARD_STYLE = f"""
QFrame#eventCard {{
    background: {COLOR_CARD_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: {BORDER_RADIUS}px;
    margin: {CARD_MARGIN // 2}px 0px;
    padding: {PADDING_MD}px;
}}
QFrame#eventCard:hover {{
    border-color: {COLOR_PRIMARY};
    background: {COLOR_CARD_BG};
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background: {COLOR_CARD_BG};
    border-radius: {BORDER_RADIUS}px;
}}
"""

# ── Color Map (for programmatic use) ─────────────────────────

STATUS_COLORS = {
    "normal": COLOR_SUCCESS,
    "imminent": COLOR_WARNING,
    "expired": COLOR_DANGER,
}

STATUS_LABELS = {
    "normal": "正常",
    "imminent": "即将到期",
    "expired": "已过期",
}
