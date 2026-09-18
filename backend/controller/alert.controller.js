import jwt from "jsonwebtoken";
import { pool } from "../db/connectdb.js";

// Helper to resolve user identity from JWT cookie, x-user-id, or x-demo-user
const resolveUserId = (req) => {
  if (req.headers["x-demo-user"] === "true" || req.query.demo === "true") {
    return 999999;
  }
  if (req.user?.id) {
    return req.user.id;
  }
  if (req.headers["x-user-id"]) {
    const parsed = parseInt(req.headers["x-user-id"], 10);
    if (!isNaN(parsed)) return parsed;
  }
  if (req.cookies?.jwt) {
    try {
      const decoded = jwt.verify(req.cookies.jwt, process.env.JWT_SECRET);
      if (decoded?.userId) return decoded.userId;
    } catch (e) {}
  }
  return null;
};

export const createAlertController = async (req, res) => {
  try {
    const {
      camera_id,
      user_id,
      event_timestamp,
      object_type,
      tracking_id,
      confidence,
      spatial_coordinates,
      snapshot_data,
    } = req.body;

    if (
      !camera_id ||
      !object_type ||
      tracking_id === undefined ||
      confidence === undefined ||
      !spatial_coordinates ||
      !snapshot_data
    ) {
      return res.status(400).json({
        error: "Required alert data is missing",
      });
    }

    // Resolve user_id: from body, or resolve from request, or resolve from user_cameras matching camera_id
    let alertUserId = user_id || resolveUserId(req);
    if (!alertUserId && camera_id) {
      const parsedId = parseInt(camera_id.toString().replace(/^CAM-/, ""), 10);
      if (!isNaN(parsedId)) {
        const camRes = await pool.query(
          "SELECT user_id FROM user_cameras WHERE id = $1",
          [parsedId]
        );
        if (camRes.rows.length > 0) {
          alertUserId = camRes.rows[0].user_id;
        }
      }
    }

    const query = `
      INSERT INTO alerts (
        camera_id,
        user_id,
        event_timestamp,
        object_type,
        tracking_id,
        confidence,
        spatial_coordinates,
        snapshot_data
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *;
    `;

    const values = [
      camera_id,
      alertUserId,
      event_timestamp || new Date(),
      object_type,
      tracking_id,
      confidence,
      spatial_coordinates,
      snapshot_data,
    ];

    const result = await pool.query(query, values);

    res.status(201).json({
      message: "Intrusion alert created successfully",
      alert: result.rows[0],
    });
  } catch (error) {
    console.error("Error in createAlertController:", error.message);

    res.status(500).json({
      error: "Internal server error.",
    });
  }
};

export const getAlertsController = async (req, res) => {
  try {
    const userId = resolveUserId(req);

    // If no user context can be resolved, do NOT leak other accounts' alerts
    if (!userId) {
      return res.status(200).json({
        count: 0,
        alerts: [],
      });
    }

    // Query alerts belonging specifically to this user or this user's cameras
    const query = `
      SELECT a.*
      FROM alerts a
      WHERE a.user_id = $1
         OR a.camera_id IN (
            SELECT 'CAM-' || id::text FROM user_cameras WHERE user_id = $1
            UNION
            SELECT id::text FROM user_cameras WHERE user_id = $1
            UNION
            SELECT camera_name FROM user_cameras WHERE user_id = $1
         )
      ORDER BY a.event_timestamp DESC;
    `;

    const result = await pool.query(query, [userId]);

    res.status(200).json({
      count: result.rows.length,
      alerts: result.rows,
    });
  } catch (error) {
    console.error("Error in getAlertsController:", error.message);

    res.status(500).json({
      error: "Internal server error.",
    });
  }
};

export const getAlertByIdController = async (req, res) => {
  try {
    const { alertId } = req.params;

    const query = `
      SELECT *
      FROM alerts
      WHERE alert_id = $1;
    `;

    const result = await pool.query(query, [alertId]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: "Alert not found",
      });
    }

    res.status(200).json({
      alert: result.rows[0],
    });
  } catch (error) {
    console.error("Error in getAlertByIdController:", error.message);

    res.status(500).json({
      error: "Internal server error.",
    });
  }
};

export const updateAlertStatusController = async (req, res) => {
  try {
    const { alert_status } = req.body;
    const { alertId } = req.params;

    const allowedStatuses = ["active", "resolved", "false_positive"];

    if (!allowedStatuses.includes(alert_status)) {
      return res.status(400).json({
        message: "Invalid alert status",
      });
    }

    const query = `
      UPDATE alerts
      SET
        alert_status = $1,
        updated_at = CURRENT_TIMESTAMP
      WHERE alert_id = $2
      RETURNING *;
    `;

    const result = await pool.query(query, [alert_status, alertId]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        message: "Alert not found",
      });
    }

    res.status(200).json({
      message: "Alert status updated successfully",
      alert: result.rows[0],
    });
  } catch (error) {
    console.error("Error in updateAlertStatusController:", error.message);

    res.status(500).json({
      error: "Internal server error.",
    });
  }
};
