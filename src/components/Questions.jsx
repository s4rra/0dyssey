import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

function Questions({ userId }) {
  const { subunitId } = useParams();

  if (!subunitId) {
    console.error("Subunit ID is undefined");
    return <p>Error: Subunit not found.</p>;
  }
  if (!userId) {
    console.error("User ID is undefined");
    return <p>Error: User not found.</p>;
  }

  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userAnswers, setUserAnswers] = useState({});
  const [score, setScore] = useState(null);

  const API_URL = `http://127.0.0.1:8080/subunits/${subunitId}/questions`;

  useEffect(() => {
    const fetchQuestions = () => {
      axios
        .get(API_URL, { params: { user_id: userId } })
        .then(response => {
          setQuestions(response.data);
          setLoading(false);
        })
        .catch(error => {
          console.error("Error fetching questions:", error);
          setLoading(false);
        });
    };

    fetchQuestions();
  }, [subunitId, userId]);

  const handleGenerateQuestions = () => {
    axios
      .post(`http://127.0.0.1:8080/subunits/${subunitId}/generate-questions`, {
        user_id: userId,
      })
      .then(response => {
        setQuestions(prev => [...prev, ...response.data]);
      })
      .catch(error => {
        console.error("Error generating questions:", error);
      });
  };

  const handleAnswer = (questionId, value) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleCheckAnswers = () => {
    axios
      .post("http://127.0.0.1:8080/check-answers", {
        user_id: userId,
        userAnswers: userAnswers,
      })
      .then(response => {
        setScore(response.data.score);
      })
      .catch(error => {
        console.error("Error checking answers:", error);
      });
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="questions-container">
      <h1 className="questions-title">Questions</h1>
      <div className="question-list">
        {questions.length === 0 && !loading ? (
          <p>No questions available. Try generating some.</p>
        ) : (
          questions.map((question, index) => (
            <div key={question.questionID || `question-${index}`}>
              {[1, 2].includes(question.questionTypeID) && renderMCQAndFillBlanks(question, index)}
              {question.questionTypeID === 3 && renderCoding(question, index)}
              {question.questionTypeID === 4 && renderDropDown(question, index)}
            </div>
          ))
        )}
      </div>

      <button onClick={handleGenerateQuestions}>Generate More Questions</button>
      <button onClick={handleCheckAnswers}>Check Answers</button>

      {score !== null && questions.length > 0 && <p>Your Score: {score} / {questions.length}</p>}
    </div>
  );
}

export default Questions;
