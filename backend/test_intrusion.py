"""
Tests zone intrusion detection using live tracking on the test video.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.tracker import Tracker
from app.analytics.intrusion import Zone, IntrusionDetector

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

# A rectangular test zone. Your video is 1280x720 (from earlier test),
# so this covers roughly the bottom-right quarter of the frame -
# adjust these numbers once we confirm this works, to match where
# your test person actually walks.
zone = Zone("ZONE-1", points=[(500, 400), (1280, 400), (1280, 720), (500, 720)])
intrusion_detector = IntrusionDetector(zone)

print("Model loaded. Monitoring zone for intrusions...\n")

DETECTION_INTERVAL_SECONDS = 0.3
end_time = time.time() + 10

while time.time() < end_time:
    frame = worker.get_latest_frame()

    if frame is not None:
        tracked = tracker.track(frame)
        new_intrusions = intrusion_detector.check(tracked)

        for track_id in new_intrusions:
            print(f"[{time.strftime('%H:%M:%S')}] 🚨 INTRUSION DETECTED - Track#{track_id} entered {zone.zone_id}")

        if tracked:
            print(f"[{time.strftime('%H:%M:%S')}] Currently tracking: {[t.track_id for t in tracked]}")

    time.sleep(DETECTION_INTERVAL_SECONDS)

worker.stop()
print("\nDone.")