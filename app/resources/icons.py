"""Inline SVG icons for the application.

All icons are pure SVG paths embedded as Python strings, so no external
image files are needed.  Qt renders them natively via QIcon/QPixmap.
"""

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication


# ═══════════════════════════════════════════════════════════════
#  SVG Data
# ═══════════════════════════════════════════════════════════════

SVG_CHEVRON_LEFT = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_CHEVRON_RIGHT = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 6L15 12L9 18" stroke="currentColor" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_CHEVRON_DOUBLE_LEFT = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M11 17L5 12L11 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M18 17L12 12L18 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_CHEVRON_DOUBLE_RIGHT = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 17L12 12L6 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M13 17L19 12L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_CALENDAR = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
  <path d="M16 2v4M8 2v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M3 10h18" stroke="currentColor" stroke-width="2"/>
</svg>'''

SVG_TODAY = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="3" fill="currentColor"/>
  <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
  <path d="M16 2v4M8 2v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M3 10h18" stroke="currentColor" stroke-width="2"/>
</svg>'''

SVG_CLOCK = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
  <path d="M12 7v5l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_EVENT_DOT = '''<svg viewBox="0 0 8 8" xmlns="http://www.w3.org/2000/svg">
  <circle cx="4" cy="4" r="4" fill="currentColor"/>
</svg>'''

SVG_PLUS = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5"
        stroke-linecap="round"/>
</svg>'''

SVG_PIN = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L15 9H9L12 2Z" fill="currentColor"/>
  <path d="M12 9v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="19" r="1.5" fill="currentColor"/>
</svg>'''

SVG_EDIT = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_TRASH = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>'''

SVG_SUN = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="2"/>
  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
        stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>'''

SVG_MOON = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 12.79A9 9 0 1111.21 4 7 7 0 0020 12.79z"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

SVG_MINIMIZE = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>'''

SVG_MAXIMIZE = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="5" width="14" height="14" rx="1" stroke="currentColor" stroke-width="2"/>
</svg>'''

SVG_RESTORE = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="6" y="8" width="10" height="10" rx="1" stroke="currentColor" stroke-width="2"/>
  <rect x="8" y="4" width="10" height="10" rx="1" stroke="currentColor" stroke-width="2" fill="white"/>
</svg>'''

SVG_CLOSE = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.5"
        stroke-linecap="round"/>
</svg>'''

SVG_PIN_FILLED = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L15 9H9L12 2Z" fill="currentColor"/>
  <path d="M12 9v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="19" r="2" fill="currentColor"/>
  <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.5"/>
</svg>'''


# ═══════════════════════════════════════════════════════════════
#  Helper: Render SVG → QIcon
# ═══════════════════════════════════════════════════════════════

def _svg_to_icon(svg_data: str, color: str = "#2C3E50",
                 size: int = 20) -> QIcon:
    """Render an SVG string into a QIcon at the given size and color.

    We inject the color into the SVG so `currentColor` works, then
    render the SVG to a QPixmap for the icon.
    """
    # Replace currentColor with the desired color
    colored = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
    colored = colored.replace('fill="currentColor"', f'fill="{color}"')

    # Render to pixmap
    renderer = QSvgRenderer(bytes(colored, "utf-8"))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # transparent background
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


def _make_icon(svg_data: str, size: int = 20) -> QIcon:
    """Create a QIcon from SVG that inherits the widget's palette color.

    We leave `currentColor` as-is; Qt's QSvgRenderer will use the
    widget's palette text color at render time.  But since we render to
    a fixed pixmap, we need to pick a color now.  Default to the app's
    main text color.
    """
    from app.config import COLOR_TEXT, COLOR_TEXT_SECONDARY
    return _svg_to_icon(svg_data, COLOR_TEXT, size)


# ═══════════════════════════════════════════════════════════════
#  Public icon factory functions
# ═══════════════════════════════════════════════════════════════

def chevron_left(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CHEVRON_LEFT, c, size)

def chevron_right(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CHEVRON_RIGHT, c, size)

def chevron_double_left(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CHEVRON_DOUBLE_LEFT, c, size)

def chevron_double_right(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CHEVRON_DOUBLE_RIGHT, c, size)

def calendar(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CALENDAR, c, size)

def today(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_TODAY, c, size)

def clock(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CLOCK, c, size)

def event_dot(size: int = 8, color: str | None = None) -> QIcon:
    c = color or from_config_primary()
    return _svg_to_icon(SVG_EVENT_DOT, c, size)

def plus(size: int = 20, color: str = "#FFFFFF") -> QIcon:
    return _svg_to_icon(SVG_PLUS, color, size)

def pin(size: int = 16, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_PIN, c, size)

def pin_filled(size: int = 16, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_PIN_FILLED, c, size)

def edit(size: int = 16, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_EDIT, c, size)

def trash(size: int = 16, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_TRASH, c, size)

def sun(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_primary()
    return _svg_to_icon(SVG_SUN, c, size)

def moon(size: int = 20, color: str | None = None) -> QIcon:
    c = color or from_config_primary()
    return _svg_to_icon(SVG_MOON, c, size)

def minimize(size: int = 18, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_MINIMIZE, c, size)

def maximize(size: int = 18, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_MAXIMIZE, c, size)

def restore(size: int = 18, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_RESTORE, c, size)

def close(size: int = 18, color: str | None = None) -> QIcon:
    c = color or from_config_text()
    return _svg_to_icon(SVG_CLOSE, c, size)


# ═══════════════════════════════════════════════════════════════
#  Internal helpers
# ═══════════════════════════════════════════════════════════════

def from_config_text() -> str:
    from app.config import COLOR_TEXT
    return COLOR_TEXT

def from_config_primary() -> str:
    from app.config import COLOR_PRIMARY
    return COLOR_PRIMARY
