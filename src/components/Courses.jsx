import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8080/api/courses";

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    fetch(API_URL, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching courses:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>Courses</h2>
      <ul>
        {courses.map((course) => (
          <li key={course.unitID}>
            <h3>{course.unitName}</h3>
            {course.RefSubUnit && course.RefSubUnit.length > 0 ? (
              <ul>
                {course.RefSubUnit.map((subUnit) => (
                  <li key={subUnit.subUnitID}>
                    <button
                      onClick={() => navigate(`/subunit/${subUnit.subUnitID}/questions`)}
                      style={{ background: "none", border: "none", color: "blue", textDecoration: "underline", cursor: "pointer" }}
                    >
                      {subUnit.subUnitName}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No subunits available</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Courses;
