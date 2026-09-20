"""
Netra AI - Live Edge-to-Cloud Video Streamer
============================================
Connects your local camera (Phone IP Webcam, Phone RTSP, PC Webcam, or Video File)
directly to your deployed Render Cloud Website!

Why is this needed?
-------------------
Your phone camera (e.g. 192.168.0.133:8080) is on your private home Wi-Fi.
Cloud servers (like Render in the USA/Europe) cannot directly reach private 192.168.x.x Wi-Fi IPs across the internet.
This script runs locally on your PC/laptop (which is on the same Wi-Fi as your phone),
processes YOLOv8 AI tracking and perimeter intrusion detection at high speed,
and streams the analyzed video and intrusion alerts directly to your deployed cloud website!
"""

import os
import sys
import time
import argparse
from pathlib import Path
import requests

# Ensure soumil-backend/backend is in Python path
workspace_root = Path(__file__).resolve().parent
backend_dir = workspace_root / "soumil-backend" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configure OpenCV FFMPEG RTSP options globally before importing cv2
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;3000000|fflags;nobuffer|flags;low_delay|max_delay;500000|framedrop;1"

try:
    from app.camera.camera_manager import CameraManager
    from app.camera.camera_worker import CameraWorker
    from app.ai.pipeline import DetectionPipeline
    from app.analytics.intrusion import Zone
    from app.events.event_manager import EventManager
except ImportError as e:
    print(f"[Error] Failed to import Netra AI modules: {e}")
    sys.exit(1)


def get_default_render_url() -> str:
    # Check .env in workspace root or ranajit-apis
    candidates = [
        workspace_root / ".env",
        workspace_root / "ranajit-apis" / ".env",
        backend_dir / ".env",
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("RENDER_URL=") or line.startswith("WEBSITE_URL="):
                            return line.split("=", 1)[1].strip().strip("\"'")
            except Exception:
                pass
    return ""


def check_cloud_health(base_url: str):
    """Verifies that the deployed Render website is responsive."""
    health_url = f"{base_url}/api/health"
    print(f"\n[Pre-flight Check] Verifying cloud connection to {health_url}...")
    try:
        res = requests.get(health_url, timeout=12)
        if res.status_code == 200:
            data = res.json()
            active = data.get("activeViewers", 0)
            print(f"  [SUCCESS] Cloud server is ONLINE! Active dashboard viewers: {active}")
            return True
        else:
            print(f"  [WARNING] Cloud server returned HTTP {res.status_code}. Proceeding anyway...")
            return False
    except requests.exceptions.Timeout:
        print("  [NOTE] Cloud server timed out. If on Render free tier, the service may be spinning up from sleep.")
        print("  Proceeding with stream ingestion. Frames will be received once the server finishes waking up.")
        return False
    except Exception as e:
        print(f"  [NOTE] Connection notice: {e}")
        print("  Proceeding with stream ingestion...")
        return False


def main():
    parser = argparse.ArgumentParser(description="Netra AI - Edge-to-Cloud Video Streamer")
    parser.add_argument("--url", help="Deployed Render Website URL (e.g. https://sih-tensortribe.onrender.com)")
    parser.add_argument("--source", help="Camera source (e.g. http://192.168.0.133:8080/video or 0)")
    args = parser.parse_args()

    print("\n" + "=" * 64)
    print("  NETRA AI - EDGE-TO-CLOUD LIVE VIDEO STREAMER")
    print("=" * 64)

    # 1. Get Cloud Website URL
    user_url = args.url
    if not user_url:
        default_url = get_default_render_url() or "http://localhost:5000"
        prompt_msg = f"\nEnter your deployed Render Website URL [default: {default_url}]:\n> "
        user_url = input(prompt_msg).strip() or default_url

    if not user_url.startswith("http://") and not user_url.startswith("https://"):
        user_url = f"https://{user_url}"
    user_url = user_url.rstrip("/")

    broadcaster_url = f"{user_url}/ingest"
    api_alert_url = f"{user_url}/api/alert"

    print(f"\n[Target Cloud Website]  {user_url}")
    print(f"[Frame Ingest Target]   {broadcaster_url}")
    print(f"[Alert Ingest Target]   {api_alert_url}")

    # Check Cloud connectivity
    check_cloud_health(user_url)

    # 2. Select Video Stream Source
    source = args.source
    source_type = "rtsp"
    cam_name = "Tactical Surveillance Feed"

    if not source:
        print("\nSelect Camera / Stream Source:")
        print("  [1] Phone IP Webcam (e.g. http://192.168.0.133:8080/video)")
        print("  [2] Phone RTSP Stream (e.g. rtsp://192.168.0.133:8554/)")
        print("  [3] PC Local Webcam (camera index 0)")
        print("  [4] Sample Test Video (MP4 file)")
        print("  [5] Custom RTSP / HTTP URL")

        choice = input("\nEnter choice [1-5, default: 1]: ").strip() or "1"

        if choice == "1":
            default_ip = "http://192.168.0.133:8080/video"
            inp = input(f"Enter Phone IP Webcam URL [default: {default_ip}]: ").strip() or default_ip
            if not inp.startswith("http://") and not inp.startswith("https://"):
                inp = f"http://{inp}"
            if not inp.endswith("/video") and ":8080" in inp:
                inp = f"{inp.rstrip('/')}/video"
            source = inp
            cam_name = "Mobile Phone IP Webcam"
            source_type = "rtsp"

        elif choice == "2":
            default_rtsp = "rtsp://192.168.0.133:8554/"
            inp = input(f"Enter Phone RTSP URL [default: {default_rtsp}]: ").strip() or default_rtsp
            if not inp.startswith("rtsp://"):
                inp = f"rtsp://{inp}"
            source = inp
            cam_name = "Mobile Tactical Scout RTSP"
            source_type = "rtsp"

        elif choice == "3":
            source = "0"
            cam_name = "Command Terminal PC Webcam"
            source_type = "rtsp"

        elif choice == "4":
            test_videos = list(workspace_root.glob("uploads/*.mp4")) + list(backend_dir.glob("videos/*.mp4"))
            if test_videos:
                source = str(test_videos[0].resolve())
                cam_name = f"Recorded Patrol ({test_videos[0].name})"
            else:
                source = str((workspace_root / "uploads" / "patrol.mp4").resolve())
                cam_name = "Local Recorded Patrol"
            source_type = "file"
            print(f"Using video file: {source}")

        else:
            source = input("Enter custom stream link: ").strip()
            cam_name = "Custom Tactical Stream"
            source_type = "rtsp"
    else:
        # Source provided via CLI
        if source == "0" or source.isdigit():
            cam_name = "PC Local Webcam"
            source_type = "rtsp"
        elif source.endswith(".mp4") or source.endswith(".avi"):
            cam_name = "Recorded Video File"
            source_type = "file"
        else:
            cam_name = "Tactical Surveillance Feed"
            source_type = "rtsp"

    print("\n" + "-" * 64)
    print(f" Initializing Computer Vision Engine...")
    print(f" Source:      {source}")
    print(f" Designation: {cam_name}")
    print(f" Target:      {broadcaster_url}")
    print("-" * 64)

    camera_manager = CameraManager()
    camera_id = "CAM-LIVE"

    try:
        camera_manager.add_camera(
            camera_id=camera_id,
            name=cam_name,
            source=source,
            type=source_type,
        )
    except Exception:
        camera_manager.update_status(camera_id, "running")

    worker = CameraWorker(
        camera_id=camera_id,
        source=source,
        camera_manager=camera_manager,
        source_type=source_type,
    )
    worker.start()

    # Define +6M tactical perimeter fence (lower half of 1280x720 frame: y=450 to 720)
    zone = Zone("+6M-FENCE", points=[(0, 450), (1280, 450), (1280, 720), (0, 720)])
    event_manager = EventManager()

    pipeline = DetectionPipeline(
        camera_id=camera_id,
        camera_worker=worker,
        event_manager=event_manager,
        zone=zone,
        camera_name=cam_name,
        user_id=999999,
        user_email="operator@netra-ai.mil",
        user_name="Tactical Operator",
        user_rank="Major General",
        broadcaster_url=broadcaster_url,
        api_alert_url=api_alert_url,
    )
    pipeline.start()

    print("\n" + "=" * 64)
    print("  STREAMING ACTIVE!")
    print(f"  • Open your website in ANY browser: {user_url}")
    print(f"  • Devices watching the site will receive live video & beeping alerts!")
    print("  • Press Ctrl+C at any time to stop streaming.")
    print("=" * 64 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping streaming pipeline...")
        pipeline.stop()
        worker.stop()
        print("Done. Edge stream terminated.")


if __name__ == "__main__":
    main()
