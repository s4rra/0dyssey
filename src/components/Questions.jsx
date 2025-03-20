import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { subunitId } = useParams();
  const API_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/questions`;

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in");
      navigate("/login");
      return;
    }

    fetch(API_URL, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setQuestions(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching questions:", err);
        setError(err.message);
        setLoading(false);
      });
  }, [subunitId]);

  if (loading) return <p>Loading questions...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>Questions</h2>
      {questions.length === 0 ? (
        <p>No questions available.</p>
      ) : (
        <ul>
          {questions.map((question) => {
            
            let options = {};
            try {
              options = JSON.parse(question.options);
            } catch (e) {
              console.error("Error parsing options:", e);
            }

            return (
              <li key={question.questionID}>
                <h3>{question.questionText}</h3>
                {question.questionTypeID === 1 && options ? (
                  <form>
                    {Object.entries(options).map(([key, value]) => (
                      <label key={key} style={{ display: "block" }}>
                        <input type="radio" name={`q${question.questionID}`} value={key} />
                        {value}
                      </label>
                    ))}
                  </form>
                ) : (
                  <p>Unsupported question type</p>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default Questions;
