import React, { Fragment, useEffect, useState } from "react";
import { MessageSquare, X } from "lucide-react";

const API_ANALYSE_UNIT = (id) => `http://127.0.0.1:8080/api/performance/unit/${id}`;
const API_SKILL_UPDATE = "http://127.0.0.1:8080/api/performance/skill-level";

const SuggestionBox = ({ unitId , onFeedback  }) => {
  const [unitSummary, setUnitSummary] = useState(null);
  const [unitLocked, setUnitLocked] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const [feedbackHandled, setFeedbackHandled] = useState(false);
  const [updatingLvl, setUpdatingLvl] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const analyseLastCompletedUnit = async () => {
      for (let i = unitId - 1; i >= 1; i--) {
        try {
          const res = await fetch(API_ANALYSE_UNIT(i), {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` }
          });
          const result = await res.json();
          if (result.success) {
            setUnitSummary({
              summary: result.feedback.aiSummary,
              prompt: result.feedback.feedbackPrompt,
              levelSug: result.feedback.levelSuggestion,
              unitName: `Unit ${i}`,
            });
            if (onFeedback) {
              onFeedback({
                tagInsights: result.feedback.tagPerformance ?? [],
                unitLabel: `Unit ${i}`
              });
            }            
            setUnitLocked(false);
            setShowPrompt(!!result.feedback.feedbackPrompt);
            return;
          }          
        } catch (e) {
          console.error("Error fetching feedback:", e);
        }
      }
      setUnitLocked(true);
    };

    analyseLastCompletedUnit();
  }, [unitId]);

  const handleLevelOk = async () => {
    if (updatingLvl) return;
    setUpdatingLvl(true);
    try {
      const token = localStorage.getItem("token");
      await fetch(API_SKILL_UPDATE, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ skillLevel: unitSummary.levelSug }),
      });
      setShowPrompt(false);
      setFeedbackHandled(true);
    } catch (e) {
      alert("Level update failed: " + e.message);
    }
    setUpdatingLvl(false);
  };

  return (
    <div className="card suggestion-box">
      <div className="card-header">
        <h3>Quick Note</h3>
        <MessageSquare className="card-icon" />
      </div>

      {unitLocked || !unitSummary ? (
        <p>Keep going!</p>
      
      ) : feedbackHandled ? (
        <p>Keep going! Finish Unit {unitId} for your next AI review.</p>
      ) : (
        <Fragment>
          <p className="note-text">{unitSummary.summary}</p>
          {showPrompt && (
            <>
              <p className="suggestion-text">{unitSummary.prompt}</p>
              <div className="btn-row">
                <button className="btn confirm" onClick={handleLevelOk}>OK</button>
                <button className="btn cancel" onClick={() => {
                  setShowPrompt(false);
                  setFeedbackHandled(true);
                }}>
                  <X size={14} />
                </button>
              </div>
            </>
          )}
        </Fragment>
      )}
    </div>
  );



};

export default SuggestionBox;
