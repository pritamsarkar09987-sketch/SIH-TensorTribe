import jwt from 'jsonwebtoken';
import { pool } from '../db/connectdb.js';

const protectRoute = async (req, res, next) => {
  try {
    const token = req.cookies.jwt; 
    if (!token) {
      return res
        .status(401)
        .json({ error: "Unauthorized! No token provided." });
    }
    const decoded = jwt.verify(token, process.env.JWT_SECRET); 
    if (!decoded) {
      return res.status(401).json({ error: "Unauthorized! Invalid token." });
    }
    const result = await pool.query(
      `SELECT id, fullname, email, gender, profile_pic, role FROM users WHERE id = $1`,
      [decoded.userId]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found!" });
    }
    req.user = result.rows[0];
    next();
  } catch (error) {
    console.log("Error in protectRoute:", error.message); 
    res.status(500).json({ error: "Internal server error!" });     
  }
};

export default protectRoute;