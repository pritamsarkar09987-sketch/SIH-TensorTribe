import pg from "pg";
import dotenv from "dotenv";
dotenv.config();

const { Pool } = pg;

export const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
});

const connectDB = async () => {
  try {
    const client = await pool.connect();
    console.log("PostgreSQL connected successfully!");
    client.release();
  } catch (error) {
    console.error("PostgreSQL connection error:", error.message);
    process.exit(1);
  }
};

export default connectDB;
