import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [userName, setUserName] = useState("");
  const [chosenSkillLevel, setChosenSkillLevel] = useState("");
  const [skillLevels, setSkillLevels] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8080/api/skill-levels")
      .then((res) => res.json())
      .then((data) => setSkillLevels(data))
      .catch((err) => console.error("Failed to fetch skill levels:", err));
  }, []);

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8080/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, userName, chosenSkillLevel }),
      });
      const data = await response.json();

      if (!response.ok) throw new Error(data.error || "Signup failed");

      alert("Signup successful! Please login.");
      navigate("/login");
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div>
      <h1>Signup</h1>
      <form onSubmit={handleSignup}>
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <input type="text" placeholder="Username" value={userName} onChange={(e) => setUserName(e.target.value)} required />

        <select value={chosenSkillLevel} onChange={(e) => setChosenSkillLevel(e.target.value)} required>
          <option value="">Select Skill Level</option>
          {skillLevels.map((level) => (
            <option key={level.skillLevelID} value={level.skillLevelID}>
              {level.skillLevel}
            </option>
          ))}
        </select>

        <button type="submit">Signup</button>
      </form>
      <button onClick={() => navigate("/login")}>Already have an account? Login</button>
    </div>
  );
};

export default Signup;
