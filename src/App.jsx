import "./App.css";

function App() {
  return (
    <div className="app">

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          BorderWatch
        </div>

        <nav>
          <div className="nav-item active">Dashboard</div>
          <div className="nav-item">Cameras</div>
          <div className="nav-item">Alerts</div>
          <div className="nav-item">Incidents</div>
          <div className="nav-item">Settings</div>
        </nav>

        <div className="system-status">
          <div className="status-dot"></div>
          System Online
        </div>
      </aside>


      {/* Main Content */}
      <main className="main">

        {/* Header */}
        <header className="header">
          <div>
            <h1>Surveillance Dashboard</h1>
            <p>AI-powered border monitoring system</p>
          </div>

          <div className="user">
            <div className="avatar">A</div>
            <div>
              <strong>Admin</strong>
              <small>Security Operator</small>
            </div>
          </div>
        </header>


        {/* Statistics */}
        <section className="stats">

          <div className="stat-card">
            <span>📹</span>
            <div>
              <p>Active Cameras</p>
              <h2>04</h2>
            </div>
          </div>

          <div className="stat-card">
            <span>🚨</span>
            <div>
              <p>Active Alerts</p>
              <h2 className="danger">03</h2>
            </div>
          </div>

          <div className="stat-card">
            <span>👤</span>
            <div>
              <p>Objects Detected</p>
              <h2>127</h2>
            </div>
          </div>

          <div className="stat-card">
            <span>🟢</span>
            <div>
              <p>System Status</p>
              <h2 className="online">Online</h2>
            </div>
          </div>

        </section>


        {/* Camera Section */}
        <section className="content-grid">

          <div className="cameras">

            <div className="section-title">
              <h2>Live Camera Feeds</h2>
              <span>4 Cameras Connected</span>
            </div>

            <div className="camera-grid">

              <div className="camera-card">
                <div className="camera-feed">
                  <span className="live">● LIVE</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 01</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Camera 01</strong>
                  <span className="normal">● Normal</span>
                </div>
              </div>


              <div className="camera-card alert-camera">
                <div className="camera-feed">
                  <span className="live">● LIVE</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 02</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Camera 02</strong>
                  <span className="alert">● Alert</span>
                </div>
              </div>


              <div className="camera-card">
                <div className="camera-feed">
                  <span className="live">● LIVE</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 03</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Camera 03</strong>
                  <span className="normal">● Normal</span>
                </div>
              </div>


              <div className="camera-card">
                <div className="camera-feed">
                  <span className="live">● LIVE</span>
                  <div className="camera-placeholder">
                    📹
                    <p>Camera Feed 04</p>
                  </div>
                </div>
                <div className="camera-info">
                  <strong>Camera 04</strong>
                  <span className="normal">● Normal</span>
                </div>
              </div>

            </div>
          </div>


          {/* Alerts */}
          <aside className="alerts">

            <div className="section-title">
              <h2>Active Alerts</h2>
              <span className="alert-count">3</span>
            </div>

            <div className="alert-item critical">
              <div className="alert-icon">🚨</div>
              <div>
                <strong>Intrusion Detected</strong>
                <p>Camera 02 • Zone A</p>
                <small>2 minutes ago</small>
              </div>
            </div>

            <div className="alert-item warning">
              <div className="alert-icon">⚠️</div>
              <div>
                <strong>Loitering Detected</strong>
                <p>Camera 01 • Zone B</p>
                <small>7 minutes ago</small>
              </div>
            </div>

            <div className="alert-item warning">
              <div className="alert-icon">⚠️</div>
              <div>
                <strong>Unknown Movement</strong>
                <p>Camera 04 • Zone C</p>
                <small>12 minutes ago</small>
              </div>
            </div>

            <button className="view-alerts">
              View All Alerts →
            </button>

          </aside>

        </section>

      </main>
    </div>
  );
}

export default App;