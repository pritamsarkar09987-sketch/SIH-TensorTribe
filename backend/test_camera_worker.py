"""
Manual test for CameraWorker.
Requires a real (non-empty) videos/test.mp4 file to work.
"""

import time
from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker

manager = CameraManager()
manager.add_camera(
    camera_id="CAM-01",
    name="Border Camera 1",
    source="videos/test.mp4",
    type="file",
)

worker = CameraWorker(camera_id="CAM-01", source="videos/test.mp4", camera_manager=manager, source_type="file")
worker.start()

print("Status right after start:", manager.get_camera("CAM-01").status)

# Give it a moment to read a few frames
time.sleep(1)

frame = worker.get_latest_frame()
if frame is not None:
    print("Got a frame! Shape:", frame.shape)
else:
    print("No frame yet.")

# Let it run until the video ends (or stop it manually after a few seconds)
time.sleep(3)
worker.stop()

print("Status after stop:", manager.get_camera("CAM-01").status)