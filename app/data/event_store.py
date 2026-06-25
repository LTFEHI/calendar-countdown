"""Event persistence layer: JSON file with atomic writes."""
import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from app.config import DATA_FILE
from app.data.models import Event


class EventStore:
    """Manages reading/writing events to a JSON file.

    Uses an atomic write strategy:
      1. Write serialized data to a temp file in the same directory.
      2. os.replace() the temp file onto the real path.
    This prevents data corruption if the process crashes mid-write.
    """

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or DATA_FILE
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Public API ───────────────────────────────────────────

    def load_all(self) -> list[Event]:
        """Load all events from the JSON file.

        Returns an empty list if the file does not exist or is corrupted.
        """
        if not self.file_path.exists():
            return []
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            events_data = data.get("events", [])
            return [Event.from_dict(e) for e in events_data]
        except (json.JSONDecodeError, KeyError, ValueError):
            return []

    def save_all(self, events: list[Event]) -> None:
        """Atomically save all events to the JSON file."""
        payload = {"events": [e.to_dict() for e in events]}
        self._atomic_write(payload)

    def add(self, event: Event) -> list[Event]:
        """Add an event and persist. Returns the updated list."""
        events = self.load_all()
        events.append(event)
        self.save_all(events)
        return events

    def update(self, updated: Event) -> list[Event]:
        """Update an existing event (matched by id). Returns the updated list."""
        events = self.load_all()
        for i, e in enumerate(events):
            if e.id == updated.id:
                events[i] = updated
                break
        self.save_all(events)
        return events

    def delete(self, event_id: str) -> list[Event]:
        """Delete an event by id. Returns the updated list."""
        events = self.load_all()
        events = [e for e in events if e.id != event_id]
        self.save_all(events)
        return events

    def count(self) -> int:
        """Return the number of stored events."""
        return len(self.load_all())

    # ── Internal ─────────────────────────────────────────────

    def _atomic_write(self, payload: dict) -> None:
        """Write payload dict to a temp file, then atomically replace."""
        dir_path = str(self.file_path.parent)
        fd, tmp_path = tempfile.mkstemp(
            dir=dir_path, prefix="events_", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(self.file_path))
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
