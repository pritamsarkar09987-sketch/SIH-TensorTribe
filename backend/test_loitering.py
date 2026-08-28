"""
Tests loitering detection using live tracking on the test video.
Uses a SHORT threshold (2 seconds) just to prove the logic works
within our short test video - not a realistic production value.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.tracker import Tracker
from app.analytics.loitering import LoiteringDetector

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

loitering_detector = LoiteringDetector(time_threshold_seconds=2.0, movement_tolerance_pixels=50.0)

print("Model loaded. Monitoring for loitering...\n")

DETECTION_INTERVAL_SECONDS = 0.2
end_time = time.time() + 10

while time.time() < end_time:
    frame = worker.get_latest_frame()

    if frame is not None:
        tracked = tracker.track(frame)
        loitering_ids = loitering_detector.check(tracked)

        for track_id in loitering_ids:
            print(f"[{time.strftime('%H:%M:%S')}] 🚨 LOITERING DETECTED - Track#{track_id}")

        if tracked:
            print(f"[{time.strftime('%H:%M:%S')}] Currently tracking: {[t.track_id for t in tracked]}")

    time.sleep(DETECTION_INTERVAL_SECONDS)

worker.stop()
print("\nDone.")