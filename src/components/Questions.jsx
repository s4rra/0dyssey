
import { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

function Questions() {
  const { subunit_id } = useParams();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_URL = `http://127.0.0.1:8080/questions/${subunit_id}`;  // Define API_URL

  useEffect(() => {
    axios.get(API_URL)
      .then(response => {
        console.log("Fetched questions:", response.data);
        setQuestions(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching questions:", error);
        setLoading(false);
      });
  }, [API_URL, subunit_id]);  // Add API_URL and subunit_id to the dependency array

  const handleGenerateQuestions = () => {
    axios.post("http://127.0.0.1:8080/generate-questions", {
      subunit_id: subunit_id,
      skill_level: "beginner"  // Adjust based on user selection
    })
      .then(response => {
        console.log("Generated questions:", response.data);
        setQuestions([...questions, ...response.data]);
      })
      .catch((error) => {
        console.error("Error generating questions:", error);
      });
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>Questions</h2>
      <ul>
        {questions.map(question => (
          <li key={question.questionID}>
            <p>{question.questionText}</p>
          </li>
        ))}
      </ul>
      <button onClick={handleGenerateQuestions}>Generate More Questions</button>
    </div>
  );
}

export default Questions;
