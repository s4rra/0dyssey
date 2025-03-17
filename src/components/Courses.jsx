import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom"; // Import Link for navigation

function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_URL = "http://127.0.0.1:8080/courses";

  useEffect(() => {
    axios.get(API_URL)
      .then(response => {
        console.log("Fetched courses:", response.data);
        setCourses(response.data);
        setLoading(false);
      })
      .catch(error => {
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
                    <Link to={`/subunit/${subUnit.subUnitID}`}>
                      {subUnit.subUnitName}
                    </Link>
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