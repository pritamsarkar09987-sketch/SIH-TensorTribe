"""
Intrusion detection (+10-Meter Restricted Perimeter Zone)
----------------------------------------------------------
Checks whether a detected person's bounding box enters or intersects
with the defined static +10-meter perimeter polygon/bracket.
"""

import cv2
import numpy as np


class Zone:
    """A restricted +10m perimeter area, defined as a polygon of (x, y) points."""

    def __init__(self, zone_id: str = "+10M-PERIMETER", points: list[tuple[int, int]] = None):
        self.zone_id = zone_id
        # Default static +10-meter perimeter bracket (trapezoid across tactical ground plane)
        self.points = points or [(200, 360), (1080, 360), (1240, 680), (40, 680)]
        self._np_points = np.array(self.points, dtype=np.int32)

    def contains_point(self, x: float, y: float) -> bool:
        """Returns True if (x, y) is inside or on the edge of the polygon."""
        result = cv2.pointPolygonTest(self._np_points, (float(x), float(y)), False)
        return result >= 0

    def intersects_box(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """
        Returns True if any critical point of the person bounding box is inside
        the +10m perimeter zone, or if the box intersects the perimeter.
        """
        # Test key points: feet center, feet left, feet right, center, top center
        test_points = [
            ((x1 + x2) / 2, y2),        # Feet center (standing position)
            (x1, y2),                   # Feet bottom-left
            (x2, y2),                   # Feet bottom-right
            ((x1 + x2) / 2, (y1 + y2) / 2), # Torso center
            ((x1 + x2) / 2, y1),        # Head / upper boundary
        ]
        for px, py in test_points:
            if self.contains_point(px, py):
                return True
        return False


class IntrusionDetector:
    def __init__(self, zone: Zone):
        self.zone = zone
        self._tracks_inside: set[int] = set()

    def check(self, tracked_objects: list) -> list[int]:
        """
        Given a list of TrackedObject (from Tracker), returns the
        list of track_ids that are NEWLY inside the +10m perimeter zone.
        Filters strictly for person detections.
        """
        new_intrusions = []
        currently_inside = set()

        for obj in tracked_objects:
            # Threat detection filter: persons & tactical vehicles
            class_name = getattr(obj, "class_name", "person").lower()
            if class_name not in ["person", "car", "truck", "bus", "motorcycle"]:
                continue

            x1, y1, x2, y2 = obj.box

            if self.zone.intersects_box(x1, y1, x2, y2):
                currently_inside.add(obj.track_id)
                if obj.track_id not in self._tracks_inside:
                    new_intrusions.append(obj.track_id)

        self._tracks_inside = currently_inside
        return new_intrusions