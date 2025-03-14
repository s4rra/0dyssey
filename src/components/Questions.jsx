import { useEffect, useState } from "react";
import { useParams } from "react-router-dom"; // Import useParams
import axios from "axios";

function Questions({ userId }) {
  const { subunitId } = useParams(); // Extract subunitId from the URL

  if (!subunitId) {
    console.error("Subunit ID is undefined");
    return <p>Error: Subunit not found.</p>;
  }

  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userAnswers, setUserAnswers] = useState({});
  const API_URL = `http://127.0.0.1:8080/subunits/${subunitId}/questions`;

  useEffect(() => {
    axios.get(API_URL)
      .then(response => {
        setQuestions(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching questions:", error);
        setLoading(false);
      });
  }, [subunitId]); // Re-run effect when subunitId changes

  const handleGenerateQuestions = () => {
    axios.post(`http://127.0.0.1:8080/subunits/${subunitId}/generate-questions`, { user_id: userId })
    .then(response => {
      if (Array.isArray(response.data)) { //  array?
        setQuestions([...questions, ...response.data]); //Append only the new questions
      } else {
        console.error("Invalid response format:", response.data);
      }
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
        {questions.map((question, index) => (
          <li key={index}>
            <p>{question.questionText}</p>
          </li>
        ))}
      </ul>
      <button onClick={handleGenerateQuestions}>Generate More Questions</button>
    </div>
  );
}

export default Questions;