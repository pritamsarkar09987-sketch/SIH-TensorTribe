"""
Runs YOLO tracking continuously on live frames from CameraWorker,
so we can see Track IDs stay consistent as the same object moves
across frames.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.tracker import Tracker

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
print("Model loaded. Starting live tracking...\n")

DETECTION_INTERVAL_SECONDS = 0.3
end_time = time.time() + 10

while time.time() < end_time:
    frame = worker.get_latest_frame()

    if frame is not None:
        tracked = tracker.track(frame)
        if tracked:
            print(f"[{time.strftime('%H:%M:%S')}] Tracking {len(tracked)} object(s):")
            for t in tracked:
                print("   ", t)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Nothing tracked.")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] No frame available yet.")

    time.sleep(DETECTION_INTERVAL_SECONDS)

worker.stop()
print("\nDone.")