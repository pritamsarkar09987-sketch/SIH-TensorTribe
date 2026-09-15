import express from "express";
import protectRoute from "../middleware/protectRoute.js";
import {
  createCameraController,
  getCameraByIdController,
  getCamerasController,
  updateCameraController,
} from "../controller/camera.controller.js";

const cameraRouter = express.Router();

cameraRouter.post("/addCamera", createCameraController);
cameraRouter.get("/getAllCamera", protectRoute, getCamerasController);
cameraRouter.get(
  "/getCameraById/:cameraId",
  protectRoute,
  getCameraByIdController,
);
cameraRouter.patch(
  "/updateCamera/:cameraId",
  protectRoute,
  updateCameraController,
);
cameraRouter.delete(
  "/deleteCamera/:cameraId",
  protectRoute,
  getCameraByIdController,
);

export default cameraRouter;
