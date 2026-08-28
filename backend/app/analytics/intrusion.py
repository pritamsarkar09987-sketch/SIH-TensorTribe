"""
Intrusion detection
--------------------
Checks whether a tracked object's position is inside a restricted
zone (a polygon). If a track enters the zone, that's an intrusion.

Does NOT know about cameras, YOLO, or events - just: given a point
and a zone, is it inside?
"""

import cv2
import numpy as np


class Zone:
    """A restricted area, defined as a polygon of (x, y) points."""

    def __init__(self, zone_id: str, points: list[tuple[int, int]]):
        self.zone_id = zone_id
        self.points = points
        # OpenCV wants points as a specific NumPy array shape for
        # its point-in-polygon check.
        self._np_points = np.array(points, dtype=np.int32)

    def contains_point(self, x: float, y: float) -> bool:
        """Returns True if the point (x, y) is inside this zone."""
        # cv2.pointPolygonTest returns >0 if inside, 0 if on the edge,
        # <0 if outside. measureDist=False just gives us a yes/no signal.
        result = cv2.pointPolygonTest(self._np_points, (float(x), float(y)), False)
        return result >= 0


class IntrusionDetector:
    def __init__(self, zone: Zone):
        self.zone = zone
        # Remembers which track IDs were already inside the zone last
        # check, so we only report a NEW intrusion once - not every frame.
        self._tracks_inside: set[int] = set()

    def check(self, tracked_objects: list) -> list[int]:
        """
        Given a list of TrackedObject (from Tracker), returns the
        list of track_ids that are NEWLY inside the zone this check
        (i.e. weren't inside last time).
        """
        new_intrusions = []
        currently_inside = set()

        for obj in tracked_objects:
            x1, y1, x2, y2 = obj.box
            # Use the bottom-center of the box as the object's "position" -
            # a common convention, since that's roughly where a person's
            # feet are, i.e. where they're actually standing.
            center_x = (x1 + x2) / 2
            bottom_y = y2

            if self.zone.contains_point(center_x, bottom_y):
                currently_inside.add(obj.track_id)
                if obj.track_id not in self._tracks_inside:
                    new_intrusions.append(obj.track_id)

        self._tracks_inside = currently_inside
        return new_intrusions