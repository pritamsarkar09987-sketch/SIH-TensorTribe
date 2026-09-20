import pg from "pg";
import dotenv from "dotenv";
dotenv.config();

const { Pool } = pg;

const isCloudHost = (host) => {
  if (!host) return false;
  return host !== "localhost" && host !== "127.0.0.1" && host !== "::1";
};

const poolConfig = process.env.DATABASE_URL
  ? {
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.DB_SSL === "false" ? false : { rejectUnauthorized: false },
    }
  : {
      user: process.env.DB_USER || "postgres.uiewamjcjmygmynbczlc",
      host: process.env.DB_HOST || "aws-0-ap-south-1.pooler.supabase.com",
      database: process.env.DB_NAME || "postgres",
      password: process.env.DB_PASSWORD || "dead98.xdxdx",
      port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 5432,
      ssl: { rejectUnauthorized: false },
    };

export const pool = new Pool(poolConfig);

const connectDB = async () => {
  try {
    const client = await pool.connect();
    const res = await client.query("SELECT current_database(), current_user;");
    const dbInfo = res.rows[0];
    console.log(
      `PostgreSQL connected successfully! (Database: ${dbInfo.current_database}, User: ${dbInfo.current_user})`
    );
    client.release();
    return true;
  } catch (error) {
    console.error("PostgreSQL connection notice:", error.message);
    if (error.message.includes('database "ibvap" does not exist')) {
      console.error(
        "Hint: In cloud providers like Supabase or Neon, the default database is usually 'postgres' or 'neondb'. Set DB_NAME=postgres in your .env file."
      );
    }
    return false;
  }
};

export default connectDB;
