import React, { useEffect, useState } from "react";
import { BookOpen, Clock, CheckSquare, Square } from "lucide-react";
import { useNavigate } from "react-router-dom";


const API_OBJECTIVES = (unitId) => `http://127.0.0.1:8080/api/performance/objectives/${unitId}`;

const Insights = ({ unitId }) => {
  const [lessonStats, setLessonStats] = useState("Loading lesson stats...");
  const [objectives, setObjectives] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const fetchObjectives = async () => {
      try {
        const res = await fetch(API_OBJECTIVES(unitId), {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();

        setObjectives(data?.objectives ?? []);

        const summaries = (data?.objectives ?? [])
          .filter(obj => obj.completed && obj.aiSummary)
          .map(obj => `${obj.subUnitName}: ${obj.aiSummary}`);

        if (summaries.length) {
          setLessonStats(summaries.join("\n"));
        } else {
          setLessonStats("No recent lesson data.");
        }

      } catch (err) {
        setLessonStats("Unable to load lesson summaries.");
        setObjectives([]);
        console.error("Error fetching insights:", err);
      }
    };

    fetchObjectives();
  }, [unitId]);

  return (
    <>
      
      <div className="cards-container">
        <div className="card">
          <div className="card-header">
            <h3>Unit {unitId} Objectives</h3>
            <BookOpen className="card-icon" />
          </div>
          {objectives.length ? (
            <div className="objectives-list">
              {objectives.map((item, idx) => (
                <div
                  key={idx}
                  className="clickable-card"
                  onClick={() => navigate(`/courses/subunit/${unitId}/${item.subUnitID}`)}
                >
                  {item.completed ? (
                    <CheckSquare size={16} style={{ marginRight: "6px" }} />
                  ) : (
                    <Square size={16} style={{ marginRight: "6px" }} />
                  )}
                  {item.subUnitName}
                </div>
              ))}
            </div>
          ) : (
            <p>All lessons in Unit {unitId} are done</p>
          )}
        </div>
     
        <div className="card">
          <div className="card-header">
            <h3>Unit {unitId} Lesson Notes</h3>
            <Clock className="card-icon" />
          </div>
          <div className="lesson-notes-scrollable">
  {lessonStats.split("\n").map((line, idx) => (
    <div key={idx} className="lesson-note">
      {line}
    </div>
  ))}
</div>

        </div>
      </div>

    </>
  );
};

export default Insights;
