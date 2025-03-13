import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8080/courses";

  useEffect(() => {
    axios.get(API_URL)
      .then(response => {
        console.log("Fetched courses:", response.data);
        setCourses(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching courses:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>Courses</h2>
      <ul>
        {courses.map(course => (
          <li key={course.unitID}>
            <h1>{course.unitName}</h1>
            {course.RefSubUnit && course.RefSubUnit.length > 0 ? (
              <ul>
                {course.RefSubUnit.map(subUnit => (
                  <li key={subUnit.subUnitID}>
                    <button 
                      onClick={() => navigate(`/subunit/${subUnit.subUnitID}/questions`)} // Pass subunitId correctly
                      style={{ 
                        background: "none", 
                        border: "none", 
                        color: "blue", 
                        textDecoration: "underline", 
                        cursor: "pointer" 
                      }}
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