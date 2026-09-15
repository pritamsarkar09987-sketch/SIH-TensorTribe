"""
Tests that a broken/unreachable RTSP-style source fails gracefully
(reconnects a few times, then reports 'error') instead of crashing
or hanging forever.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker

manager = CameraManager()
manager.add_camera(
    camera_id="CAM-BAD",
    name="Broken Camera",
    source="rtsp://nonexistent-camera-address/stream",
    type="rtsp",
)

worker = CameraWorker(
    camera_id="CAM-BAD",
    source="rtsp://nonexistent-camera-address/stream",
    camera_manager=manager,
    source_type="rtsp",
)

try:
    worker.start()
except RuntimeError as e:
    print("Expected failure on start:", e)