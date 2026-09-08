import { useState } from "react";

function Register({ onLogin }) {
  const [fullname, setFullname] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [gender, setGender] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    const registerData = {
      fullname: fullname,
      email: email,
      password: password,
      confirmPassword: confirmPassword,
      gender: gender,
    };

    console.log("Registration Data:", registerData);

    
  };

  return (
    <div className="login-page">
      <div className="login-card">

        <div className="login-logo">
          🛡️
        </div>

        <h1>Create Account</h1>
        <p>Register for BorderWatch</p>

        <form onSubmit={handleSubmit}>

          <div className="input-group">
            <label>Full Name</label>
            <input
              type="text"
              placeholder="Enter your full name"
              value={fullname}
              onChange={(e) => setFullname(e.target.value)}
              required
            />
          </div>

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
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Gender</label>

            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              required
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          <button type="submit" className="login-button">
            Create Account
          </button>
        <p className="switch-page">
                Already have an account?{" "}
             <button type="button" onClick={onLogin}>
             Login
            </button>
         </p>

        </form>

        <p className="login-footer">
          Authorized personnel only
        </p>

      </div>
    </div>
  );
}

export default Register;