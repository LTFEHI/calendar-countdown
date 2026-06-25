"""Event sorting logic.

PRD rules:
  1. Pinned events at the top, sorted by target date ascending.
  2. Active (normal + imminent) events in the middle, sorted by target date ascending.
  3. Expired events at the bottom, sorted by target date descending (most recently expired first).
"""
from datetime import datetime
from typing import Optional

from app.data.models import Event, EventStatus


def sort_key(event: Event, now: Optional[datetime] = None) -> tuple:
    """Return a sort key tuple for the given event.

    Group ordering:
      0 — pinned events (top)
      1 — active events (normal + imminent)
      2 — expired events (bottom)

    Within each group, events are sorted by target datetime:
      - Groups 0 & 1: ascending (nearest first).
      - Group 2: descending (most recently expired first).
    """
    if now is None:
        now = datetime.now()
    status = event.status(now)
    target_ts = event.target_datetime().timestamp()

    if event.is_pinned:
        group = 0
        date_val = target_ts
    elif status == EventStatus.EXPIRED:
        group = 2
        date_val = -target_ts  # negate for descending sort
    else:
        group = 1
        date_val = target_ts

    return (group, date_val)


def sort_events(
    events: list[Event], now: Optional[datetime] = None
) -> list[Event]:
    """Return a new list of events sorted according to PRD rules."""
    return sorted(events, key=lambda e: sort_key(e, now))
