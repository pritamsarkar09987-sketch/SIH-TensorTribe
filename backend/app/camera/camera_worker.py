"""
CameraWorker
------------
Owns ONE camera's video source. Runs in its own background thread,
continuously reading frames and keeping the latest one available.

Handles both:
  - "file" sources (e.g. videos/test.mp4) — reaching the end is NORMAL.
  - "rtsp" sources (e.g. rtsp://...) — a failed read means the connection
    was lost, and the worker should automatically try to reconnect.

Does NOT do AI, tracking, or anything beyond frame capture.
"""

import threading
import time
import cv2

from app.camera.camera_manager import CameraManager

# How long to wait before retrying a dropped RTSP connection.
RECONNECT_DELAY_SECONDS = 3

# How many reconnect attempts before giving up and marking the camera "error".
MAX_RECONNECT_ATTEMPTS = 5


class CameraWorker:
    def __init__(self, camera_id: str, source: str, camera_manager: CameraManager, source_type: str = "file"):
        self.camera_id = camera_id
        self.source = source
        self.camera_manager = camera_manager
        self.source_type = source_type  # "file" or "rtsp"

        self._capture = None
        self._thread = None
        self._running = False

        self._lock = threading.Lock()
        self._latest_frame = None

    def start(self) -> None:
        """Open the video source and start reading frames in the background."""
        if not self._open_capture():
            self.camera_manager.update_status(self.camera_id, "error")
            raise RuntimeError(f"Could not open source: {self.source}")

        self._running = True
        self.camera_manager.update_status(self.camera_id, "running")

        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _open_capture(self) -> bool:
        """Attempts to open the video source. Returns True/False for success."""
        self._capture = cv2.VideoCapture(self.source)
        return self._capture.isOpened()

    def _read_loop(self) -> None:
        """Runs in the background thread. Reads frames until stopped or given up on."""
        reconnect_attempts = 0

        while self._running:
            try:
                ret, frame = self._capture.read()

                if not ret:
                    if self.source_type == "file":
                        # A file reaching its end is NORMAL, not a failure.
                        self.camera_manager.update_status(self.camera_id, "stopped")
                        self._running = False
                        break

                    # source_type == "rtsp": treat this as a dropped connection.
                    reconnect_attempts += 1
                    if reconnect_attempts > MAX_RECONNECT_ATTEMPTS:
                        self.camera_manager.update_status(self.camera_id, "error")
                        self._running = False
                        break

                    self.camera_manager.update_status(self.camera_id, "reconnecting")
                    self._capture.release()
                    time.sleep(RECONNECT_DELAY_SECONDS)

                    if self._open_capture():
                        self.camera_manager.update_status(self.camera_id, "running")
                        reconnect_attempts = 0  # reset counter after a successful reconnect
                    continue

                # Successful read — reset the reconnect counter.
                reconnect_attempts = 0
                with self._lock:
                    self._latest_frame = frame

                time.sleep(1 / 30)

            except Exception as e:
                # Catch anything unexpected so this thread can't die silently.
                print(f"[CameraWorker:{self.camera_id}] Unexpected error: {e}")
                self.camera_manager.update_status(self.camera_id, "error")
                self._running = False
                break

    def get_latest_frame(self):
        """Thread-safe access to the most recent frame (or None if not ready yet)."""
        with self._lock:
            return self._latest_frame

    def stop(self) -> None:
        """Signal the loop to stop and release the video source."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
        if self._capture is not None:
            self._capture.release()
        self.camera_manager.update_status(self.camera_id, "stopped")