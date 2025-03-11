import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Signup = ({ onSignup }) => {  // Pass onSignup as a prop
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    dob: "",
    chosenSkillLevel: "2",
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/signup", formData);
      onSignup(response.data.user); // Save user data in App.jsx
      navigate("/dashboard"); // Redirect to dashboard after signup
    } catch (error) {
      setError(error.response?.data?.error || "Signup failed");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" name="username" placeholder="Username" value={formData.username} onChange={handleChange} required />
      <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
      <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
      <input type="date" name="dob" value={formData.dob} onChange={handleChange} required />
      <select name="chosenSkillLevel" value={formData.chosenSkillLevel} onChange={handleChange}>
        <option value="1">Beginner</option>
        <option value="2">Intermediate</option>
        <option value="3">Advanced</option>
      </select>
      <button type="submit">Sign Up</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
};

export default Signup;
