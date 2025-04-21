import React from "react";
import { BookOpen, Clock, CheckSquare, Square } from "lucide-react";

const Insights = ({ lessonStats, objectives, unitId }) => {
  return (
    <>
      {/* LESSON STATS */}
      <div className="cards-container">
        <div className="card">
          <div className="card-header">
            <h3>Unit {unitId} Lesson notes</h3>
            <Clock className="card-icon" />
          </div>
          {lessonStats.split("\n").map((line, idx) => (
            <div
              key={idx}
              className="clickable-card"
              onClick={() => console.log(`Clicked: ${line}`)}
            >
              {line}
            </div>
          ))}
        </div>
      </div>

      {/* OBJECTIVES */}
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
                  onClick={() => console.log(`Clicked objective: ${item.subUnitName}`)}
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
      </div>
    </>
  );
};

export default Insights;
