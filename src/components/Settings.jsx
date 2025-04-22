import { useNavigate } from "react-router-dom";

function Settings() {
  const navigate = useNavigate();

  const handleSignOut = () => {
    localStorage.removeItem("access_token"); // or sessionStorage
    navigate("/login"); // or wherever your login page is
  };

  return (
    <div className="settings-page">
      <h1>Settings</h1>
      <button onClick={handleSignOut}>Sign Out</button>
    </div>
  );
}

export default Settings;
