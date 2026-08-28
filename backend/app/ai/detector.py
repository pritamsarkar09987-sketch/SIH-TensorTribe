"""
Detector
--------
Wraps a YOLO model. Loads it ONCE (loading is slow), and exposes a
simple method to run detection on a single frame and get back a
clean list of detections.

Does NOT know about cameras, threads, or video - just: give it a
frame, get back detections.
"""

from ultralytics import YOLO


class Detection:
    """One detected object in a frame."""

    def __init__(self, class_name: str, confidence: float, box: tuple):
        self.class_name = class_name
        self.confidence = confidence
        self.box = box  # (x1, y1, x2, y2)

    def __repr__(self):
        x1, y1, x2, y2 = self.box
        return f"Detection({self.class_name}, conf={self.confidence:.2f}, box=[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}])"


class Detector:
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.4):
        # Loading the model is slow, so this should happen ONCE,
        # not every time we want to detect something.
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, frame) -> list[Detection]:
        """Run detection on a single frame. Returns a list of Detection objects."""
        results = self.model(frame, verbose=False)
        result = results[0]

        detections = []
        for box in result.boxes:
            confidence = float(box.conf[0])

            # Skip low-confidence detections - reduces false alarms.
            if confidence < self.confidence_threshold:
                continue

            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append(Detection(class_name, confidence, (x1, y1, x2, y2)))

        return detections