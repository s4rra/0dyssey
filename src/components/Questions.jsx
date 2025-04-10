import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import QuestionRender from "./QuestionRender";
import "../css/questions.css";

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [questionStartTimes, setQuestionStartTimes] = useState({});
  const [submissionResults, setSubmissionResults] = useState({});
  const [showHints, setShowHints] = useState({});
  const [loading, setLoading] = useState(true);
  const [totalPoints, setTotalPoints] = useState(0);

  const { subunitId } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const API_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/questions`;
  const SUBMIT_URL = `http://127.0.0.1:8080/api/submit-answers`;
  const GENERATE_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/generate-questions`;

  useEffect(() => {
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }
    fetchQuestions();
  }, [subunitId, token, navigate]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setQuestions(data);
      
      const startTimes = {};
      data.forEach(q => {
        startTimes[q.questionID] = Math.floor(Date.now() / 1000);
      });
      setQuestionStartTimes(startTimes);
    } catch (err) {
      alert("Error fetching questions");
    } finally {
      setLoading(false);
      setUserAnswers({});
      setSubmissionResults({});
      setShowHints({});
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleFillBlankChange = (questionId, index, value) => {
    const current = userAnswers[questionId] || [];
    current[index] = value;
    setUserAnswers(prev => ({ ...prev, [questionId]: current }));
  };

  const toggleHint = (questionId) => {
    setShowHints(prev => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const generateMoreQuestions = async () => {
    await fetch(GENERATE_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    fetchQuestions();
  };

  const submitAnswers = async () => {
    const currentTime = Math.floor(Date.now() / 1000);
    
    const answersData = questions.map(q => ({
      questionId: q.questionID,
      questionTypeId: q.questionTypeID,
      userAnswer: userAnswers[q.questionID] || '',
      startTime: questionStartTimes[q.questionID] || currentTime - 60,
      endTime: currentTime
    }));

    const res = await fetch(SUBMIT_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(answersData)
    });

    const result = await res.json();
    if (result.results) {
      const resultsMap = result.results.reduce((acc, r) => {
        acc[r.questionId] = r;
        return acc;
      }, {});
      setSubmissionResults(resultsMap);
      const totalPoints = result.results.reduce((sum, r) => sum + (r.points || 0), 0);
      setTotalPoints(totalPoints);
    } else {
      alert("Error submitting answers");
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="questions-container">
      <h2 className="questions-title">Questions</h2>
      <div className="questions-list">
        {questions.map((question, index) => (
          <QuestionRender
            key={question.questionID}
            question={question}
            index={index}
            userAnswers={userAnswers}
            handleAnswerChange={handleAnswerChange}
            handleFillBlankChange={handleFillBlankChange}
            submissionResults={submissionResults}
            toggleHint={toggleHint}
            showHints={showHints}
            questionStartTimes={questionStartTimes}
            setQuestionStartTimes={setQuestionStartTimes}
          />
        ))}
      </div>
      {Object.keys(submissionResults).length > 0 && (
        <div className="points-banner">+{totalPoints} points!</div>
      )}
      <div className="action-buttons">
        {Object.keys(submissionResults).length === 0 && (
          <button
            onClick={submitAnswers}
            className="submit-button"
          >
            Submit
          </button>
        )}
        <button onClick={generateMoreQuestions} className="generate-button">
          More Questions?
        </button>
      </div>
    </div>
  );
}

export default Questions;