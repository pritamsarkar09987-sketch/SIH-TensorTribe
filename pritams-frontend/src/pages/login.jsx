import { useState } from "react";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const res = await fetch("http://localhost:5000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (res.ok) {
        onLogin(data.fullname || "Operator");
      } else {
        setErrorMsg(data.error || "Login failed");
      }
    } catch (err) {
      console.warn("Backend API unavailable, using local demo bypass:", err);
      onLogin("Tactical Operator");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    onLogin("Major General (Admin)");
  };

  return (
    <div className="login-page">
      <div className="login-card">

        <div className="login-logo">
          🛡️
        </div>

        <h1>Welcome Back</h1>
        <p>Login to BorderWatch</p>

        <form onSubmit={handleSubmit}>

          <div className="input-group">
            <label>Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {errorMsg && <p style={{ color: "#dc2626", fontSize: "13px", marginBottom: "12px" }}>{errorMsg}</p>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? "Authenticating..." : "Login"}
          </button>

          <button
            type="button"
            onClick={handleDemoLogin}
            style={{
              width: "100%",
              marginTop: "10px",
              padding: "10px",
              background: "#1f2937",
              color: "#34d399",
              border: "1px dashed #34d399",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "13px"
            }}
          >
            ⚡ Quick Demo Access (Bypass)
          </button>
        </form>

        <p className="login-footer">
          Authorized personnel only
        </p>

      </div>
    </div>
  );
}

export default Login;