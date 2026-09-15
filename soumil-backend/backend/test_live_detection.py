"""
Runs YOLO detection continuously on live frames from CameraWorker,
twice per second, for 10 seconds - simulating how detection will
work against a real camera feed.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.detector import Detector

manager = CameraManager()
manager.add_camera(
    camera_id="CAM-01",
    name="Border Camera 1",
    source="videos/test.mp4",
    type="file",
)

worker = CameraWorker(camera_id="CAM-01", source="videos/test.mp4", camera_manager=manager, source_type="file")
worker.start()

print("Loading YOLO model...")
detector = Detector()
print("Model loaded. Starting live detection...\n")

DETECTION_INTERVAL_SECONDS = 0.5  # run detection twice per second
end_time = time.time() + 10  # run for 10 seconds total

while time.time() < end_time:
    frame = worker.get_latest_frame()

    if frame is not None:
        detections = detector.detect(frame)
        if detections:
            print(f"[{time.strftime('%H:%M:%S')}] Detected {len(detections)} object(s):")
            for d in detections:
                print("   ", d)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] No objects detected.")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] No frame available yet.")

    time.sleep(DETECTION_INTERVAL_SECONDS)

worker.stop()
print("\nDone.")