"""
DetectionPipeline
------------------
Runs continuously in the background alongside a live CameraWorker.
Pulls the latest frame, runs tracking + analytics, and creates
Events automatically - this is what makes detection actually happen
in the real running system, not just in test scripts.

One DetectionPipeline per camera - each camera needs its own Tracker
so Track IDs never collide between cameras.
"""

import threading
import time

from app.ai.tracker import Tracker
from app.analytics.intrusion import Zone, IntrusionDetector
from app.events.event_manager import EventManager


class DetectionPipeline:
    def __init__(self, camera_id: str, camera_worker, event_manager: EventManager, zone: Zone):
        self.camera_id = camera_id
        self.camera_worker = camera_worker
        self.event_manager = event_manager

        # Own Tracker + IntrusionDetector per camera - tracking state
        # (Track IDs) must never be shared between cameras.
        self.tracker = Tracker()
        self.intrusion_detector = IntrusionDetector(zone)
        self.zone = zone

        self._running = False
        self._thread = None

        # Detection is slow (~120ms) - check a few times per second,
        # not on every captured frame.
        self.check_interval_seconds = 0.3

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        while self._running:
            frame = self.camera_worker.get_latest_frame()

            if frame is not None:
                tracked_objects = self.tracker.track(frame)
                new_intrusions = self.intrusion_detector.check(tracked_objects)

                for track_id in new_intrusions:
                    self.event_manager.create_event(
                        event_type="intrusion",
                        camera_id=self.camera_id,
                        track_id=track_id,
                        severity="high",
                        details={"zone_id": self.zone.zone_id},
                    )

            time.sleep(self.check_interval_seconds)

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)