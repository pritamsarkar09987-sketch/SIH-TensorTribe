import express from "express";
import {
  createAlertController,
  getAlertByIdController,
  getAlertsController,
  updateAlertStatusController,
} from "../controller/alert.controller.js";

const alertRouter = express.Router();

alertRouter.post("/", createAlertController);
alertRouter.post("/createAlert", createAlertController);

alertRouter.get("/", getAlertsController);
alertRouter.get("/getAllAlert", getAlertsController);

alertRouter.get("/:alertId", getAlertByIdController);
alertRouter.get("/getOneAlert/:alertId", getAlertByIdController);

alertRouter.patch("/:alertId", updateAlertStatusController);
alertRouter.patch("/updateAlert/:alertId", updateAlertStatusController);

export default alertRouter;
