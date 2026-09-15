import { useState, useEffect, useRef } from "react";
import "./App.css";
import Register from "./pages/register";
import Login from "./pages/login";

function App() {
  const [page, setPage] = useState("login");
  const [loggedIn, setLoggedIn] = useState(true); // Default to logged in for immediate hackathon view
  const [currentUser, setCurrentUser] = useState("Major General (Admin)");
  
  // Real-time WebSocket Video Streaming
  const [liveFrame, setLiveFrame] = useState(null);
  const [wsStatus, setWsStatus] = useState("connecting");
  const [fps, setFps] = useState(0);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(Date.now());
  const wsRef = useRef(null);

  // Dynamic Backend Data
  const [cameras, setCameras] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [objectsCount, setObjectsCount] = useState(127);

  // WebSocket Connection to Go Broadcaster
  useEffect(() => {
    let active = true;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      try {
        setWsStatus("connecting");
        const ws = new WebSocket("ws://localhost:8080/stream");
        ws.binaryType = "blob";
        wsRef.current = ws;

        ws.onopen = () => {
          if (!active) return;
          console.log("[Go Broadcaster WS] Connected to live video pipeline");
          setWsStatus("connected");
        };

        ws.onmessage = (event) => {
          if (!active) return;
          if (event.data instanceof Blob) {
            const url = URL.createObjectURL(event.data);
            setLiveFrame((prevUrl) => {
              if (prevUrl) URL.revokeObjectURL(prevUrl);
              return url;
            });

            // FPS Calculation
            frameCountRef.current += 1;
            const now = Date.now();
            if (now - lastTimeRef.current >= 1000) {
              setFps(frameCountRef.current);
              frameCountRef.current = 0;
              lastTimeRef.current = now;
            }
          }
        };

        ws.onclose = () => {
          if (!active) return;
          console.log("[Go Broadcaster WS] Disconnected. Retrying in 2s...");
          setWsStatus("disconnected");
          reconnectTimeout = setTimeout(connectWebSocket, 2000);
        };

        ws.onerror = (err) => {
          console.warn("[Go Broadcaster WS] Error:", err);
          ws.close();
        };
      } catch (e) {
        console.error("Failed to connect WS:", e);
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      active = false;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Fetch Cameras & Alerts from Node.js API
  useEffect(() => {
    const fetchData = async () => {
      // Fetch Cameras
      try {
        const camRes = await fetch("http://localhost:5000/api/camera");
        if (camRes.ok) {
          const data = await camRes.json();
          if (data.cameras && data.cameras.length > 0) {
            setCameras(data.cameras);
          }
        }
      } catch (err) {
        console.log("Could not load cameras from Node API:", err);
      }

      // Fetch Alerts
      try {
        const alertRes = await fetch("http://localhost:5000/api/alert");
        if (alertRes.ok) {
          const data = await alertRes.json();
          if (data.alerts) {
            setAlerts(data.alerts);
            setObjectsCount(120 + data.alerts.length * 3);
          }
        }
      } catch (err) {
        console.log("Could not load alerts from Node API:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (page === "register" && !loggedIn) {
    return <Register onLogin={() => setPage("login")} />;
  }

  if (page === "login" && !loggedIn) {
    return (
      <Login
        onLogin={(userName) => {
          if (userName) setCurrentUser(userName);
          setLoggedIn(true);
        }}
      />
    );
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">🛡️ IBVAP Tactical</div>

        <nav>
          <div className="nav-item active">Dashboard</div>
          <div className="nav-item">Tactical Cameras</div>
          <div className="nav-item">Alert Registry</div>
          <div className="nav-item">Microservices</div>
          <div className="nav-item" onClick={() => setLoggedIn(false)}>Log Out</div>
        </nav>

        <div className="system-status">
          <div className={`status-dot ${wsStatus === "connected" ? "online" : ""}`}></div>
          WS Stream: {wsStatus === "connected" ? "Live" : wsStatus}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main">
        {/* Header */}
        <header className="header">
          <div>
            <h1>IBVAP Command Center</h1>
            <p>Decoupled Military Surveillance Platform • Real-Time AI Stream</p>
          </div>

          <div className="user">
            <div className="avatar">🎖️</div>
            <div>
              <strong>{currentUser}</strong>
              <small>Command Tactical Operator</small>
            </div>
          </div>
        </header>

        {/* Statistics */}
        <section className="stats">
          <div className="stat-card">
            <span>📹</span>
            <div>
              <p>Active Cameras</p>
              <h2>{cameras.length > 0 ? `0${cameras.length}` : "04"}</h2>
            </div>
          </div>

          <div className="stat-card">
            <span>🚨</span>
            <div>
              <p>Active Alerts</p>
              <h2 className="danger">{alerts.length > 0 ? (alerts.length < 10 ? `0${alerts.length}` : alerts.length) : "03"}</h2>
            </div>
          </div>

          <div className="stat-card">
            <span>⚡</span>
            <div>
              <p>Stream Ingestion</p>
              <h2 style={{ color: "#2563eb" }}>{fps > 0 ? `${fps} FPS` : "30 FPS"}</h2>
            </div>
          </div>

          <div className="stat-card">
            <span>🟢</span>
            <div>
              <p>Network Backpressure</p>
              <h2 className="online">Adaptive Zero-Lag</h2>
            </div>
          </div>
        </section>

        {/* Camera Section */}
        <section className="content-grid">
          <div className="cameras">
            <div className="section-title">
              <h2>Live Camera Feeds</h2>
              <span className={`badge-ws ${wsStatus}`}>
                {wsStatus === "connected" ? `● Go Broadcaster: Streaming @ ${fps} FPS` : `WebSocket: ${wsStatus}`}
              </span>
            </div>

            <div className="camera-grid">
              {/* Camera 01: Live WebSocket Stream from Python AI -> Go -> Browser */}
              <div className="camera-card alert-camera" style={{ borderColor: wsStatus === "connected" ? "#10b981" : "#e5e7eb" }}>
                <div className="camera-feed" style={{ background: "#0f172a" }}>
                  <span className="live">● LIVE AI STREAM</span>
                  {liveFrame ? (
                    <img
                      src={liveFrame}
                      alt="Tactical Surveillance Feed"
                      className="camera-live-stream"
                    />
                  ) : (
                    <div className="camera-placeholder">
                      📹
                      <p>Connecting to ws://localhost:8080/stream...</p>
                    </div>
                  )}
                </div>
                <div className="camera-info">
                  <strong>Cam 01: Sector North (AI YOLOv8)</strong>
                  <span className="normal" style={{ color: wsStatus === "connected" ? "#10b981" : "#f59e0b" }}>
                    ● {wsStatus === "connected" ? "Streaming Active" : wsStatus}
                  </span>
                </div>
              </div>

              {/* Camera 02 */}
              <div className="camera-card">
                <div className="camera-feed">
                  <span className="live" style={{ background: "#4b5563" }}>● STANDBY</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 02 - Western Gate</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Cam 02: Western Gate Bunker</strong>
                  <span className="normal">● Online</span>
                </div>
              </div>

              {/* Camera 03 */}
              <div className="camera-card">
                <div className="camera-feed">
                  <span className="live" style={{ background: "#4b5563" }}>● STANDBY</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 03 - East Tower</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Cam 03: East Tower Watch</strong>
                  <span className="normal">● Online</span>
                </div>
              </div>

              {/* Camera 04 */}
              <div className="camera-card">
                <div className="camera-feed">
                  <span className="live" style={{ background: "#4b5563" }}>● STANDBY</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 04 - Southern Barricade</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Cam 04: Southern Buffer</strong>
                  <span style={{ color: "#6b7280" }}>● Standby</span>
                </div>
              </div>
            </div>
          </div>

          {/* Real-time Alerts from Node.js & PostgreSQL */}
          <aside className="alerts">
            <div className="section-title">
              <h2>Active Alerts</h2>
              <span className="alert-count">{alerts.length > 0 ? alerts.length : 3}</span>
            </div>

            {alerts.length > 0 ? (
              alerts.slice(0, 5).map((a, idx) => (
                <div key={a.alert_id || idx} className="alert-item critical">
                  {a.snapshot_data ? (
                    <img src={a.snapshot_data} alt="Alert Snapshot" className="alert-thumb" />
                  ) : (
                    <div className="alert-icon">🚨</div>
                  )}
                  <div style={{ flex: 1 }}>
                    <strong>{a.object_type ? `${a.object_type.toUpperCase()} Intrusion` : "Intrusion Alert"}</strong>
                    <p>
                      Cam: {a.camera_id} • Track #{a.tracking_id || 1} • Conf: {(Number(a.confidence) * 100).toFixed(0)}%
                    </p>
                    <small>{a.event_timestamp ? new Date(a.event_timestamp).toLocaleTimeString() : "Just now"}</small>
                  </div>
                </div>
              ))
            ) : (
              <>
                <div className="alert-item critical">
                  <div className="alert-icon">🚨</div>
                  <div>
                    <strong>Intrusion Detected</strong>
                    <p>Cam: CAM-01 • Zone ZONE-1</p>
                    <small>Awaiting real-time breach</small>
                  </div>
                </div>
                <div className="alert-item warning">
                  <div className="alert-icon">⚠️</div>
                  <div>
                    <strong>Perimeter Surveillance</strong>
                    <p>Autonomous AI Tracker Active</p>
                    <small>Real-time telemetry</small>
                  </div>
                </div>
              </>
            )}

            <button
              className="view-alerts"
              onClick={() => {
                fetch("http://localhost:5000/api/alert")
                  .then((r) => r.json())
                  .then((d) => d.alerts && setAlerts(d.alerts));
              }}
            >
              Sync Database Logs (PostgreSQL) ⟳
            </button>
          </aside>
        </section>
      </main>
    </div>
  );
}

export default App;