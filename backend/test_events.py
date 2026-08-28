"""
Full pipeline test: tracks objects, checks for intrusion, and
creates structured Events instead of just printing.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.tracker import Tracker
from app.analytics.intrusion import Zone, IntrusionDetector
from app.events.event_manager import EventManager

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

zone = Zone("ZONE-1", points=[(500, 400), (1280, 400), (1280, 720), (500, 720)])
intrusion_detector = IntrusionDetector(zone)
event_manager = EventManager()

print("Model loaded. Monitoring for events...\n")

DETECTION_INTERVAL_SECONDS = 0.3
end_time = time.time() + 10

while time.time() < end_time:
    frame = worker.get_latest_frame()

    if frame is not None:
        tracked = tracker.track(frame)
        new_intrusions = intrusion_detector.check(tracked)

        for track_id in new_intrusions:
            event = event_manager.create_event(
                event_type="intrusion",
                camera_id="CAM-01",
                track_id=track_id,
                severity="high",
                details={"zone_id": zone.zone_id},
            )
            print(f"[{time.strftime('%H:%M:%S')}] Created event:", event)

    time.sleep(DETECTION_INTERVAL_SECONDS)

worker.stop()

print(f"\nTotal events recorded: {len(event_manager.get_all_events())}")
for event in event_manager.get_all_events():
    print(event.to_dict())

print("\nDone.")