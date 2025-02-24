import { useEffect, useState } from "react";
import { supabase } from "../supabaseClient"; // Ensure correct path

function Courses() {
  // State to store the data fetched from Supabase
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch data from the RefLesson table
        const { data: fetchedData, error } = await supabase
          .from("RefLesson") // Ensure table name is correct
          .select("lessonName"); // Select only relevant columns

        if (error) throw error; // Handle errors
        setData(fetchedData); // Set state with fetched data
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false); // Set loading to false after fetching
      }
    };

    fetchData(); // Call the function on mount
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Courses</h1>
      {data.length === 0 ? (
        <p>No courses available.</p>
      ) : (
        <ul>
          {data.map((lesson) => (
            <li key={lesson.lessonID}>
              <h2>{lesson.lessonName}</h2>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Courses;
