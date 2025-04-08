import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../css/questions.css";

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [questionStartTimes, setQuestionStartTimes] = useState({});
  const [submissionResults, setSubmissionResults] = useState({});
  const [showHints, setShowHints] = useState({});
  const [loading, setLoading] = useState(true);

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
      
      // Initialize start times for all questions
      const startTimes = {};
      data.forEach(q => {
        startTimes[q.questionID] = Math.floor(Date.now() / 1000); // Current Unix timestamp in seconds
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
      startTime: questionStartTimes[q.questionID] || currentTime - 60, // Fallback if missing
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
    } else {
      alert("Error submitting answers");
    }
  };

  const renderMCQ = (q, i) => (
    <div key={q.questionID} className="question-container">
      <p className="question-text">{i + 1}. {q.questionText}</p>
      <div className="options-container">
        {q.options && Object.entries(q.options).map(([key, value]) => (
          <label key={key} className="option-label">
            <input
              type="radio"
              name={q.questionID}
              value={key}
              checked={userAnswers[q.questionID] === key}
              onChange={() => handleAnswerChange(q.questionID, key)}
              disabled={!!submissionResults[q.questionID]}
            />
            <span>{value}</span>
          </label>
        ))}
      </div>
      {renderFeedback(q.questionID)}
    </div>
  );

  const renderFillIn = (q, i) => {
    const parts = q.questionText.split("_____");
    const blanksCount = parts.length - 1;
    const answers = userAnswers[q.questionID] || [];

    return (
      <div key={q.questionID} className="question-container">
        <p className="question-text">
          {i + 1}. {parts.map((part, index) => (
            <span key={index}>
              {part}
              {index < blanksCount && (
                <input
                  type="text"
                  className="fill-blank-input"
                  value={answers[index] || ""}
                  onChange={e => handleFillBlankChange(q.questionID, index, e.target.value)}
                  disabled={!!submissionResults[q.questionID]}
                />
              )}
            </span>
          ))}
        </p>
        {renderFeedback(q.questionID)}
      </div>
    );
  };

  const renderDragDrop = (q, i) => {
    const blankCount = (q.questionText.match(/_____/g) || []).length;
    const blanks = userAnswers[q.questionID] || Array(blankCount).fill("");
    const parts = q.questionText.split("_____");

    const handleDrop = (e, index) => {
      e.preventDefault();
      const data = e.dataTransfer.getData("text/plain");
      
      // Initialize start time if not already set
      if (!questionStartTimes[q.questionID]) {
        setQuestionStartTimes(prev => ({
          ...prev,
          [q.questionID]: Math.floor(Date.now() / 1000)
        }));
      }
      
      const updated = [...blanks];
      updated[index] = data;
      setUserAnswers(prev => ({ ...prev, [q.questionID]: updated }));
    };

    const handleDragStart = (e, text) => {
      e.dataTransfer.setData("text/plain", text);
    };

    const handleClearBlank = (index) => {
      const updated = [...blanks];
      updated[index] = "";
      setUserAnswers(prev => ({ ...prev, [q.questionID]: updated }));
    };

    return (
      <div key={q.questionID} className="question-container">
        <p className="question-text">
          <strong>{i + 1}.</strong>{" "}
          {parts.map((part, index) => (
            <span key={index}>
              {part}
              {index < blankCount && (
                <span
                  onDrop={e => handleDrop(e, index)}
                  onDragOver={e => e.preventDefault()}
                  className="drag-drop-blank"
                >
                  {blanks[index]}
                  {blanks[index] && (
                    <button
                      onClick={() => handleClearBlank(index)}
                      className="clear-blank-btn"
                    >
                    </button>
                  )}
                </span>
              )}
            </span>
          ))}
        </p>

        <div className="drag-options-container">
          {q.options.map((option, index) => (
            <div
              key={index}
              draggable
              onDragStart={e => handleDragStart(e, option)}
              className="drag-option"
            >
              {option}
            </div>
          ))}
        </div>
        {renderFeedback(q.questionID)}
      </div>
    );
  };

  const renderCoding = (q, i) => (
    <div key={q.questionID} className="question-container">
      <p className="question-text">{i + 1}. {q.questionText}</p>
      <textarea
        className="coding-textarea"
        rows={4}
        value={userAnswers[q.questionID] || ""}
        onChange={e => handleAnswerChange(q.questionID, e.target.value)}
        disabled={!!submissionResults[q.questionID]}
      />
      {renderFeedback(q.questionID)}
    </div>
  );

  const renderFeedback = (questionId) => {
    const result = submissionResults[questionId];
    if (!result) return null;
  
    return (
      <div className="feedback-container">
        <div className={`feedback-result ${result.isCorrect ? 'correct' : 'incorrect'}`}>
          <span className="feedback-symbol">
            {result.isCorrect ? '✓' : '✗'}
          </span>
          {result.isCorrect ? "Correct!" : "Incorrect"}
        </div>
        {result.feedback && (
          <div className="feedback-text">
            <strong>Feedback:</strong> {result.feedback}
          </div>
        )}
        {result.hint && (
          <div className="hint-container">
            <button onClick={() => toggleHint(questionId)} className="hint-button">
              <span className="hint-symbol">?</span>
              {showHints[questionId] ? 'Hide Hint' : 'Show Hint'}
            </button>
            {showHints[questionId] && (
              <div className="hint-text">
                <strong>Hint:</strong> {result.hint}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="questions-container">
      <h2 className="questions-title">Questions</h2>
      <div className="questions-list">
        {questions.map((q, i) => {
          switch (q.questionTypeID) {
            case 1: return renderMCQ(q, i);
            case 2: return renderCoding(q, i);
            case 3: return renderFillIn(q, i);
            case 4: return renderDragDrop(q, i);
            default: return null;
          }
        })}
      </div>
      <div className="action-buttons">
        {Object.keys(submissionResults).length === 0 && (
          <button
            onClick={submitAnswers}
            disabled={Object.keys(userAnswers).length !== questions.length}
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