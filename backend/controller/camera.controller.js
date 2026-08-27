import { pool } from "../db/connectdb.js";

export const getCamerasController = async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT
        id,
        camera_name AS "cameraName",
        location,
        rtsp_url,
        status,
        created_at AS "createdAt",
        updated_at AS "updatedAt"
       FROM cameras
       ORDER BY created_at DESC`,
    );

    return res.status(200).json({
      cameras: result.rows,
    });
  } catch (error) {
    console.log("Error in getCamerasController:", error.message);

    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

export const createCameraController = async (req, res) => {
  try {
    const { cameraName, location, rtsp_url, status } = req.body;

    if (!cameraName || !location || !rtsp_url) {
      return res.status(400).json({
        error: "All fields are required!",
      });
    }

    // Check if camera already exists
    const existingCamera = await pool.query(
      `SELECT id FROM cameras WHERE rtsp_url = $1`,
      [rtsp_url],
    );

    if (existingCamera.rows.length > 0) {
      return res.status(400).json({
        error: "Camera already exists!",
      });
    }

    // Insert camera
    const result = await pool.query(
      `INSERT INTO cameras
        (camera_name, location, rtsp_url, status)
       VALUES ($1, $2, $3, $4)
       RETURNING
        id,
        camera_name AS "cameraName",
        location,
        rtsp_url,
        status,
        created_at AS "createdAt",
        updated_at AS "updatedAt"`,
      [cameraName, location, rtsp_url, status || "offline"],
    );

    return res.status(201).json({
      newCamera: result.rows[0],
      message: "New camera added successfully!",
    });
  } catch (error) {
    console.log("Error in createCameraController:", error.message);

    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

export const getCameraByIdController = async (req, res) => {
  try {
    const { cameraId } = req.params;

    const result = await pool.query(
      `SELECT
        id,
        camera_name AS "cameraName",
        location,
        rtsp_url,
        status,
        created_at AS "createdAt",
        updated_at AS "updatedAt"
       FROM cameras
       WHERE id = $1`,
      [cameraId],
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: "Camera not found!",
      });
    }

    return res.status(200).json({
      camera: result.rows[0],
    });
  } catch (error) {
    console.log("Error in getCameraByIdController:", error.message);

    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

export const updateCameraController = async (req, res) => {
  try {
    const { cameraId } = req.params;
    const { cameraName, location, rtsp_url, status } = req.body;

    const result = await pool.query(
      `UPDATE cameras
       SET
         camera_name = COALESCE($1, camera_name),
         location = COALESCE($2, location),
         rtsp_url = COALESCE($3, rtsp_url),
         status = COALESCE($4, status),
         updated_at = CURRENT_TIMESTAMP
       WHERE id = $5
       RETURNING
         id,
         camera_name AS "cameraName",
         location,
         rtsp_url,
         status,
         created_at AS "createdAt",
         updated_at AS "updatedAt"`,
      [cameraName, location, rtsp_url, status, cameraId],
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        message: "Camera not found",
      });
    }

    return res.status(200).json({
      message: "Camera updated successfully",
      camera: result.rows[0],
    });
  } catch (error) {
    console.log("Error in updateCameraController:", error.message);

    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};

export const deleteCameraController = async (req, res) => {
  try {
    const { cameraId } = req.params;

    const result = await pool.query(
      `DELETE FROM cameras
       WHERE id = $1
       RETURNING id`,
      [cameraId],
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        message: "Camera not found",
      });
    }

    return res.status(200).json({
      message: "Camera deleted successfully",
    });
  } catch (error) {
    console.log("Error in deleteCameraController:", error.message);

    return res.status(500).json({
      error: "Internal server error!",
    });
  }
};
