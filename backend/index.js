import cookieParser from "cookie-parser";
import dotenv from "dotenv";
dotenv.config();
import express from "express";
import authRouter from "./routes/auth.routes.js";
import connectDB from "./db/connectdb.js";
import cameraRouter from "./routes/camera.routes.js";
import alertRouter from "./routes/alert.routes.js";

const port = process.env.PORT || 5000;
const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

app.use("/api/auth", authRouter);
app.use("/api/camera", cameraRouter);
app.use("/api/alert", alertRouter);

app.listen(port, async () => {
  await connectDB();
  console.log(`app listening to the port http://localhost:${port}`);
});
