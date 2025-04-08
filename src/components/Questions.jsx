import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../css/questions.css";

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [submissionResults, setSubmissionResults] = useState({});
  const [showHints, setShowHints] = useState({});
  const [loading, setLoading] = useState(true);
  const [startTimes, setStartTimes] = useState({});

  const { subunitId } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const API_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/questions`;
  const SUBMIT_URL = `http://127.0.0.1:8080/api/submit-answers`;
  const SUBMIT_SINGLE_URL = `http://127.0.0.1:8080/api/submit-answer`;
  const GENERATE_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/generate-questions`;

  useEffect(() => {
    if (!token) {
      alert("log in first");
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
      
      //setting start times for each question
      const newStartTimes = {};
      data.forEach(q => {
        newStartTimes[q.questionID] = Math.floor(Date.now() / 1000);
      });
      setStartTimes(newStartTimes);
      
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
    try {
      await fetch(GENERATE_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      fetchQuestions();
    } catch (err) {
      alert("Error generating new questions");
    }
  };

  const submitSingleAnswer = async (questionId) => {
    try {
      const question = questions.find(q => q.questionID === questionId);
      if (!question) return;

      const answerData = {
        questionId: question.questionID,
        questionTypeId: question.questionTypeID,
        userAnswer: userAnswers[question.questionID] || '',
        correctAnswer: question.correctAnswer,
        constraints: question.constraints || '',
        startTime: startTimes[question.questionID]
      };

      const res = await fetch(SUBMIT_SINGLE_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(answerData)
      });

      const result = await res.json();
      
      if (result.success) {
        setSubmissionResults(prev => ({
          ...prev,
          [questionId]: result.data
        }));
      } else {
        alert(`Error: ${result.error || "Failed to submit answer"}`);
      }
    } catch (err) {
      alert("Error submitting answer");
    }
  };

  const submitAnswers = async () => {
    try {
      const answersData = questions.map(q => ({
        questionId: q.questionID,
        questionTypeId: q.questionTypeID,
        userAnswer: userAnswers[q.questionID] || '',
        correctAnswer: q.correctAnswer,
        constraints: q.constraints || '',
        startTime: startTimes[q.questionID]
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
      if (!result.results) {
        alert("Invalid response from server");
        return;
      }
      
      const resultsMap = result.results.reduce((acc, r) => {
        if (r.success) {
          acc[r.questionId] = {
            isCorrect: r.isCorrect,
            feedback: r.feedback,
            hint: r.hint,
            points: r.points
          };
        } else {
          alert(`Error with question ${r.questionId}: ${r.error}`);
        }
        return acc;
      }, {});
      
      setSubmissionResults(resultsMap);
    } catch (err) {
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
      {!submissionResults[q.questionID] && userAnswers[q.questionID] && (
        <button 
          onClick={() => submitSingleAnswer(q.questionID)} 
          className="submit-single-button">
          Submit Answer
        </button>
      )}
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
        {!submissionResults[q.questionID] && answers.length > 0 && answers.every(a => a) && (
          <button 
            onClick={() => submitSingleAnswer(q.questionID)} 
            className="submit-single-button">
            Submit Answer
          </button>
        )}
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
        {!submissionResults[q.questionID] && blanks.every(b => b) && (
          <button 
            onClick={() => submitSingleAnswer(q.questionID)} 
            className="submit-single-button">
            Submit Answer
          </button>
        )}
      </div>
    );
  };

  const renderCoding = (q, i) => (
    <div key={q.questionID} className="question-container">
      <p className="question-text">{i + 1}. {q.questionText}</p>
      <textarea
        className="coding-textarea"
        rows={6}
        value={userAnswers[q.questionID] || ""}
        onChange={e => handleAnswerChange(q.questionID, e.target.value)}
        disabled={!!submissionResults[q.questionID]}
      />
      {renderFeedback(q.questionID)}
      {!submissionResults[q.questionID] && userAnswers[q.questionID] && (
        <button 
          onClick={() => submitSingleAnswer(q.questionID)} 
          className="submit-single-button">
          Submit Answer
        </button>
      )}
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
          {result.points > 0 && <span className="points-earned"> +{result.points} points</span>}
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
        <button onClick={submitAnswers} 
          disabled={Object.keys(userAnswers).length === 0 || Object.keys(userAnswers).length === Object.keys(submissionResults).length} 
          className="submit-button">
          Submit All
        </button>
        <button onClick={generateMoreQuestions} className="generate-button">
          More Questions?
        </button>
      </div>
    </div>
  );
}

export default Questions;