"""Tests for countdown logic and event sorting."""
from datetime import datetime, date, timedelta

from app.data.models import Event, EventStatus
from app.logic.countdown import calculate_remaining, format_remaining, format_remaining_compact
from app.logic.event_sorter import sort_events


class TestCountdownLogic:
    """Test countdown calculation edge cases."""

    def test_exactly_now(self):
        """Edge case: target is exactly now."""
        now = datetime(2026, 6, 25, 12, 0, 0)
        target = datetime(2026, 6, 25, 12, 0, 0)
        remaining = calculate_remaining(target, now)
        assert remaining["days"] == 0
        assert remaining["hours"] == 0
        assert remaining["minutes"] == 0
        assert remaining["seconds"] == 0

    def test_sub_second_boundary(self):
        """Just 1 second in the future."""
        now = datetime(2026, 6, 25, 12, 0, 0)
        target = datetime(2026, 6, 25, 12, 0, 1)
        remaining = calculate_remaining(target, now)
        assert remaining["seconds"] == 1
        assert remaining["minutes"] == 0
        assert remaining["hours"] == 0
        assert remaining["days"] == 0

    def test_format_remaining_compact(self):
        """Compact format should work."""
        remaining = {"days": 2, "hours": 5, "minutes": 30, "seconds": 0}
        result = format_remaining_compact(remaining)
        assert "2d" in result
        assert "05:30:00" in result

    def test_format_remaining_only_hours(self):
        """When days=0, show only HH:MM:SS."""
        remaining = {"days": 0, "hours": 5, "minutes": 30, "seconds": 0}
        result = format_remaining(remaining)
        assert "天" not in result


class TestEventSorter:
    """Test event sorting logic."""

    def test_pinned_first(self):
        """Pinned events should come before non-pinned, regardless of date."""
        now = datetime.now()
        pinned = Event(
            name="Pinned Future",
            target_date=(now + timedelta(days=100)).date(),
            is_pinned=True,
        )
        normal = Event(
            name="Normal Soon",
            target_date=(now + timedelta(days=1)).date(),
            is_pinned=False,
        )
        sorted_events = sort_events([normal, pinned])
        assert sorted_events[0].name == "Pinned Future"
        assert sorted_events[1].name == "Normal Soon"

    def test_expired_at_bottom(self):
        """Expired events should be at the bottom."""
        now = datetime.now()
        normal = Event(
            name="Normal",
            target_date=(now + timedelta(days=5)).date(),
        )
        expired = Event(
            name="Expired",
            target_date=(now - timedelta(days=5)).date(),
        )
        sorted_events = sort_events([expired, normal])
        assert sorted_events[0].name == "Normal"
        assert sorted_events[1].name == "Expired"

    def test_multiple_pinned_sorted_by_date(self):
        """Multiple pinned events should be sorted by date ascending."""
        now = datetime.now()
        later = Event(
            name="Later",
            target_date=(now + timedelta(days=30)).date(),
            is_pinned=True,
        )
        sooner = Event(
            name="Sooner",
            target_date=(now + timedelta(days=5)).date(),
            is_pinned=True,
        )
        sorted_events = sort_events([later, sooner])
        assert sorted_events[0].name == "Sooner"
        assert sorted_events[1].name == "Later"
