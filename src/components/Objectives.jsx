import { useState, useEffect } from "react";
import "../css/objectives.css";

function Objectives() {
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = "http://127.0.0.1:8080/api/objectives";

  useEffect(() => {
    const fetchObjectives = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const response = await fetch(API_URL, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setObjectives(data.objectives || []);
      } catch (err) {
        console.error("Error fetching objectives:", err);
        setError("Failed to load objectives");
      } finally {
        setLoading(false);
      }
    };

    fetchObjectives();
  }, []);

  const handleCompleteObjective = async (subUnitId) => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/complete/${subUnitId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update the objectives list with the completed objective
      setObjectives(
        objectives.map((obj) =>
          obj.subUnitID === subUnitId
            ? { ...obj, completed: true, pointsAwarded: true }
            : obj
        )
      );

      // Return the points awarded for the Dashboard to update total points
      return data.pointsAwarded || 0;
    } catch (err) {
      console.error("Error completing objective:", err);
      return 0;
    }
  };

  if (loading) return <div className="objectives-loading">Loading objectives...</div>;
  if (error) return <div className="objectives-error">{error}</div>;
  if (objectives.length === 0) return <div className="no-objectives">No objectives available</div>;

  return (
    <div className="objectives-container">
      <h3 className="objectives-title">Learning Objectives</h3>
      <ul className="objectives-list">
        {objectives.map((objective) => (
          <li
            key={objective.subUnitID}
            className={`objective-item ${objective.completed ? "completed" : ""}`}
          >
            <div className="objective-content">
              <div className="objective-status">
                {objective.completed ? (
                  <span className="checkmark">✓</span>
                ) : (
                  <button 
                    className="complete-button"
                    onClick={() => handleCompleteObjective(objective.subUnitID)}
                  >
                    Complete
                  </button>
                )}
              </div>
              <div className="objective-info">
                <span className="objective-name">{objective.subUnitName}</span>
                {objective.completed && objective.pointsAwarded && (
                  <span className="points-badge">+10 pts</span>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Objectives;