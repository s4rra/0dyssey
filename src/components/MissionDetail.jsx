import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../css/mission-detail.css"; // You'll need to create this CSS file

function MissionDetail() {
  const { missionId } = useParams();
  const navigate = useNavigate();
  const [mission, setMission] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  const API_URL = `http://127.0.0.1:8080/api/mission/${missionId}`;
  const SUBMIT_URL = `http://127.0.0.1:8080/api/mission/${missionId}/answer`;

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
          throw new Error("Failed to fetch mission details");
        }
        return res.json();
      })
      .then((data) => {
        setMission(data);
        
        // If mission is already completed, set the result and answer
        if (data.isCompleted) {
          setResult({
            isCorrect: data.isCorrect,
            correctAnswer: data.correctAnswer
          });
          setSelectedAnswer(data.userAnswer);
        }
        
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching mission details:", err);
        setError("Failed to load mission. Please try again later.");
        setLoading(false);
      });
  }, [API_URL, navigate]);

  const handleAnswerSelect = (answer) => {
    if (result || mission?.isCompleted) return; // Don't allow changing if already submitted
    setSelectedAnswer(answer);
  };

  const handleSubmit = () => {
    if (!selectedAnswer || submitting) return;
    
    setSubmitting(true);
    const token = localStorage.getItem("token");

    fetch(SUBMIT_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        answer: selectedAnswer
      })
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to submit answer");
        }
        return res.json();
      })
      .then((data) => {
        setResult(data);
        setSubmitting(false);
      })
      .catch((err) => {
        console.error("Error submitting answer:", err);
        setError("Failed to submit answer. Please try again.");
        setSubmitting(false);
      });
  };

  if (loading) return <p>Loading mission...</p>;
  if (error) return <p className="error-message">{error}</p>;
  if (!mission) return <p>Mission not found</p>;

  return (
    <div className="mission-detail-container">
      <button
        onClick={() => navigate("/missions")}
        className="back-button"
      >
        ← Back to Missions
      </button>
      
      <div className="mission-card-detail">
        <h1 className="mission-question">{mission.question}</h1>
        
        <div className="options-container">
          {Object.entries(mission.options).map(([key, value]) => (
            <div
              key={key}
              onClick={() => handleAnswerSelect(key)}
              className={`
                option-item
                ${selectedAnswer === key ? "selected" : ""}
                ${result && key === result.correctAnswer ? "correct-answer" : ""}
                ${result && selectedAnswer === key && key !== result.correctAnswer ? "wrong-answer" : ""}
              `}
            >
              <span className="option-key">{key}:</span> {value}
            </div>
          ))}
        </div>
        
        {!mission.isCompleted && !result && (
          <button
            onClick={handleSubmit}
            disabled={!selectedAnswer || submitting}
            className={`submit-button ${!selectedAnswer || submitting ? "disabled" : ""}`}
          >
            {submitting ? "Submitting..." : "Submit Answer"}
          </button>
        )}
        
        {result && (
          <div className={`result-container ${result.isCorrect ? "correct" : "incorrect"}`}>
            <h3 className="result-title">
              {result.isCorrect ? "Correct! 🎉" : "Sorry, that's not right."}
            </h3>
            <p className="result-message">
              {result.isCorrect 
                ? `You earned ${mission.points} points!` 
                : `The correct answer was ${result.correctAnswer}.`}
            </p>
          </div>
        )}
      </div>
      
      <div className="mission-footer-info">
        {mission.isCompleted 
          ? "You have already completed this mission." 
          : `This mission is worth ${mission.points} points.`}
      </div>
    </div>
  );
}

export default MissionDetail;