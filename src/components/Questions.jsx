import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const Questions = () => {
  const { subunitId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userAnswers, setUserAnswers] = useState({});
  const [score, setScore] = useState(null);

  const API_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/questions`;

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
        setQuestions(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching questions:", error);
        setLoading(false);
      });
  }, [subunitId]);

  const handleGenerateQuestions = () => {
    const token = localStorage.getItem("token");

    fetch(`http://127.0.0.1:8080/api/subunits/${subunitId}/generate-questions`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      }
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          setQuestions(data.questions);
        }
      })
      .catch((error) => {
        console.error("Error generating questions:", error);
      });
  };

  const handleAnswer = (questionId, value) => {
    setUserAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleCheckAnswers = () => {
    const token = localStorage.getItem("token");

    fetch("http://127.0.0.1:8080/api/check-answers", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ userAnswers }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          setScore(data.score);
        }
      })
      .catch((error) => {
        console.error("Error checking answers:", error);
      });
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="questions-container">
      <h1>Questions</h1>
      <div className="question-list">
        {questions.length === 0 ? (
          <p>No questions available. Try generating some.</p>
        ) : (
          questions.map((question) => (
            <div key={question.questionID}>
              <p>{question.questionText}</p>
              {question.options && Object.keys(question.options).map((optionKey) => (
                <label key={optionKey} style={{ display: "block", margin: "5px 0" }}>
                  <input
                    type="radio"
                    name={`question-${question.questionID}`}
                    value={optionKey}
                    onChange={() => handleAnswer(question.questionID, optionKey)}
                  />
                  {question.options[optionKey]}
                </label>
              ))}
            </div>
          ))
        )}
      </div>

      <button onClick={handleGenerateQuestions}>Generate More Questions</button>
      <button onClick={handleCheckAnswers}>Check Answers</button>

      {score !== null && questions.length > 0 && (
        <p>Your Score: {score} / {questions.length}</p>
      )}
    </div>
  );
};

export default Questions;
