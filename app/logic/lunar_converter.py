"""Lunar calendar conversion wrapper around the `lunardate` library.

Range: 1900–2099. Outside this range, falls back to solar-only display.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

try:
    from lunardate import LunarDate as _LunarDate

    _LUNARDATE_AVAILABLE = True
except ImportError:
    _LUNARDATE_AVAILABLE = False

from app.config import LUNAR_MONTH_NAMES, LUNAR_DAY_NAMES


# ── Public API ───────────────────────────────────────────────

def solar_to_lunar(
    year: int, month: int, day: int
) -> tuple[int, int, int, bool] | None:
    """Convert a solar date to lunar.

    Returns (lunar_year, lunar_month, lunar_day, is_leap_month) or None
    if the date is outside the supported range.
    """
    if not _LUNARDATE_AVAILABLE:
        return None
    try:
        ld = _LunarDate.fromSolarDate(year, month, day)
        is_leap = _LunarDate.leapMonthForYear(ld.year) == ld.month
        return (ld.year, ld.month, ld.day, is_leap)
    except (ValueError, OverflowError):
        return None


def lunar_month_name(month: int) -> str:
    """Return Chinese month name (正月..腊月). Month is 1-based."""
    if 1 <= month <= 12:
        return LUNAR_MONTH_NAMES[month - 1]
    return f"{month}月"


def lunar_day_name(day: int) -> str:
    """Return Chinese day name (初一..三十). Day is 1-based."""
    if 1 <= day <= 30:
        return LUNAR_DAY_NAMES[day - 1]
    return f"{day}日"


def format_lunar_date(year: int, month: int, day: int, is_leap: bool = False) -> str:
    """Format a lunar date as a readable string for display.

    Example: "甲辰年 三月 十五"
    """
    parts = [f"{year}年"]
    if is_leap:
        parts.append(f"闰{lunar_month_name(month)}")
    else:
        parts.append(lunar_month_name(month))
    parts.append(lunar_day_name(day))
    return " ".join(parts)


def format_lunar_day_only(solar_date: date) -> str:
    """Get just the lunar day text for a calendar cell (e.g. '初三').

    Returns empty string if out of range.
    """
    result = solar_to_lunar(solar_date.year, solar_date.month, solar_date.day)
    if result is None:
        return ""
    _, _, day, _ = result
    return lunar_day_name(day)


def format_lunar_full(solar_date: date) -> str:
    """Get the full lunar date string for the current-date display.

    Returns empty string if out of range.
    """
    result = solar_to_lunar(solar_date.year, solar_date.month, solar_date.day)
    if result is None:
        return ""
    year, month, day, is_leap = result
    return format_lunar_date(year, month, day, is_leap)
