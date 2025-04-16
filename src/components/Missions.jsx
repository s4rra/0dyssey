import { useState, useEffect } from "react";
import { useNavigate, Outlet, useParams } from "react-router-dom";
import "../css/missions.css"; // You'll need to create this CSS file

function Missions() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { missionId } = useParams(); // Detect if a mission is selected
  const API_URL = "http://127.0.0.1:8080/api/missions";

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    fetch(API_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch missions");
        }
        return res.json();
      })
      .then((data) => {
        setMissions(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching missions:", err);
        setError("Failed to load missions. Please try again later.");
        setLoading(false);
      });
  }, [navigate]);

  const handleMissionSelect = (missionId) => {
    navigate(`/missions/${missionId}`);
  };

  if (loading) return <p>Loading missions...</p>;
  if (error) return <p className="error-message">{error}</p>;

  return (
    <div className="missions-container">
      <h2 className="missions-title">Missions</h2>
      
      {/* If a mission is selected, show its details via Outlet */}
      {missionId ? (
        <Outlet />
      ) : (
        <div className="missions-grid">
          {missions.length === 0 ? (
            <p>No missions available at the moment.</p>
          ) : (
            missions.map((mission) => (
              <div
                key={mission.missionID}
                className={`mission-card ${
                  mission.isCompleted
                    ? mission.isCorrect
                      ? "completed-correct"
                      : "completed-incorrect"
                    : ""
                }`}
                onClick={() => handleMissionSelect(mission.missionID)}
              >
                <h3 className="mission-question">{mission.question}</h3>
                <div className="mission-footer">
                  <span className="mission-points">{mission.points} points</span>
                  {mission.isCompleted ? (
                    <span className={`mission-status ${mission.isCorrect ? "correct" : "incorrect"}`}>
                      {mission.isCorrect ? "Completed ✓" : "Incorrect ✗"}
                    </span>
                  ) : (
                    <span className="mission-status pending">Take this mission</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default Missions;