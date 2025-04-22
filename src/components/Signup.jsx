import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../css/auth.css";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [userName, setUserName] = useState("");
  const [chosenSkillLevel, setChosenSkillLevel] = useState("");
  const [skillLevels, setSkillLevels] = useState([]);
  const [error, setError] = useState("");
  const [dob, setDob] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8080/api/skill-levels")
      .then((res) => res.json())
      .then((data) => setSkillLevels(data))
      .catch((err) => {
        console.error("Failed to fetch skill levels:", err);
        setError("Failed to load skill levels. Please try again later.");
      });
  }, []);

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
  
    try {
      const response = await fetch("http://127.0.0.1:8080/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Email: email,  
          Password: password,  
          userName,
          chosenSkillLevel,
          DOB: dob
        })
      });
      const data = await response.json();
  
      if (!response.ok) throw new Error(data.error || "Signup failed");
  
      console.log("Signup successful! Please login.");
      navigate("/login");
    } catch (error) {
      setError(error.message);
    }
  };
  

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        
        {error && <div className="error-message">{error}</div>}

        <form className="auth-form" onSubmit={handleSignup}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              className="form-control"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              className="form-control"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              className="form-control"
              placeholder="Choose a username"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="dob">Date of Birth</label>
            <input
              type="date"
              id="dob"
              className="form-control"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="skill-level">Skill Level</label>
            <select
              id="skill-level"
              className="form-control"
              value={chosenSkillLevel}
              onChange={(e) => setChosenSkillLevel(e.target.value)}
              required
            >
              <option value="">Select your skill level</option>
              {skillLevels.map((level) => (
                <option key={level.skillLevelID} value={level.skillLevelID}>
                  {level.skillLevel}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-block">
            Sign Up
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{" "}
          <button className="btn-text" onClick={() => navigate("/login")}>
            Log in
          </button>
        </div>
      </div>
    </div>
  );
};

export default Signup;