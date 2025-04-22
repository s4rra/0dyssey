import { useEffect, useState } from "react";
import { useNavigate, Outlet, useParams, useLocation } from "react-router-dom";
import "../css/courses.css";

function Courses() {
  const [courses, setCourses] = useState([]);
  const [userProgress, setUserProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const { subUnitId } = useParams(); // Detect if a subunit is selected
  const API_URL = "http://127.0.0.1:8080/api/courses";
  const PROGRESS_URL = "http://127.0.0.1:8080/api/user-progress";

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    const fetchData = async () => {
      try {
        // Fetch courses data
        const coursesRes = await fetch(API_URL, { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const coursesData = await coursesRes.json();
        
        // Fetch user progress data
        const progressRes = await fetch(PROGRESS_URL, { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const progressData = await progressRes.json();
        
        setCourses(coursesData);
        setUserProgress(progressData.completed_subunits || []);
        
        // Log for debugging
        console.log("Fetched courses:", coursesData);
        console.log("Fetched user progress:", progressData.completed_subunits);
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate, location.pathname]); // Added location.pathname as dependency to refresh on navigation

  // Debug logging for progress data
  useEffect(() => {
    console.log("Current user progress:", userProgress);
  }, [userProgress]);

  // Check if a subunit is accessible
  const canAccessSubunit = (unitId, subunitId, allSubunits) => {
    // Get all units sorted by ID
    const allUnitIds = [...new Set(allSubunits.map(su => su.unitID))].sort();
    
    // Get this unit's index
    const unitIndex = allUnitIds.indexOf(unitId);
    
    // Get subunits for this unit sorted by ID
    const unitSubunits = allSubunits
      .filter(su => su.unitID === unitId)
      .sort((a, b) => a.subUnitID - b.subUnitID);
    
    // Find the index of the current subunit
    const subunitIndex = unitSubunits.findIndex(su => su.subUnitID === subunitId);
    
    // First subunit of first unit is always accessible
    if (unitIndex === 0 && subunitIndex === 0) {
      return true;
    }
    
    // First subunit of other units - check last subunit of previous unit
    if (subunitIndex === 0) {
      // Check if last subunit of previous unit is completed
      const prevUnitId = allUnitIds[unitIndex - 1];
      const prevUnitSubunits = allSubunits
        .filter(su => su.unitID === prevUnitId)
        .sort((a, b) => a.subUnitID - b.subUnitID);
      
      if (prevUnitSubunits.length > 0) {
        const lastPrevSubunitId = prevUnitSubunits[prevUnitSubunits.length - 1].subUnitID;
        return userProgress.some(p => p.subUnitID === lastPrevSubunitId);
      }
      return false;
    }
    
    // Check if previous subunit is completed
    const previousSubunitId = unitSubunits[subunitIndex - 1].subUnitID;
    return userProgress.some(p => p.subUnitID === previousSubunitId);
  };

  const handleSubunitClick = (unitId, subunitId, allSubunits) => {
    if (canAccessSubunit(unitId, subunitId, allSubunits)) {
      navigate(`/courses/subunit/${unitId}/${subunitId}`);
    } else {
      alert("Complete previous subunits first to unlock this one!");
    }
  };

  // Helper function to get all subunits across all courses
  const getAllSubunits = () => {
    const allSubunits = [];
    courses.forEach(course => {
      if (course.RefSubUnit && course.RefSubUnit.length > 0) {
        course.RefSubUnit.forEach(subUnit => {
          allSubunits.push({...subUnit, unitID: course.unitID});
        });
      }
    });
    return allSubunits;
  };

  const isSubunitCompleted = (subunitId) => {
    return userProgress.some(p => p.subUnitID === subunitId);
  };

  if (loading) return <p>Loading...</p>;

  const allSubunits = getAllSubunits();

  return (
    <div className="courses-container">
      <Outlet />
      {location.pathname === "/courses" && (
        <>
          <h2 className="courses-title">Lessons</h2>
          <div className="courses-grid">
            {courses.map((course) => (
              <div key={course.unitID} className="course-card">
                <span className="course-category">Skill Path</span>
                <h3 className="course-title">{course.unitName}</h3>
                <p className="course-description">{course.unitDescription}</p>

                {course.RefSubUnit?.length > 0 && (
                  <div className="subunits-container">
                    {course.RefSubUnit
                      .sort((a, b) => a.subUnitID - b.subUnitID)
                      .map((subUnit) => {
                        const isCompleted = isSubunitCompleted(subUnit.subUnitID);
                        const isAccessible = canAccessSubunit(
                          course.unitID, 
                          subUnit.subUnitID, 
                          allSubunits
                        );
                        
                        // Debug logging for each subunit
                        console.log(`Subunit ${subUnit.subUnitID} - Completed: ${isCompleted}, Accessible: ${isAccessible}`);
                        
                        return (
                          <button
                            key={subUnit.subUnitID}
                            onClick={() => handleSubunitClick(
                              course.unitID, 
                              subUnit.subUnitID, 
                              allSubunits
                            )}
                            className={`subunit-button ${isCompleted ? 'completed' : ''} ${!isAccessible ? 'locked' : ''}`}
                            disabled={!isAccessible}
                          >
                            {subUnit.subUnitName}
                            {!isAccessible && <span className="lock-icon">🔒</span>}
                            {isCompleted && <span className="check-icon">✓</span>}
                          </button>
                        );
                      })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default Courses;