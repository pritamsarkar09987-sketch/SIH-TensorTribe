"""
DetectionPipeline
------------------
Runs continuously in the background alongside a live CameraWorker.
Pulls the latest frame, runs tracking + analytics, and creates
Events automatically. Renders tactical HUD overlay, streams raw JPEG
frames to the Go Broadcaster (/ingest), and syncs alerts to Node.js / PostgreSQL.
"""

import threading
import time
import base64
import requests
import cv2
import numpy as np

from app.ai.tracker import Tracker
from app.analytics.intrusion import Zone, IntrusionDetector
from app.events.event_manager import EventManager


class DetectionPipeline:
    def __init__(self, camera_id: str, camera_worker, event_manager: EventManager, zone: Zone,
                 broadcaster_url: str = "http://localhost:8080/ingest",
                 api_alert_url: str = "http://localhost:5000/api/alert"):
        self.camera_id = camera_id
        self.camera_worker = camera_worker
        self.event_manager = event_manager
        self.broadcaster_url = broadcaster_url
        self.api_alert_url = api_alert_url

        self.tracker = Tracker()
        self.intrusion_detector = IntrusionDetector(zone)
        self.zone = zone

        self._running = False
        self._thread = None
        self._last_alert_time = 0

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _draw_hud(self, frame, tracked_objects, has_intrusion: bool):
        # Draw restricted zone polygon
        overlay = frame.copy()
        zone_color = (0, 0, 255) if has_intrusion else (0, 215, 255)  # Red if breach, amber if standby
        cv2.polylines(overlay, [self.zone._np_points], isClosed=True, color=zone_color, thickness=2)
        cv2.fillPoly(overlay, [self.zone._np_points], color=zone_color)
        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

        # Zone label
        cv2.putText(frame, f"[RESTRICTED: {self.zone.zone_id}]", 
                    (self.zone.points[0][0] + 10, self.zone.points[0][1] + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, zone_color, 2)

        # Draw tracked objects
        for obj in tracked_objects:
            x1, y1, x2, y2 = [int(v) for v in obj.box]
            center_x = (x1 + x2) / 2
            bottom_y = y2
            is_inside = self.zone.contains_point(center_x, bottom_y)
            box_color = (0, 0, 255) if is_inside else (0, 255, 0)

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            
            # Label badge
            label = f"ID:{obj.track_id} {obj.class_name} {obj.confidence:.2f}"
            if is_inside:
                label += " [INTRUSION]"
            
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 22), (x1 + w + 6, y1), box_color, -1)
            cv2.putText(frame, label, (x1 + 3, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # HUD Top Banner
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 36), (15, 15, 15), -1)
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"IBVAP TACTICAL FEED | CAM: {self.camera_id} | {timestamp_str}", (15, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 180), 2)
        
        status_text = "STATUS: BREACH DETECTED" if has_intrusion else "STATUS: PERIMETER SECURE"
        status_color = (0, 0, 255) if has_intrusion else (0, 255, 0)
        cv2.putText(frame, status_text, (frame.shape[1] - 320, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2)

        return frame

    def _run_loop(self) -> None:
        session = requests.Session()
        while self._running:
            raw_frame = self.camera_worker.get_latest_frame()

            if raw_frame is not None:
                frame_copy = raw_frame.copy()
                tracked_objects = self.tracker.track(frame_copy)
                new_intrusions = self.intrusion_detector.check(tracked_objects)
                has_intrusion = len(self.intrusion_detector._tracks_inside) > 0

                for track_id in new_intrusions:
                    self.event_manager.create_event(
                        event_type="intrusion",
                        camera_id=self.camera_id,
                        track_id=track_id,
                        severity="high",
                        details={"zone_id": self.zone.zone_id},
                    )

                    # Post alert to Node.js backend database
                    now = time.time()
                    if now - self._last_alert_time > 3.0:  # debounce 3s
                        self._last_alert_time = now
                        threading.Thread(target=self._post_db_alert, args=(track_id, frame_copy), daemon=True).start()

                # Render military tactical HUD overlay
                annotated = self._draw_hud(frame_copy, tracked_objects, has_intrusion)

                # Compress to JPEG and push to Go Broadcaster /ingest endpoint
                ret, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if ret:
                    try:
                        session.post(self.broadcaster_url, data=buffer.tobytes(), timeout=0.15)
                    except Exception:
                        pass  # Non-blocking if Go broadcaster temporarily drops

            time.sleep(1 / 30)

    def _post_db_alert(self, track_id: int, frame) -> None:
        try:
            thumb = cv2.resize(frame, (320, 180))
            _, buf = cv2.imencode('.jpg', thumb, [cv2.IMWRITE_JPEG_QUALITY, 50])
            b64_snapshot = "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode('utf-8')

            requests.post(
                self.api_alert_url,
                json={
                    "camera_id": self.camera_id,
                    "object_type": "human",
                    "tracking_id": track_id,
                    "confidence": 0.88,
                    "spatial_coordinates": {"zone_id": self.zone.zone_id},
                    "snapshot_data": b64_snapshot
                },
                timeout=1.5
            )
        except Exception as e:
            print(f"[Alert DB sync error]: {e}")

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)