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
  const [hintLoading, setHintLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const { unitId, subunitId } = useParams(); //get from url
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const API_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/questions`;
  const SUBMIT_URL = `http://127.0.0.1:8080/api/submit-answers`;
  const GENERATE_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/generate-questions`;
  const HINT_USED_URL = `http://127.0.0.1:8080/api/hint-used`;
  const PERFORMANCE_URL = `http://127.0.0.1:8080/api/performance/submit/${unitId}/${subunitId}`;

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
      const result = await res.json();
  
      const data = result.questions || [];
      setQuestions(data);
  
      if (data.length === 0 && result.message) {
        setNotification(result.message);
      } else {
        const startTimes = {};
        data.forEach(q => {
          startTimes[q.questionID] = Math.floor(Date.now() / 1000);
        });
        setQuestionStartTimes(startTimes);
      }
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

  const toggleHint = async (questionId) => {
    if (showHints[questionId]) {
      setShowHints(prev => ({ ...prev, [questionId]: false }));
      return;
    }
    setHintLoading(true);
    try {
      const res = await fetch(HINT_USED_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      const result = await res.json();
    
      if (result.success) {
        setShowHints(prev => ({ ...prev, [questionId]: true }));
        showNotification(`-30 points for using hint. remaining: ${result.updatedPoints} points`);
      } else {
        showNotification(result.message || "Cannot use hint at this time");
      }
    } catch (error) {
      console.error("Error using hint:", error);
      alert("Error processing hint request");
    } finally {
      setHintLoading(false);
    }
  }

  const showNotification = (message) => {
      setNotification(message);
      setTimeout(() => setNotification(null), 3000);
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
    setLoading(true);
    const currentTime = Math.floor(Date.now() / 1000);
    try {
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
  
       submitPerformance(result.results);
      } else {
        alert("Error submitting answers");
      }
    } catch (err) {
      alert("Submission failed");
      console.error("submitAnswers failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const submitPerformance = async (answerResults) => {
    try {
      const res = await fetch(PERFORMANCE_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(answerResults)
      });
  
      const perfResult = await res.json();
  
      if (!perfResult.success) {
        console.warn("Performance submission failed. Full response:", perfResult);
      }
    } catch (err) {
      console.error("submitPerformance failed with exception:", err);
    }
  };
  
    
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
            hintLoading={hintLoading}
            questionStartTimes={questionStartTimes}
            setQuestionStartTimes={setQuestionStartTimes}
          />
        ))}
      </div>
      {Object.keys(submissionResults).length > 0 && (
        <div className="points-notification">+{totalPoints} points!</div>
      )}
      <div className="action-buttons">
        <button
            onClick={submitAnswers}
            className="submit-button"
          >
            {Object.keys(submissionResults).length === 0 ? 'Submit' : 'Resubmit'}
        </button>
        <button onClick={generateMoreQuestions} className="generate-button">
          More Questions?
        </button>
        <button
          className="generate-button"
          onClick={() => navigate("/courses")}
        >
          Next
        </button>
        {loading && <div className="loading">Loading...</div>}
        {notification && (
            <div className="points-notification">
              {notification}
            </div>
          )}
      </div>
    </div>
  );
}

export default Questions;