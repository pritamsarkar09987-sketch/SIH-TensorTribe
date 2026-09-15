"""
Debug tool: starts a CameraWorker and displays its live frames
in a window, so we can visually confirm frame capture works.

Not part of the final app — press 'q' to quit.
"""

import cv2

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

print("Showing live feed. Press 'q' in the video window to quit.")

while True:
    frame = worker.get_latest_frame()

    if frame is not None:
        cv2.imshow("CAM-01 Feed", frame)

    # waitKey(1) checks for a keypress for 1ms and lets the OpenCV
    # window actually redraw itself. Without this, no window shows up.
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

    camera = manager.get_camera("CAM-01")
    if camera.status == "stopped":
        print("Video ended.")
        break

worker.stop()
cv2.destroyAllWindows()
print("Done.")