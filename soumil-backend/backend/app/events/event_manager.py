"""
Event Manager
-------------
Defines a structured Event: a consistent record of "something
happened" - regardless of whether it came from intrusion,
line-crossing, or loitering detection.

Also provides a simple EventManager to collect events in memory.
A teammate's database can later be plugged in here, without the
analytics code needing to know or care about that.
"""

import time
import uuid


class Event:
    """A single structured surveillance event."""

    def __init__(
        self,
        event_type: str,       # "intrusion", "line_crossing", "loitering"
        camera_id: str,
        track_id: int,
        severity: str = "medium",  # "low", "medium", "high"
        details: dict | None = None,
    ):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.camera_id = camera_id
        self.track_id = track_id
        self.severity = severity
        self.details = details or {}
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        """Convert this event into a plain dictionary - useful for
        sending as JSON over an API, or saving to a database later."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "camera_id": self.camera_id,
            "track_id": self.track_id,
            "severity": self.severity,
            "details": self.details,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"Event({self.event_type}, camera={self.camera_id}, track={self.track_id}, severity={self.severity})"


class EventManager:
    """Collects events in memory. A database can be plugged in later
    by having this class also save to it - the rest of the app
    doesn't need to change."""

    def __init__(self):
        self._events: list[Event] = []

    def create_event(
        self,
        event_type: str,
        camera_id: str,
        track_id: int,
        severity: str = "medium",
        details: dict | None = None,
    ) -> Event:
        event = Event(event_type, camera_id, track_id, severity, details)
        self._events.append(event)
        return event

    def get_all_events(self) -> list[Event]:
        return self._events

    def get_events_for_camera(self, camera_id: str) -> list[Event]:
        return [e for e in self._events if e.camera_id == camera_id]