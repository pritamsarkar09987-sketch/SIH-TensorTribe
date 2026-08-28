"""
Manual test script for CameraManager.
Run this directly to confirm CameraManager works as expected.
"""

from app.camera.camera_manager import CameraManager

manager = CameraManager()

# Add a camera
cam1 = manager.add_camera(
    camera_id="CAM-01",
    name="Border Camera 1",
    source="videos/test.mp4",
    type="file",
)
print("Added:", cam1)

# List all cameras
print("All cameras:", manager.get_all_cameras())

# Get one camera by ID
found = manager.get_camera("CAM-01")
print("Found CAM-01:", found)

# Update its status
manager.update_status("CAM-01", "running")
print("After status update:", manager.get_camera("CAM-01"))

# Try getting a camera that doesn't exist
missing = manager.get_camera("CAM-99")
print("CAM-99 (should be None):", missing)

# Remove the camera
manager.remove_camera("CAM-01")
print("All cameras after removal:", manager.get_all_cameras())