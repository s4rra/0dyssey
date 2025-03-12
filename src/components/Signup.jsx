import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [userName, setUserName] = useState("");
  const [chosenSkillLevel, setChosenSkillLevel] = useState("");
  const [skillLevels, setSkillLevels] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSkillLevels = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8080/skill-levels");
        console.log("Fetched skill levels:", response.data); 
        setSkillLevels(response.data); 
      } catch (error) {
        console.error("Failed to fetch skill levels:", error);
      }
    };
  
    fetchSkillLevels();
  }, []);
  

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const payload = { email, password, userName, chosenSkillLevel };
      console.log("Sending payload:", payload); //debug
      const response = await axios.post(
        "http://127.0.0.1:8080/signup",
        payload
      );
      alert(response.data.message);
      navigate("/login");
    } catch (error) {
      alert(error.response?.data?.error || "Signup failed");
    }
  };

  return (
    <div>
      <h1>Signup</h1>
      <form onSubmit={handleSignup}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Username"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          required
        />
        {/* Dropdown menu for skill levels */}
        <select
          value={chosenSkillLevel}
          onChange={(e) => setChosenSkillLevel(e.target.value)}
          required
        >
          <option value="">Select Skill Level</option>
          {skillLevels.map((level) => (
            <option key={level.skillLevelID} value={level.skillLevelID}>
              {level.skillLevel}
            </option>
          ))}
        </select>

        <button type="submit">Signup</button>
      </form>
      <button onClick={() => navigate("/login")}>
        Already have an account? Login
      </button>
    </div>
  );
};

export default Signup;