"""
Tests line-crossing detection using live tracking on the test video.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.tracker import Tracker
from app.analytics.line_crossing import Line, LineCrossingDetector

manager = CameraManager()
manager.add_camera(
    camera_id="CAM-01",
    name="Border Camera 1",
    source="videos/test.mp4",
    type="file",
)

worker = CameraWorker(camera_id="CAM-01", source="videos/test.mp4", camera_manager=manager, source_type="file")
worker.start()

print("Loading YOLO tracking model...")
tracker = Tracker()

# A vertical line roughly through the middle of the frame (1280x720 video).
# Adjust these points later once we know exactly where your test
# person actually walks.
line = Line("LINE-1", point_a=(640, 0), point_b=(640, 720))
line_detector = LineCrossingDetector(line)

print("Model loaded. Monitoring line for crossings...\n")

DETECTION_INTERVAL_SECONDS = 0.2  # check more frequently, to catch fast crossings
end_time = time.time() + 10

while time.time() < end_time:
    frame = worker.get_latest_frame()

    if frame is not None:
        tracked = tracker.track(frame)
        crossed = line_detector.check(tracked)

        for track_id in crossed:
            print(f"[{time.strftime('%H:%M:%S')}] 🚨 LINE CROSSED - Track#{track_id} crossed {line.line_id}")

        if tracked:
            print(f"[{time.strftime('%H:%M:%S')}] Currently tracking: {[t.track_id for t in tracked]}")

    time.sleep(DETECTION_INTERVAL_SECONDS)

worker.stop()
print("\nDone.")