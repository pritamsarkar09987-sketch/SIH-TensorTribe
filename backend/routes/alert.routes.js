import express from "express";
import {
  createAlertController,
  getAlertByIdController,
  getAlertsController,
  updateAlertStatusController,
} from "../controller/alert.controller.js";

const alertRouter = express.Router();

alertRouter.post("/createAlert", createAlertController);
alertRouter.get("/getAllAlert", getAlertsController);
alertRouter.get("/getOneAlert/:alertId", getAlertByIdController);
alertRouter.patch("/updateAlert/:alertId", updateAlertStatusController);

export default alertRouter;
