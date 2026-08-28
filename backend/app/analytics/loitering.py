"""
Loitering detection
--------------------
Checks whether a tracked object has stayed in roughly the same
position for longer than a set time threshold.

Does NOT know about cameras, YOLO, or events - just: given tracked
positions over time, who has been standing still too long?
"""

import time
import math


class LoiteringDetector:
    def __init__(self, time_threshold_seconds: float = 15.0, movement_tolerance_pixels: float = 50.0):
        # How long someone must stay before we call it loitering.
        self.time_threshold_seconds = time_threshold_seconds
        # How much they're "allowed" to move and still count as
        # "roughly the same spot" (people shift their feet, etc).
        self.movement_tolerance_pixels = movement_tolerance_pixels

        # For each track_id: (first_seen_time, first_seen_x, first_seen_y)
        self._track_start: dict[int, tuple[float, float, float]] = {}
        # Track IDs we've already reported as loitering, so we don't
        # repeat the same alert every single frame.
        self._already_reported: set[int] = set()

    def check(self, tracked_objects: list) -> list[int]:
        """
        Given a list of TrackedObject, returns the list of track_ids
        that are NEWLY confirmed as loitering this check.
        """
        newly_loitering = []
        current_ids = set()

        for obj in tracked_objects:
            x1, y1, x2, y2 = obj.box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            now = time.time()
            current_ids.add(obj.track_id)

            if obj.track_id not in self._track_start:
                # First time we've seen this track - start the clock.
                self._track_start[obj.track_id] = (now, center_x, center_y)
                continue

            start_time, start_x, start_y = self._track_start[obj.track_id]
            distance_moved = math.hypot(center_x - start_x, center_y - start_y)

            if distance_moved > self.movement_tolerance_pixels:
                # They've moved too far from where we first saw them -
                # reset the clock, they're not loitering, just moving around.
                self._track_start[obj.track_id] = (now, center_x, center_y)
                self._already_reported.discard(obj.track_id)
                continue

            elapsed = now - start_time
            if elapsed >= self.time_threshold_seconds and obj.track_id not in self._already_reported:
                newly_loitering.append(obj.track_id)
                self._already_reported.add(obj.track_id)

        # Clean up tracks that are no longer present (they left frame).
        gone_ids = set(self._track_start.keys()) - current_ids
        for gone_id in gone_ids:
            del self._track_start[gone_id]
            self._already_reported.discard(gone_id)

        return newly_loitering