import express from "express";
import protectRoute from "../middleware/protectRoute.js";
import {
  createCameraController,
  getCameraByIdController,
  getCamerasController,
  updateCameraController,
  deleteCameraController,
} from "../controller/camera.controller.js";

const cameraRouter = express.Router();

cameraRouter.post("/", createCameraController);
cameraRouter.post("/addCamera", createCameraController);

cameraRouter.get("/", getCamerasController);
cameraRouter.get("/getAllCamera", getCamerasController);

cameraRouter.get("/:cameraId", getCameraByIdController);
cameraRouter.get("/getCameraById/:cameraId", getCameraByIdController);

cameraRouter.patch("/:cameraId", protectRoute, updateCameraController);
cameraRouter.patch("/updateCamera/:cameraId", protectRoute, updateCameraController);

cameraRouter.delete("/:cameraId", protectRoute, deleteCameraController);
cameraRouter.delete("/deleteCamera/:cameraId", protectRoute, deleteCameraController);

export default cameraRouter;
