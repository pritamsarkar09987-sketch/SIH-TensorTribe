"""
Camera API
----------
REST endpoints for registering, listing, starting, and stopping cameras.
Delegates all real work to CameraManager and CameraWorker.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.camera.camera_manager import CameraManager
from app.camera.camera_worker import CameraWorker
from app.ai.pipeline import DetectionPipeline
from app.analytics.intrusion import Zone
from app.events.event_manager import EventManager

router = APIRouter(prefix="/cameras", tags=["cameras"])

# Single shared instances for the whole app (for now — simple is fine at this stage).
camera_manager = CameraManager()
workers: dict[str, CameraWorker] = {}
pipelines: dict[str, DetectionPipeline] = {}

# One shared EventManager for the whole app - all cameras' events
# go into this single collector (each Event already has camera_id).
event_manager = EventManager()

# Shared test zone for now - per-camera zones come later via a
# future zone_api.py.
default_zone = Zone("ZONE-1", points=[(500, 400), (1280, 400), (1280, 720), (500, 720)])


class AddCameraRequest(BaseModel):
    camera_id: str
    name: str
    source: str
    type: str


@router.post("")
def add_camera(payload: AddCameraRequest):
    try:
        camera = camera_manager.add_camera(
            camera_id=payload.camera_id,
            name=payload.name,
            source=payload.source,
            type=payload.type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return camera


@router.get("")
def list_cameras():
    return camera_manager.get_all_cameras()


@router.get("/{camera_id}")
def get_camera(camera_id: str):
    camera = camera_manager.get_camera(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/{camera_id}/start")
def start_camera(camera_id: str):
    camera = camera_manager.get_camera(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    if camera_id in workers:
        raise HTTPException(status_code=400, detail="Camera already started")

    # Now correctly passes source_type - previously always defaulted
    # to "file", so RTSP reconnect logic never actually engaged here.
    worker = CameraWorker(
        camera_id=camera_id,
        source=camera.source,
        camera_manager=camera_manager,
        source_type=camera.type,
    )
    try:
        worker.start()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    workers[camera_id] = worker

    pipeline = DetectionPipeline(
        camera_id=camera_id,
        camera_worker=worker,
        event_manager=event_manager,
        zone=default_zone,
    )
    pipeline.start()
    pipelines[camera_id] = pipeline

    return {"message": f"{camera_id} started"}


@router.post("/{camera_id}/stop")
def stop_camera(camera_id: str):
    worker = workers.get(camera_id)
    if worker is None:
        raise HTTPException(status_code=400, detail="Camera is not running")

    pipeline = pipelines.get(camera_id)
    if pipeline is not None:
        pipeline.stop()
        del pipelines[camera_id]

    worker.stop()
    del workers[camera_id]
    return {"message": f"{camera_id} stopped"}


@router.get("/{camera_id}/events")
def get_camera_events(camera_id: str):
    return [e.to_dict() for e in event_manager.get_events_for_camera(camera_id)]