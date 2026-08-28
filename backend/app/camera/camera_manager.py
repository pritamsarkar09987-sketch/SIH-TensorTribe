"""
CameraManager
-------------
Keeps track of every camera the system knows about.
It does NOT open video files, read frames, or run AI.
It is just a registry: add, list, get, update-status, remove.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Camera:
    """Represents a single camera's information (not its video feed)."""
    camera_id: str
    name: str
    source: str          # e.g. "videos/test.mp4" or "rtsp://..."
    type: str             # e.g. "file" or "rtsp"
    status: str = "stopped"  # "stopped", "running", "error", etc.


class CameraManager:
    """A simple in-memory registry of Camera objects."""

    def __init__(self) -> None:
        # Internally we store cameras in a dictionary so lookups by
        # camera_id are fast (no looping through a list every time).
        self._cameras: Dict[str, Camera] = {}

    def add_camera(self, camera_id: str, name: str, source: str, type: str) -> Camera:
        """Register a new camera. Raises an error if the ID already exists."""
        if camera_id in self._cameras:
            raise ValueError(f"Camera '{camera_id}' already exists.")

        camera = Camera(camera_id=camera_id, name=name, source=source, type=type)
        self._cameras[camera_id] = camera
        return camera

    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """Look up one camera by its ID. Returns None if it doesn't exist."""
        return self._cameras.get(camera_id)

    def get_all_cameras(self) -> List[Camera]:
        """Return every camera currently registered."""
        return list(self._cameras.values())

    def update_status(self, camera_id: str, status: str) -> Camera:
        """Change a camera's status (e.g. 'stopped' -> 'running')."""
        camera = self.get_camera(camera_id)
        if camera is None:
            raise ValueError(f"Camera '{camera_id}' not found.")
        camera.status = status
        return camera

    def remove_camera(self, camera_id: str) -> None:
        """Delete a camera from the registry."""
        if camera_id not in self._cameras:
            raise ValueError(f"Camera '{camera_id}' not found.")
        del self._cameras[camera_id]