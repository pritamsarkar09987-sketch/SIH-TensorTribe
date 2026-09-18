import multer from "multer";
import path from "path";
import fs from "fs";
import { pool } from "../db/connectdb.js";

// Helper to reliably locate the shared uploads folder
const getUploadsDir = () => {
  const candidates = [
    path.resolve(process.cwd(), "uploads"),
    path.resolve(process.cwd(), "..", "uploads"),
    "D:\\ibvap-workspace\\SIH-TensorTribe\\uploads",
  ];
  for (const dir of candidates) {
    try {
      if (fs.existsSync(dir)) return dir;
    } catch (e) {}
  }
  const fallback = path.resolve(process.cwd(), "..", "uploads");
  try {
    fs.mkdirSync(fallback, { recursive: true });
  } catch (e) {}
  return fallback;
};

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, getUploadsDir());
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname) || ".mp4";
    const cleanName = path.basename(file.originalname, ext).replace(/[^a-zA-Z0-9_-]/g, "_");
    cb(null, `${Date.now()}-${cleanName}${ext}`);
  },
});

export const videoUploadMiddleware = multer({
  storage,
  limits: { fileSize: 500 * 1024 * 1024 }, // 500MB
});

// Helper to notify Python AI backend to switch / start RTSP ingestion
const triggerAiIngestion = async (cameraData) => {
  try {
    const res = await fetch("http://127.0.0.1:8000/cameras/ingest_dynamic", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cameraData),
      signal: AbortSignal.timeout(15000),
    });
    const data = await res.json();
    console.log("[Camera Controller] Python AI dynamic ingestion response:", data);
  } catch (err) {
    console.warn("[Camera Controller] Note: Python AI pipeline dynamic trigger:", err.message);
  }
};

export const uploadVideoCameraController = async (req, res) => {
  try {
    const isDemo = req.headers["x-demo-user"] === "true" || req.body.isDemo === "true";
    const userId = isDemo ? 999999 : (req.user?.id || 999999);

    if (!req.file) {
      return res.status(400).json({ error: "Please select a valid video file (.mp4, .avi, .mkv, .mov) to upload." });
    }

    const videoPath = req.file.path;
    const cameraName = (req.body.cameraName || req.file.originalname || "Uploaded Recon Video").trim();
    const location = (req.body.location || "Sector Tactical Recon Ground").trim();

    // Set other cameras for this user to inactive so uploaded video is primary
    await pool.query(
      `UPDATE user_cameras SET is_active = false WHERE user_id = $1`,
      [userId],
    );

    // Insert into user_cameras
    const result = await pool.query(
      `INSERT INTO user_cameras
        (user_id, camera_name, rtsp_link, location, status, is_active)
       VALUES ($1, $2, $3, $4, 'online', true)
       RETURNING
        id,
        user_id AS "userId",
        camera_name AS "cameraName",
        rtsp_link AS "rtspUrl",
        location,
        status,
        is_active AS "isActive",
        created_at AS "createdAt",
        updated_at AS "updatedAt"`,
      [userId, cameraName, videoPath, location],
    );

    const newCamera = result.rows[0];

    // Trigger Python AI dynamic ingestion on the uploaded video
    await triggerAiIngestion({
      camera_id: `CAM-${newCamera.id}`,
      camera_name: newCamera.cameraName,
      rtsp_link: videoPath,
      user_id: userId,
      user_email: isDemo ? "demo.operator@ibvap.mil" : (req.user?.email || "operator@ibvap.mil"),
      user_name: isDemo ? "Major General Vikram Singh" : (req.user?.fullname || "Tactical Operator"),
      user_rank: isDemo ? "Major General" : (req.user?.rank || "Captain"),
    });

    return res.status(201).json({
      message: "Video uploaded and live computer vision detection started!",
      camera: newCamera,
      hasActiveCamera: true,
    });
  } catch (err) {
    console.error("Error in uploadVideoCameraController:", err.message);
    return res.status(500).json({ error: "Failed to upload and process video." });
  }
};

export const getUserCamerasController = async (req, res) => {
  try {
    const isDemo = req.headers["x-demo-user"] === "true" || req.query.demo === "true";
    const userId = isDemo ? 999999 : req.user?.id;

    if (userId) {
      const result = await pool.query(
        `SELECT
          id,
          user_id AS "userId",
          camera_name AS "cameraName",
          rtsp_link AS "rtspUrl",
          location,
          status,
          is_active AS "isActive",
          created_at AS "createdAt",
          updated_at AS "updatedAt"
         FROM user_cameras
         WHERE user_id = $1
         ORDER BY is_active DESC, created_at DESC`,
        [userId],
      );

      return res.status(200).json({
        cameras: result.rows,
        hasActiveCamera: result.rows.length > 0,
      });
    }

    return res.status(200).json({
      cameras: [],
      hasActiveCamera: false,
    });
  } catch (error) {
    console.log("Error in getUserCamerasController:", error.message);
    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

export const addUserCameraController = async (req, res) => {
  try {
    const { cameraName, rtsp_link, rtsp_url, location, isDemo: clientDemo } = req.body;
    const isDemo = clientDemo || req.headers["x-demo-user"] === "true";
    let rtspStream = (rtsp_link || rtsp_url || "").trim();
    // Auto-sanitize accidental "ip:" typos, e.g. rtsp://ip:100.98.7.93:8080/...
    rtspStream = rtspStream
      .replace(/^rtsp:\/\/ip:/i, "rtsp://")
      .replace(/^rtsps:\/\/ip:/i, "rtsps://")
      .replace(/^http:\/\/ip:/i, "http://")
      .replace(/^https:\/\/ip:/i, "https://");

    const name = (cameraName || "Tactical Perimeter Cam").trim();
    const loc = (location || "Perimeter Sector Alpha").trim();
    const userId = isDemo ? 999999 : (req.user?.id || 999999);

    if (!rtspStream) {
      return res.status(400).json({
        error: "RTSP stream link is required!",
      });
    }

    // Set other cameras for this user to inactive so new camera is primary
    await pool.query(
      `UPDATE user_cameras SET is_active = false WHERE user_id = $1`,
      [userId],
    );

    // Insert dynamic camera linked to user
    const result = await pool.query(
      `INSERT INTO user_cameras
        (user_id, camera_name, rtsp_link, location, status, is_active)
       VALUES ($1, $2, $3, $4, 'online', true)
       RETURNING
        id,
        user_id AS "userId",
        camera_name AS "cameraName",
        rtsp_link AS "rtspUrl",
        location,
        status,
        is_active AS "isActive",
        created_at AS "createdAt",
        updated_at AS "updatedAt"`,
      [userId, name, rtspStream, loc],
    );

    const newCamera = result.rows[0];

    // Trigger Python AI pipeline dynamic ingestion in background
    await triggerAiIngestion({
      camera_id: `CAM-${newCamera.id}`,
      camera_name: newCamera.cameraName,
      rtsp_link: rtspStream,
      user_id: userId,
      user_email: isDemo ? "demo.operator@ibvap.mil" : (req.user?.email || "operator@ibvap.mil"),
      user_name: isDemo ? "Major General Vikram Singh" : (req.user?.fullname || "Tactical Operator"),
      user_rank: isDemo ? "Major General" : (req.user?.rank || "Captain"),
    });

    return res.status(201).json({
      message: "Camera linked successfully!",
      camera: newCamera,
      hasActiveCamera: true,
    });
  } catch (error) {
    console.log("Error in addUserCameraController:", error.message);
    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

export const deleteUserCameraController = async (req, res) => {
  try {
    const { cameraId } = req.params;
    const userId = req.user?.id;

    let result;
    if (userId) {
      result = await pool.query(
        `DELETE FROM user_cameras WHERE id = $1 AND user_id = $2 RETURNING id`,
        [cameraId, userId],
      );
    } else {
      result = await pool.query(
        `DELETE FROM user_cameras WHERE id = $1 RETURNING id`,
        [cameraId],
      );
    }

    if (result.rows.length === 0) {
      return res.status(404).json({
        message: "Camera not found or unauthorized",
      });
    }

    return res.status(200).json({
      message: "Camera deleted successfully",
    });
  } catch (error) {
    console.log("Error in deleteUserCameraController:", error.message);
    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

// Aliases for backward compatibility
export const getCamerasController = getUserCamerasController;
export const createCameraController = addUserCameraController;
export const getCameraByIdController = async (req, res) => {
  try {
    const { cameraId } = req.params;
    const result = await pool.query(
      `SELECT id, user_id AS "userId", camera_name AS "cameraName", rtsp_link AS "rtspUrl", location, status, is_active AS "isActive" FROM user_cameras WHERE id = $1`,
      [cameraId],
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Camera not found!" });
    }
    return res.status(200).json({ camera: result.rows[0] });
  } catch (err) {
    return res.status(500).json({ error: "Internal server error" });
  }
};
export const updateCameraController = async (req, res) => {
  try {
    const { cameraId } = req.params;
    const { cameraName, location, rtsp_link, status, is_active } = req.body;
    const result = await pool.query(
      `UPDATE user_cameras
       SET
         camera_name = COALESCE($1, camera_name),
         location = COALESCE($2, location),
         rtsp_link = COALESCE($3, rtsp_link),
         status = COALESCE($4, status),
         is_active = COALESCE($5, is_active),
         updated_at = CURRENT_TIMESTAMP
       WHERE id = $6
       RETURNING *`,
      [cameraName, location, rtsp_link, status, is_active, cameraId],
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Camera not found" });
    }
    return res.status(200).json({ camera: result.rows[0] });
  } catch (err) {
    return res.status(500).json({ error: "Internal server error" });
  }
};
export const deleteCameraController = deleteUserCameraController;

export const activateCameraController = async (req, res) => {
  try {
    const { cameraId } = req.params;
    const isDemo = req.headers["x-demo-user"] === "true" || req.query.demo === "true";
    const userId = isDemo ? 999999 : (req.user?.id || 999999);

    // Set other cameras inactive
    await pool.query(
      `UPDATE user_cameras SET is_active = false WHERE user_id = $1`,
      [userId]
    );

    // Set selected camera active
    const result = await pool.query(
      `UPDATE user_cameras
       SET is_active = true, updated_at = CURRENT_TIMESTAMP
       WHERE id = $1 AND user_id = $2
       RETURNING
        id,
        user_id AS "userId",
        camera_name AS "cameraName",
        rtsp_link AS "rtspUrl",
        location,
        status,
        is_active AS "isActive"`,
      [cameraId, userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Camera not found for this user." });
    }

    const activeCamera = result.rows[0];

    // Trigger Python AI dynamic ingestion
    await triggerAiIngestion({
      camera_id: `CAM-${activeCamera.id}`,
      camera_name: activeCamera.cameraName,
      rtsp_link: activeCamera.rtspUrl,
      user_id: userId,
      user_email: isDemo ? "demo.operator@ibvap.mil" : (req.user?.email || "operator@ibvap.mil"),
      user_name: isDemo ? "Major General Vikram Singh" : (req.user?.fullname || "Tactical Operator"),
      user_rank: isDemo ? "Major General" : (req.user?.rank || "Captain"),
    });

    return res.status(200).json({
      message: "Camera activated successfully",
      camera: activeCamera,
    });
  } catch (error) {
    console.error("Error in activateCameraController:", error.message);
    return res.status(500).json({ error: "Internal server error." });
  }
};
