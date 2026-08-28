"""
Tracker
-------
Wraps YOLO's built-in tracking (ByteTrack under the hood).
Unlike plain detection, tracking requires calling the model in
"track mode" continuously on the SAME video stream, so it can
remember objects between frames and assign consistent Track IDs.

Does NOT know about cameras or threads - just: give it a frame
from an ongoing stream, get back tracked detections with IDs.
"""

from ultralytics import YOLO


class TrackedObject:
    """One tracked object in a frame, with a consistent ID across frames."""

    def __init__(self, track_id: int, class_name: str, confidence: float, box: tuple):
        self.track_id = track_id
        self.class_name = class_name
        self.confidence = confidence
        self.box = box  # (x1, y1, x2, y2)

    def __repr__(self):
        x1, y1, x2, y2 = self.box
        return f"Track#{self.track_id}({self.class_name}, conf={self.confidence:.2f}, box=[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}])"


class Tracker:
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.4):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def track(self, frame) -> list[TrackedObject]:
        """
        Run tracking on a single frame from an ONGOING stream.
        persist=True tells YOLO to remember previous frames' tracked
        objects, so IDs stay consistent as this is called repeatedly.
        """
        results = self.model.track(frame, persist=True, verbose=False)
        result = results[0]

        tracked_objects = []

        # If nothing is tracked yet (e.g. very first frame), boxes.id can be None.
        if result.boxes.id is None:
            return tracked_objects

        for box in result.boxes:
            confidence = float(box.conf[0])
            if confidence < self.confidence_threshold:
                continue

            track_id = int(box.id[0])
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            tracked_objects.append(TrackedObject(track_id, class_name, confidence, (x1, y1, x2, y2)))

        return tracked_objects