from fastapi import FastAPI
from app.api.camera_api import router as camera_router

app = FastAPI()

app.include_router(camera_router)


@app.get("/")
def home():
    return {
        "message": "SIH26187 Backend is running"
    }