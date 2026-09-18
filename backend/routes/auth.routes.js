import express from "express";
import { loginController, logoutController, signupController, getMeController } from "../controller/auth.controller.js";
import protectRoute from "../middleware/protectRoute.js";

const authRouter = express.Router();

authRouter.post("/signup", signupController);
authRouter.post("/login", loginController);
authRouter.post("/logout", logoutController);
authRouter.get("/me", protectRoute, getMeController);

export default authRouter;