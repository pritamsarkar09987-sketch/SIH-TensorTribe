import os
# Configure OpenCV FFMPEG RTSP options globally before importing cv2
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;4000000|buffer_size;1024000"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.camera_api import router as camera_router

app = FastAPI(title="IVVP AI Computer Vision Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(camera_router)


@app.on_event("startup")
def startup_event():
    print("[IVVP AI Engine] Computer Vision service initialized with +10M Perimeter ROI and Email Alerting.")


@app.get("/")
def home():
    return {
        "service": "IVVP AI Computer Vision Engine",
        "status": "online",
        "ingest_target": "http://localhost:5000/ingest",
        "database_api": "http://localhost:5000/api",
        "roi_perimeter": "+10-Meter Restricted Yellow Bracket",
    }