import { pool } from "../db/connectdb.js";

export const createAlertController = async (req, res) => {
  try {
    const {
      camera_id,
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

    const query = `
      INSERT INTO alerts (
        camera_id,
        event_timestamp,
        object_type,
        tracking_id,
        confidence,
        spatial_coordinates,
        snapshot_data
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *;
    `;

    const values = [
      camera_id,
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
    const query = `
      SELECT *
      FROM alerts
      ORDER BY event_timestamp DESC;
    `;

    const result = await pool.query(query);

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
