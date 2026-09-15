"""
Line-crossing detection
------------------------
Checks whether a tracked object's position has crossed from one
side of a defined line to the other, between two checks.

Does NOT know about cameras, YOLO, or events - just: given a point
and a line, which side is it on, and did it change sides?
"""


class Line:
    """A boundary line, defined by two (x, y) endpoints."""

    def __init__(self, line_id: str, point_a: tuple[int, int], point_b: tuple[int, int]):
        self.line_id = line_id
        self.point_a = point_a
        self.point_b = point_b

    def side_of_line(self, x: float, y: float) -> int:
        """
        Returns which side of the line the point (x, y) is on:
          > 0  -> one side
          < 0  -> the other side
          = 0  -> exactly on the line

        This uses the "cross product" trick: a simple bit of geometry
        math that tells you which side of a line a point falls on,
        without needing angles or trigonometry.
        """
        ax, ay = self.point_a
        bx, by = self.point_b
        # Cross product of (B - A) and (Point - A).
        value = (bx - ax) * (y - ay) - (by - ay) * (x - ax)

        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0


class LineCrossingDetector:
    def __init__(self, line: Line):
        self.line = line
        # Remembers which side each track_id was on LAST time we checked.
        self._last_side: dict[int, int] = {}

    def check(self, tracked_objects: list) -> list[int]:
        """
        Given a list of TrackedObject, returns the list of track_ids
        that crossed the line since the last check (side flipped).
        """
        crossed = []

        for obj in tracked_objects:
            x1, y1, x2, y2 = obj.box
            center_x = (x1 + x2) / 2
            bottom_y = y2

            current_side = self.line.side_of_line(center_x, bottom_y)

            # Ignore points exactly on the line - treat as "no change yet".
            if current_side == 0:
                continue

            previous_side = self._last_side.get(obj.track_id)

            # If we've seen this track before, AND the side flipped
            # (and neither reading was "on the line"), that's a crossing.
            if previous_side is not None and previous_side != current_side:
                crossed.append(obj.track_id)

            self._last_side[obj.track_id] = current_side

        return crossed