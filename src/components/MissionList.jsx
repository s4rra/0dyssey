import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../css/missionlist.css";

function MissionList() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8080/api/missions";

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          navigate("/login");
          return;
        }

        const response = await fetch(API_URL, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch missions");
        }

        const data = await response.json();
        setMissions(data.missions || []);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching missions:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMissions();
  }, [navigate]);

  const handleMissionClick = (missionId) => {
    navigate(`/missions/${missionId}`);
  };

  if (loading) return <div className="loading-container">Loading missions...</div>;
  if (error) return <div className="error-container">Error: {error}</div>;

  return (
    <div className="missions-container">
      <h2 className="missions-title">Missions</h2>
      {missions.length === 0 ? (
        <div className="no-missions">No missions available.</div>
      ) : (
        <div className="missions-grid">
          {missions.map((mission) => (
            <div 
              key={mission.missionID} 
              className={`mission-card ${mission.completed ? 'completed' : ''}`}
              onClick={() => handleMissionClick(mission.missionID)}
            >
              <div className="mission-status">
                {mission.completed ? (
                  <div className="status-badge completed">
                    <span className="status-icon">✓</span>
                    <span className="status-text">Completed</span>
                  </div>
                ) : (
                  <div className="status-badge">
                    <span></span>
                  </div>
                )}
              </div>
              
              <h3 className="mission-title">{mission.missionTitle}</h3>
              <p className="mission-description">{mission.missionDescription}</p>
              
              <div className="mission-footer">
                <div className="mission-difficulty">
                </div>
                <div className="mission-reward">
                  <span className="xp-icon">⭐</span>
                  <span className="xp-value">{mission.xpReward} XP</span>
                </div>
              </div>
              
              {mission.completed && (
                <div className="mission-score">
                  Score: {mission.score}%
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MissionList;