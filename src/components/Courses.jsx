import { useEffect, useState } from "react";
import axios from "axios";

function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_URL = "http://127.0.0.1:5000/courses"; 
  useEffect(() => {
    axios.get(API_URL)
      .then(response => {
        setCourses(response.data);
        setLoading(false);
      })
      .catch(error => console.error("Error fetching courses:", error));
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>Courses</h1>
      <ol>
        {courses.map(course => (
          <li key={course.unitID}>{course.unitName}</li>
        ))}
      </ol>
    </div>
  );
}

export default Courses;
