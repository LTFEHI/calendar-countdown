"""Countdown calculation logic.

Pure functions — no side effects, no UI dependency.
"""
from datetime import datetime
from typing import Optional


def calculate_remaining(
    target: datetime, now: Optional[datetime] = None
) -> dict:
    """Calculate time remaining until target.

    Returns: {"days": int, "hours": int, "minutes": int, "seconds": int}
    All values are zeroed if the target has passed.
    """
    if now is None:
        now = datetime.now()
    total_seconds = max(0, int((target - now).total_seconds()))
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}


def format_remaining(remaining: dict) -> str:
    """Format remaining dict as a readable string.

    > 0 days:  "12天 08时 30分 45秒"
    == 0 days: "03时 15分 22秒"
    expired:   "已结束"
    """
    d, h, m, s = remaining["days"], remaining["hours"], remaining["minutes"], remaining["seconds"]
    if d == 0 and h == 0 and m == 0 and s == 0:
        return "已结束"
    if d > 0:
        return f"{d}天 {h:02d}时 {m:02d}分 {s:02d}秒"
    return f"{h:02d}时 {m:02d}分 {s:02d}秒"


def format_remaining_compact(remaining: dict) -> str:
    """Compact format for when space is tight.

    > 0 days:  "12d 08:30:45"
    == 0 days: "03:15:22"
    expired:   "已结束"
    """
    d, h, m, s = remaining["days"], remaining["hours"], remaining["minutes"], remaining["seconds"]
    if d == 0 and h == 0 and m == 0 and s == 0:
        return "已结束"
    if d > 0:
        return f"{d}d {h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"
