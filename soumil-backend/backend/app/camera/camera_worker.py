"""
CameraWorker
------------
Owns ONE camera's video source. Runs in its own background thread,
continuously reading frames and keeping the latest one available.

Handles:
  - "file" sources (e.g. videos/test.mp4) — loops infinitely.
  - "rtsp" sources (e.g. rtsp://...) — TCP interleaved transport, handles network reconnects.
  - "http" MJPEG sources (e.g. http://192.168.x.x:8080/video).
  - local webcam indices (e.g. "0", "1").

Does NOT block main thread. Reconnects automatically in background.
"""

import os
import threading
import time
import cv2

from app.camera.camera_manager import CameraManager

# Configure OpenCV FFMPEG RTSP options:
# Force TCP transport (prevents UDP packet loss and Windows firewall drops)
# stimeout in microseconds: 4000000 = 4 seconds
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;4000000|buffer_size;1024000"

RECONNECT_DELAY_SECONDS = 2.0
MAX_RECONNECT_ATTEMPTS = 100


class CameraWorker:
    def __init__(self, camera_id: str, source: str, camera_manager: CameraManager, source_type: str = "file"):
        self.camera_id = camera_id
        self.source = source
        self.camera_manager = camera_manager
        self.source_type = source_type  # "file" or "rtsp"

        self.status = "initializing"
        self.reconnect_count = 0
        self.last_error = ""

        self._capture = None
        self._thread = None
        self._running = False

        self._lock = threading.Lock()
        self._latest_frame = None

    def start(self) -> None:
        """Start reading frames in the background thread (non-blocking)."""
        self._running = True
        self.status = "connecting"
        self.camera_manager.update_status(self.camera_id, "connecting")
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        print(f"[CameraWorker:{self.camera_id}] Background worker thread started for: {self.source}")

    def _open_capture(self) -> bool:
        """Attempts to open the video source with optimal backend and timeouts."""
        try:
            src = self.source.strip()
            if src.isdigit():
                # Built-in or USB webcam index (DirectShow on Windows for instant initialization)
                cam_backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
                self._capture = cv2.VideoCapture(int(src), cam_backend)
            elif src.startswith("rtsp://") or src.startswith("rtsps://"):
                # Force FFMPEG backend with TCP transport and explicit OpenCV 5.0 timeout properties
                params = [
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 4000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC, 4000,
                    cv2.CAP_PROP_BUFFERSIZE, 1,
                ]
                self._capture = cv2.VideoCapture(src, cv2.CAP_FFMPEG, params)
            elif src.startswith("http://") or src.startswith("https://"):
                # HTTP MJPEG / IP Webcam streams
                params = [
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 4000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC, 4000,
                    cv2.CAP_PROP_BUFFERSIZE, 1,
                ]
                self._capture = cv2.VideoCapture(src, cv2.CAP_FFMPEG, params)
            else:
                self._capture = cv2.VideoCapture(src)

            if self._capture is not None and self._capture.isOpened():
                self.status = "connected"
                return True
        except Exception as e:
            self.last_error = str(e)
            print(f"[CameraWorker:{self.camera_id}] Open capture error: {e}")
        return False

    def _read_loop(self) -> None:
        """Runs continuously in background thread. Handles reconnection and stream decoding."""
        reconnect_attempts = 0
        consecutive_read_failures = 0

        while self._running:
            if self._capture is None or not self._capture.isOpened():
                self.status = "connecting"
                self.camera_manager.update_status(self.camera_id, "connecting")
                opened = self._open_capture()
                if not opened:
                    reconnect_attempts += 1
                    self.reconnect_count = reconnect_attempts
                    self.status = f"reconnecting (attempt {reconnect_attempts})"
                    self.camera_manager.update_status(self.camera_id, "reconnecting")
                    time.sleep(RECONNECT_DELAY_SECONDS)
                    continue

            try:
                ret, frame = self._capture.read()

                if not ret or frame is None:
                    if self.source_type == "file":
                        # Video file reached end - rewind to frame 0 for continuous live feed
                        self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret_rewind, frame_rewind = self._capture.read()
                        if ret_rewind and frame_rewind is not None:
                            reconnect_attempts = 0
                            self.reconnect_count = 0
                            self.status = "running"
                            with self._lock:
                                self._latest_frame = frame_rewind
                            time.sleep(1 / 35)
                            continue
                        else:
                            time.sleep(0.05)
                            continue

                    # For RTSP / live streams: tolerate brief keyframe gaps (up to ~1.5 seconds)
                    consecutive_read_failures += 1
                    if consecutive_read_failures < 25:
                        time.sleep(0.04)
                        continue

                    # Stream has genuinely stalled or disconnected
                    consecutive_read_failures = 0
                    reconnect_attempts += 1
                    self.reconnect_count = reconnect_attempts
                    self.status = f"reconnecting (attempt {reconnect_attempts})"
                    self.camera_manager.update_status(self.camera_id, "reconnecting")
                    if self._capture is not None:
                        try:
                            self._capture.release()
                        except Exception:
                            pass
                        self._capture = None
                    time.sleep(RECONNECT_DELAY_SECONDS)
                    continue

                # Successful frame read
                consecutive_read_failures = 0
                reconnect_attempts = 0
                self.reconnect_count = 0
                self.status = "running"
                self.camera_manager.update_status(self.camera_id, "running")

                with self._lock:
                    self._latest_frame = frame

                time.sleep(1 / 35)

            except Exception as e:
                print(f"[CameraWorker:{self.camera_id}] Read loop error: {e}")
                self.last_error = str(e)
                consecutive_read_failures = 0
                if self._capture is not None:
                    try:
                        self._capture.release()
                    except Exception:
                        pass
                    self._capture = None
                time.sleep(RECONNECT_DELAY_SECONDS)

    def get_latest_frame(self):
        """Thread-safe access to the most recent frame (or None if connecting)."""
        with self._lock:
            return self._latest_frame

    def stop(self) -> None:
        """Signal the loop to stop and release the video source."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.5)
        if self._capture is not None:
            try:
                self._capture.release()
            except Exception:
                pass
            self._capture = None
        self.camera_manager.update_status(self.camera_id, "stopped")