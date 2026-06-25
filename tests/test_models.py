"""Tests for Event data model and countdown logic."""
from datetime import datetime, date, time, timedelta

from app.data.models import Event, EventStatus
from app.logic.countdown import calculate_remaining, format_remaining


class TestEvent:
    """Tests for the Event data model."""

    def test_status_expired(self):
        """Event in the past should be EXPIRED."""
        event = Event(
            name="Past Event",
            target_date=(datetime.now() - timedelta(days=1)).date(),
        )
        assert event.status() == EventStatus.EXPIRED

    def test_status_imminent(self):
        """Event within 3 days should be IMMINENT."""
        event = Event(
            name="Soon",
            target_date=(datetime.now() + timedelta(days=1)).date(),
        )
        assert event.status() == EventStatus.IMMINENT

    def test_status_normal(self):
        """Event more than 3 days away should be NORMAL."""
        event = Event(
            name="Later",
            target_date=(datetime.now() + timedelta(days=10)).date(),
        )
        assert event.status() == EventStatus.NORMAL

    def test_remaining_expired(self):
        """Expired event should return all zeros."""
        event = Event(
            name="Past",
            target_date=(datetime.now() - timedelta(days=1)).date(),
        )
        remaining = event.remaining()
        assert remaining == {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    def test_remaining_positive(self):
        """Future event should have positive remaining time."""
        event = Event(
            name="Future",
            target_date=(datetime.now() + timedelta(days=1)).date(),
        )
        remaining = event.remaining()
        assert remaining["days"] >= 0
        assert remaining["hours"] >= 0
        assert remaining["minutes"] >= 0
        assert remaining["seconds"] >= 0

    def test_to_dict_and_from_dict(self):
        """Round-trip serialization should preserve data."""
        event = Event(
            name="Test",
            target_date=date(2026, 12, 25),
            target_time=time(10, 30, 0),
            note="A note",
            is_pinned=True,
        )
        d = event.to_dict()
        restored = Event.from_dict(d)
        assert restored.name == event.name
        assert restored.target_date == event.target_date
        assert restored.target_time == event.target_time
        assert restored.note == event.note
        assert restored.is_pinned == event.is_pinned

    def test_target_datetime_default_time(self):
        """When target_time is None, default to 23:59:59."""
        event = Event(
            name="No time",
            target_date=date(2026, 7, 15),
            target_time=None,
        )
        dt = event.target_datetime()
        assert dt.hour == 23
        assert dt.minute == 59
        assert dt.second == 59


class TestCountdown:
    """Tests for countdown calculation."""

    def test_calculate_remaining_future(self):
        """Calculate remaining time for a future event."""
        now = datetime(2026, 6, 25, 12, 0, 0)
        target = datetime(2026, 6, 26, 12, 0, 0)
        remaining = calculate_remaining(target, now)
        assert remaining == {"days": 1, "hours": 0, "minutes": 0, "seconds": 0}

    def test_calculate_remaining_past(self):
        """Past target should return all zeros."""
        now = datetime(2026, 6, 26, 12, 0, 0)
        target = datetime(2026, 6, 25, 12, 0, 0)
        remaining = calculate_remaining(target, now)
        assert remaining == {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    def test_format_remaining_normal(self):
        """Format with days."""
        remaining = {"days": 5, "hours": 3, "minutes": 30, "seconds": 15}
        result = format_remaining(remaining)
        assert "5天" in result
        assert "03时" in result

    def test_format_remaining_expired(self):
        """Expired (all zeros) should show '已结束'."""
        remaining = {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
        result = format_remaining(remaining)
        assert result == "已结束"
