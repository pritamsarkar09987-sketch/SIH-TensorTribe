import express from "express";
import protectRoute from "../middleware/protectRoute.js";
import {
  createCameraController,
  getCameraByIdController,
  getCamerasController,
  updateCameraController,
  deleteCameraController,
  activateCameraController,
  uploadVideoCameraController,
  videoUploadMiddleware,
} from "../controller/camera.controller.js";

const cameraRouter = express.Router();

// Video upload endpoint (supports .mp4, .avi, .mkv, .mov files)
cameraRouter.post("/upload", videoUploadMiddleware.single("video"), uploadVideoCameraController);

cameraRouter.post("/", createCameraController);
cameraRouter.post("/addCamera", createCameraController);

cameraRouter.post("/:cameraId/activate", activateCameraController);
cameraRouter.post("/activateCamera/:cameraId", activateCameraController);

cameraRouter.get("/", getCamerasController);
cameraRouter.get("/getAllCamera", getCamerasController);

cameraRouter.get("/:cameraId", getCameraByIdController);
cameraRouter.get("/getCameraById/:cameraId", getCameraByIdController);

cameraRouter.patch("/:cameraId", protectRoute, updateCameraController);
cameraRouter.patch("/updateCamera/:cameraId", protectRoute, updateCameraController);

cameraRouter.delete("/:cameraId", deleteCameraController);
cameraRouter.delete("/deleteCamera/:cameraId", deleteCameraController);

export default cameraRouter;
