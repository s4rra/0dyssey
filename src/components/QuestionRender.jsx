import React from 'react';

function QuestionRender({ 
  question, 
  index, 
  userAnswers, 
  handleAnswerChange, 
  handleFillBlankChange,
  submissionResults,
  toggleHint,
  showHints,
  questionStartTimes,
  setQuestionStartTimes,
}) {
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
      
      if (!questionStartTimes[q.questionID]) {
        setQuestionStartTimes(prev => ({
          ...prev,
          [q.questionID]: Math.floor(Date.now() / 1000)
        }));
      }
      
      const updated = [...blanks];
      updated[index] = data;
      handleAnswerChange(q.questionID, updated);
    };

    const handleDragStart = (e, text) => {
      e.dataTransfer.setData("text/plain", text);
    };

    const handleClearBlank = (index) => {
      const updated = [...blanks];
      updated[index] = "";
      handleAnswerChange(q.questionID, updated);
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
        {result.hint && result.retry >= 3 && (
          <div className="hint-container">
            <button onClick={() => toggleHint(questionId)} className="hint-button">
              <span className="hint-symbol"></span>
              {showHints[questionId] ? 'Hide Hint!' : 'Show Hint!'}
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

  switch (question.questionTypeID) {
    case 1: return renderMCQ(question, index);
    case 2: return renderCoding(question, index);
    case 3: return renderFillIn(question, index);
    case 4: return renderDragDrop(question, index);
    default: return null;
  }
}

export default QuestionRender;