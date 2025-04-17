import { useState, useEffect } from "react";
import "../css/objectives.css";

function Objectives({ onPointsEarned }) {
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentCourseIndex, setCurrentCourseIndex] = useState(0);
  const [courseGroups, setCourseGroups] = useState([]);
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
        const fetchedObjectives = data.objectives || [];
        setObjectives(fetchedObjectives);
        
        // Group objectives by course
        const groupedByCourse = {};
        fetchedObjectives.forEach(obj => {
          if (!groupedByCourse[obj.courseID]) {
            groupedByCourse[obj.courseID] = {
              courseName: obj.courseName || `Course ${obj.courseID}`,
              objectives: []
            };
          }
          groupedByCourse[obj.courseID].objectives.push(obj);
        });
        
        // Convert to array format for easier navigation
        const courseGroupsArray = Object.values(groupedByCourse);
        setCourseGroups(courseGroupsArray);
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
      const updatedObjectives = objectives.map((obj) =>
        obj.subUnitID === subUnitId
          ? { ...obj, completed: true, pointsAwarded: true }
          : obj
      );
      
      setObjectives(updatedObjectives);
      
      // Also update the course groups
      const updatedCourseGroups = [...courseGroups];
      updatedCourseGroups.forEach(course => {
        course.objectives = course.objectives.map(obj => 
          obj.subUnitID === subUnitId
            ? { ...obj, completed: true, pointsAwarded: true }
            : obj
        );
      });
      setCourseGroups(updatedCourseGroups);

      // Notify the parent component about points earned
      if (onPointsEarned) {
        onPointsEarned(data.pointsAwarded || 10);
      }

      return data.pointsAwarded || 0;
    } catch (err) {
      console.error("Error completing objective:", err);
      return 0;
    }
  };

  const navigatePrevious = () => {
    setCurrentCourseIndex(prev => 
      prev === 0 ? courseGroups.length - 1 : prev - 1
    );
  };

  const navigateNext = () => {
    setCurrentCourseIndex(prev => 
      prev === courseGroups.length - 1 ? 0 : prev + 1
    );
  };

  if (loading) return <div className="objectives-loading">Loading objectives...</div>;
  if (error) return <div className="objectives-error">{error}</div>;
  if (courseGroups.length === 0) return <div className="no-objectives">No objectives available</div>;

  const currentCourse = courseGroups[currentCourseIndex];

  return (
    <div className="objectives-container">
      <div className="objectives-header">
        <h3 className="objectives-title">Learning Objectives</h3>
        <div className="course-navigation">
          <span className="course-counter">
            {currentCourseIndex + 1} / {courseGroups.length}
          </span>
        </div>
      </div>

      <div className="course-card">
        <div className="course-name">{currentCourse.courseName}</div>
        
        <ul className="objectives-list">
          {currentCourse.objectives.map((objective) => (
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
        
        <div className="navigation-controls">
          <button 
            className="nav-button prev-button" 
            onClick={navigatePrevious}
            aria-label="Previous course"
          >
            ←
          </button>
          <button 
            className="nav-button next-button" 
            onClick={navigateNext}
            aria-label="Next course"
          >
            →
          </button>
        </div>
      </div>
    </div>
  );
}

export default Objectives;