from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.camera_api import router as camera_router, start_camera

app = FastAPI(title="IBVAP AI Backend")

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
    try:
        start_camera("CAM-01")
        print("[AI Backend] Successfully auto-started CAM-01 tactical pipeline")
    except Exception as e:
        print(f"[AI Backend] Camera startup status: {e}")


@app.get("/")
def home():
    return {
        "service": "IBVAP AI Engine",
        "status": "online",
        "ingest_target": "http://localhost:8080/ingest",
        "database_api": "http://localhost:5000/api"
    }