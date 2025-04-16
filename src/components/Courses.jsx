import { useEffect, useState } from "react";
import { useNavigate, Outlet, useParams } from "react-router-dom";
import "../css/courses.css";

function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { subUnitId } = useParams(); // Detect if a subunit is selected
  const API_URL = "http://127.0.0.1:8080/api/courses";

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    fetch(API_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching courses:", err);
        setLoading(false);
      });
  }, [navigate]);

  if (loading) return <p>Loading...</p>;

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
                    {course.RefSubUnit.map((subUnit) => (
                      <button
                        key={subUnit.subUnitID}
                        onClick={() =>
                          navigate(
                            `/courses/subunit/${course.unitID}/${subUnit.subUnitID}`
                          )
                        }
                        className="subunit-button"
                      >
                        {subUnit.subUnitName}
                      </button>
                    ))}
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
