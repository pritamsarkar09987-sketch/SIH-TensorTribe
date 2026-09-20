import http from "http";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import dotenv from "dotenv";
import { WebSocketServer, WebSocket } from "ws";

dotenv.config();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

if (!process.env.DB_HOST && !process.env.DATABASE_URL) {
  const ranajitEnv = path.resolve(__dirname, "../ranajit-apis/.env");
  if (fs.existsSync(ranajitEnv)) {
    dotenv.config({ path: ranajitEnv });
  }
}

import authRouter from "./routes/auth.routes.js";
import connectDB from "./db/connectdb.js";
import cameraRouter from "./routes/camera.routes.js";
import alertRouter from "./routes/alert.routes.js";

const port = process.env.PORT || 5000;
const app = express();
const server = http.createServer(app);

// -------------------------------------------------------------
// 1. Consolidated WebSocket Video Stream Broadcaster (/stream)
// -------------------------------------------------------------
const wss = new WebSocketServer({ server, path: "/stream" });
const streamClients = new Set();

wss.on("connection", (ws, req) => {
  streamClients.add(ws);
  const clientIp = req.socket.remoteAddress;
  console.log(`[Netra AI WebSocket] Dashboard client connected (${clientIp}). Active viewers: ${streamClients.size}`);

  ws.on("close", () => {
    streamClients.delete(ws);
    console.log(`[Netra AI WebSocket] Dashboard client disconnected. Active viewers: ${streamClients.size}`);
  });

  ws.on("error", (err) => {
    console.warn(`[Netra AI WebSocket] Client error: ${err.message}`);
    streamClients.delete(ws);
  });
});

const broadcastFrame = (frameBuffer) => {
  for (const client of streamClients) {
    if (client.readyState === WebSocket.OPEN) {
      // Prevent latency buildup: if client is still receiving previous frame, drop stale frame
      if (client.bufferedAmount > 64 * 1024) {
        continue;
      }
      client.send(frameBuffer, { binary: true });
    }
  }
};

export const broadcastAlert = (alertData) => {
  try {
    const payload = JSON.stringify({ type: "INTRUSION_ALERT", alert: alertData });
    for (const client of streamClients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(payload);
      }
    }
  } catch (err) {
    console.warn("[Netra AI WebSocket] Alert broadcast notice:", err.message);
  }
};
app.set("broadcastAlert", broadcastAlert);

// -------------------------------------------------------------
// 2. High-Performance Frame Ingestion from Python AI Pipeline
// -------------------------------------------------------------
const rawBodyParser = express.raw({ type: () => true, limit: "25mb" });

app.post("/ingest", rawBodyParser, (req, res) => {
  if (req.body && Buffer.isBuffer(req.body) && req.body.length > 0) {
    broadcastFrame(req.body);
  }
  return res.status(200).send("OK");
});

app.post("/api/stream/ingest", rawBodyParser, (req, res) => {
  if (req.body && Buffer.isBuffer(req.body) && req.body.length > 0) {
    broadcastFrame(req.body);
  }
  return res.status(200).send("OK");
});

// -------------------------------------------------------------
// 3. Middleware & REST APIs
// -------------------------------------------------------------
app.use(
  cors({
    origin: true,
    credentials: true,
  })
);
app.use(express.urlencoded({ extended: true }));
app.use(express.json({ limit: "15mb" }));
app.use(cookieParser());

app.use("/api/auth", authRouter);
app.use("/api/camera", cameraRouter);
app.use("/api/alert", alertRouter);

// Health check endpoint
app.get("/api/health", (req, res) => {
  return res.status(200).json({
    status: "online",
    platform: "Netra AI Unified Platform",
    activeViewers: streamClients.size,
    timestamp: new Date().toISOString(),
  });
});

// -------------------------------------------------------------
// 4. Consolidated Frontend Dashboard Serving
// -------------------------------------------------------------
const candidateDistPaths = [
  path.resolve(__dirname, "../dist"),
  path.resolve(__dirname, "../pritams-frontend/dist"),
  path.resolve(__dirname, "../../pritams-frontend/dist"),
];
const frontendDistPath = candidateDistPaths.find((p) => fs.existsSync(p)) || candidateDistPaths[0];
app.use(express.static(frontendDistPath));

app.use((req, res, next) => {
  if (req.method === "GET" && !req.path.startsWith("/api/")) {
    return res.sendFile(path.join(frontendDistPath, "index.html"), (err) => {
      if (err) {
        res.status(200).send(`
          <html>
            <body style="background:#0c121e;color:#fff;font-family:sans-serif;padding:2rem;">
              <h2>Netra AI Tactical Command Monolith Online</h2>
              <p>API and WebSocket stream are active on port ${port}.</p>
              <p>Please run <code>npm run build</code> in the root folder or pritams-frontend to compile the static UI bundle.</p>
            </body>
          </html>
        `);
      }
    });
  }
  return res.status(404).json({ error: "Endpoint not found" });
});

// -------------------------------------------------------------
// 5. Server Startup
// -------------------------------------------------------------
server.listen(port, async () => {
  await connectDB();
  console.log(`\n==========================================================`);
  console.log(` Netra AI Consolidated Tactical Platform Online!`);
  console.log(` - Single Entry Point:   http://localhost:${port}`);
  console.log(` - REST API Base:        http://localhost:${port}/api`);
  console.log(` - WebSocket Feed:       ws://localhost:${port}/stream`);
  console.log(` - Frame Ingest Target:  http://localhost:${port}/ingest`);
  console.log(`==========================================================\n`);
});
