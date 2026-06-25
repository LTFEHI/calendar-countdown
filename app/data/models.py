"""Data models: Event, EventStatus, CalendarMode."""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum, auto
import uuid


class EventStatus(Enum):
    """Event status based on remaining time.

    PRD defines: 即将到期 = 3天内 orange, 已过期 = red.
    """
    NORMAL = auto()    # > IMMINENT_DAYS remaining
    IMMINENT = auto()  # <= IMMINENT_DAYS but not expired
    EXPIRED = auto()   # Target datetime has passed


class CalendarMode(Enum):
    """Calendar display mode."""
    SOLAR = auto()   # 公历
    LUNAR = auto()   # 农历


@dataclass
class Event:
    """A countdown event with target date/time and metadata."""
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    name: str = ""
    target_date: date = field(default_factory=date.today)
    target_time: time | None = None   # None = end-of-day (23:59:59)
    note: str = ""
    is_pinned: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    # ── Derived properties ───────────────────────────────────

    def target_datetime(self) -> datetime:
        """Combine target_date and target_time into a single datetime."""
        from app.config import DEFAULT_TARGET_TIME
        t = self.target_time if self.target_time is not None else DEFAULT_TARGET_TIME
        return datetime.combine(self.target_date, t)

    def status(self, now: datetime | None = None) -> EventStatus:
        """Classify event status relative to now."""
        from app.config import IMMINENT_DAYS
        if now is None:
            now = datetime.now()
        delta = self.target_datetime() - now
        total_seconds = delta.total_seconds()
        if total_seconds <= 0:
            return EventStatus.EXPIRED
        elif total_seconds <= IMMINENT_DAYS * 86400:
            return EventStatus.IMMINENT
        else:
            return EventStatus.NORMAL

    def remaining(self, now: datetime | None = None) -> dict:
        """Return dict with days, hours, minutes, seconds remaining.

        Returns zeroed values if already expired.
        """
        if now is None:
            now = datetime.now()
        delta = self.target_datetime() - now
        total_seconds = max(0, int(delta.total_seconds()))
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}

    def is_expired(self, now: datetime | None = None) -> bool:
        """Convenience: has the event expired?"""
        return self.status(now) == EventStatus.EXPIRED

    # ── Serialization ────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "name": self.name,
            "target_date": self.target_date.isoformat(),
            "target_time": self.target_time.isoformat() if self.target_time else None,
            "note": self.note,
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        """Deserialize from dict. Tolerates missing/extra keys."""
        return cls(
            id=d.get("id", f"evt_{uuid.uuid4().hex[:12]}"),
            name=d.get("name", ""),
            target_date=date.fromisoformat(d["target_date"]),
            target_time=(
                time.fromisoformat(d["target_time"])
                if d.get("target_time") else None
            ),
            note=d.get("note", ""),
            is_pinned=d.get("is_pinned", False),
            created_at=datetime.fromisoformat(
                d.get("created_at", datetime.now().isoformat())
            ),
        )
