import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { DndProvider, useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import "../css/missiondetail.css";

// Draggable item component for drag and drop questions
const DraggableItem = ({ id, text, index }) => {
  const [{ isDragging }, drag] = useDrag({
    type: "ITEM",
    item: { id, text, index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={drag}
      className={`draggable-item ${isDragging ? "dragging" : ""}`}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      {text}
    </div>
  );
};

// Drop target component for drag and drop questions
const DropTarget = ({ id, placedItem, onDrop, label, isOptional }) => {
  const [{ isOver }, drop] = useDrop({
    accept: "ITEM",
    drop: (item) => onDrop(id, item.id),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <div
      ref={drop}
      className={`drop-target ${isOver ? "over" : ""} ${placedItem ? "filled" : ""} ${isOptional ? "optional" : "required"}`}
    >
      <div className="drop-label">
        {label} {isOptional && <span className="optional-indicator">(optional)</span>}
      </div>
      {placedItem && <div className="placed-item">{placedItem}</div>}
    </div>
  );
};

function MissionDetail() {
  const { missionId } = useParams();
  const navigate = useNavigate();
  const [mission, setMission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userAnswers, setUserAnswers] = useState([]);
  const [dragDropState, setDragDropState] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const API_URL = `http://127.0.0.1:8080/api/missions/${missionId}`;
  const SUBMIT_URL = `http://127.0.0.1:8080/api/missions/${missionId}/submit`;
  const API_BASE_URL = "http://127.0.0.1:8080";

  useEffect(() => {
    const fetchMissionDetails = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          navigate("/login");
          return;
        }

        const response = await fetch(API_URL, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch mission details");
        }

        const data = await response.json();
        console.log("Mission data:", data);
        
        // Ensure the mission content has the expected structure
        if (!data.content || !data.content.chapters || !Array.isArray(data.content.chapters)) {
          console.error("Invalid mission data structure:", data);
          setError("Mission data has an invalid structure");
          setLoading(false);
          return;
        }
        
        // Sort chapters if they have an order field
        if (data.content.chapters.length > 0) {
          // Check if chapters have an order property
          const hasOrderProperty = data.content.chapters.some(ch => ch.order !== undefined);
          
          if (hasOrderProperty) {
            // Sort by order property if available
            data.content.chapters.sort((a, b) => (a.order || 0) - (b.order || 0));
          } else {
            // Otherwise, ensure chapters are in sequential order based on their index in the array
            // This assumes the chapters should be in the order they were stored in the database
            // No additional sorting needed in this case
          }
        }
        
        setMission(data);
        
        // Count total questions across all chapters
        let totalQuestions = 0;
        data.content.chapters.forEach(chapter => {
          if (chapter && chapter.questions && Array.isArray(chapter.questions)) {
            totalQuestions += chapter.questions.length;
          }
        });
        
        // Initialize answers array with empty values
        const initialAnswers = Array(totalQuestions).fill(null);
        setUserAnswers(initialAnswers);
        
        // Initialize drag drop state if needed
        const dragDropItems = {};
        let questionIndex = 0;
        data.content.chapters.forEach(chapter => {
          if (chapter && chapter.questions && Array.isArray(chapter.questions)) {
            chapter.questions.forEach((question) => {
              if (question.type === "dragdrop") {
                dragDropItems[questionIndex] = {};
              }
              questionIndex++;
            });
          }
        });
        setDragDropState(dragDropItems);
        
        // If mission is already completed and has user answers, load them
        if (data.completed && data.userAnswers) {
          setUserAnswers(data.userAnswers);
          
          // Restore drag-drop state if available
          if (data.userAnswers.length > 0) {
            const restoredDragDrop = {...dragDropItems};
            
            let questionIndex = 0;
            data.content.chapters.forEach(chapter => {
              if (chapter && chapter.questions && Array.isArray(chapter.questions)) {
                chapter.questions.forEach((question) => {
                  if (question.type === "dragdrop" && data.userAnswers[questionIndex]) {
                    const userAnswer = data.userAnswers[questionIndex];
                    for (const dropId in userAnswer) {
                      const itemId = userAnswer[dropId];
                      // Find the text for this item
                      const itemText = question.options?.find(item => 
                        (typeof item === 'object' ? item.id : item) === itemId
                      ) || itemId;
                      restoredDragDrop[questionIndex][dropId] = typeof itemText === 'object' ? itemText.text : itemText;
                    }
                  }
                  questionIndex++;
                });
              }
            });
            setDragDropState(restoredDragDrop);
          }
          
          setSubmitted(true);
          setResult({
            score: data.score,
            completed: data.completed
          });
        }
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching mission details:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMissionDetails();
  }, [navigate, missionId, API_URL]);

  // Helper function to get image URL with proper path
  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return null;
    
    // Check if the URL is already absolute (starts with http:// or https://)
    if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
      return imageUrl;
    }
    
    // Otherwise, join with API base URL
    return `${API_BASE_URL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;
  };

  // Helper function to get global question index
  const getGlobalQuestionIndex = (chapterIndex, localQuestionIndex) => {
    if (!mission || !mission.content || !mission.content.chapters) {
      return 0;
    }
    
    let globalIndex = 0;
    for (let i = 0; i < chapterIndex; i++) {
      if (mission.content.chapters[i] && mission.content.chapters[i].questions) {
        globalIndex += mission.content.chapters[i].questions.length;
      }
    }
    return globalIndex + localQuestionIndex;
  };

  const handleMCQSelect = (chapterIndex, questionIndex, optionId) => {
    if (submitted) return; // Prevent changes after submission
    
    const globalIndex = getGlobalQuestionIndex(chapterIndex, questionIndex);
    const newAnswers = [...userAnswers];
    newAnswers[globalIndex] = optionId;
    setUserAnswers(newAnswers);
  };

  // Determine if a blank is optional based on its position and available answers
  const isOptionalBlank = (question, blankIndex) => {
    // If this blank's index is greater than or equal to the number of answers provided,
    // we consider it optional
    return !question.answers || blankIndex >= question.answers.length;
  };

  const handleDragDrop = (chapterIndex, questionIndex, dropTargetId, dragItemId) => {
    if (submitted) return; // Prevent changes after submission
    
    const globalIndex = getGlobalQuestionIndex(chapterIndex, questionIndex);
    const question = mission.content.chapters[chapterIndex].questions[questionIndex];
    
    // Update the drag drop visual state
    const newDragDropState = { ...dragDropState };
    if (!newDragDropState[globalIndex]) {
      newDragDropState[globalIndex] = {};
    }
    
    // For dragdrop questions, find the dragged item text
    let draggedItemText = dragItemId;
    if (question.options && Array.isArray(question.options)) {
      // Find the option - can be string or object
      const option = question.options.find(opt => 
        typeof opt === 'object' ? opt.id === dragItemId : opt === dragItemId
      );
      draggedItemText = typeof option === 'object' ? option.text : option || dragItemId;
    }
    
    newDragDropState[globalIndex][dropTargetId] = draggedItemText;
    setDragDropState(newDragDropState);
    
    // Update user answers
    const newAnswers = [...userAnswers];
    if (!newAnswers[globalIndex]) {
      newAnswers[globalIndex] = {};
    }
    newAnswers[globalIndex][dropTargetId] = dragItemId;
    setUserAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      // Check if all required MCQ questions are answered
      // For drag-drop, check if required blanks are answered
      let unansweredMCQ = false;
      let anyQuestionAnswered = false;
      
      let questionIndex = 0;
      if (mission && mission.content && mission.content.chapters) {
        mission.content.chapters.forEach(chapter => {
          if (chapter && chapter.questions && Array.isArray(chapter.questions)) {
            chapter.questions.forEach(question => {
              const answer = userAnswers[questionIndex];
              
              // For MCQ, require an answer
              if (question.type === "mcq" && answer === null) {
                unansweredMCQ = true;
              }
              
              // Check if any question has been answered
              if (answer !== null && 
                  !(typeof answer === 'object' && Object.keys(answer).length === 0)) {
                anyQuestionAnswered = true;
              }
              
              questionIndex++;
            });
          }
        });
      }
      
      if (unansweredMCQ) {
        alert("Please answer all multiple choice questions before submitting.");
        return;
      }
      
      if (!anyQuestionAnswered) {
        alert("Please answer at least one question before submitting.");
        return;
      }

      const response = await fetch(SUBMIT_URL, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ answers: userAnswers })
      });

      if (!response.ok) {
        throw new Error("Failed to submit answers");
      }

      const data = await response.json();
      setResult(data);
      setSubmitted(true);

    } catch (err) {
      console.error("Error submitting answers:", err);
      setError(err.message);
    }
  };

  const handleRetry = () => {
    // Reset state for retry
    let totalQuestions = 0;
    if (mission && mission.content && mission.content.chapters) {
      mission.content.chapters.forEach(chapter => {
        if (chapter && chapter.questions) {
          totalQuestions += chapter.questions.length;
        }
      });
    }
    
    const initialAnswers = Array(totalQuestions).fill(null);
    setUserAnswers(initialAnswers);
    
    const dragDropItems = {};
    let questionIndex = 0;
    if (mission && mission.content && mission.content.chapters) {
      mission.content.chapters.forEach(chapter => {
        if (chapter && chapter.questions) {
          chapter.questions.forEach((question) => {
            if (question.type === "dragdrop") {
              dragDropItems[questionIndex] = {};
            }
            questionIndex++;
          });
        }
      });
    }
    setDragDropState(dragDropItems);
    
    setSubmitted(false);
    setResult(null);
  };

  const handleBack = () => {
    navigate("/missions");
  };

  const nextChapter = () => {
    if (mission && mission.content && mission.content.chapters && 
        currentChapterIndex < mission.content.chapters.length - 1) {
      setCurrentChapterIndex(currentChapterIndex + 1);
      window.scrollTo(0, 0); // Scroll to top when changing chapters
    }
  };

  const prevChapter = () => {
    if (currentChapterIndex > 0) {
      setCurrentChapterIndex(currentChapterIndex - 1);
      window.scrollTo(0, 0); // Scroll to top when changing chapters
    }
  };

  if (loading) return <div className="loading-container">Loading mission...</div>;
  if (error) return <div className="error-container">Error: {error}</div>;
  if (!mission) return <div className="error-container">Mission not found</div>;

  const currentChapter = mission.content.chapters[currentChapterIndex];
  if (!currentChapter) return <div className="error-container">Chapter not found</div>;

  return (
    <div className="mission-detail-container">
      <button className="back-button" onClick={handleBack}>
        &larr; Back to Missions
      </button>
      
      <div className="mission-header">
        <h2>{mission.missionTitle}</h2>
        <div className="mission-meta">
          <span className={`difficulty-badge ${mission.difficulty.toLowerCase()}`}>
            {mission.difficulty}
          </span>
          <span className="xp-reward">
            <span className="xp-icon">⭐</span>
            {mission.xpReward} XP
          </span>
        </div>
      </div>
      
      {/* Display mission image if available */}
      {mission.imageUrl && (
        <div className="mission-image-container">
          <img 
            src={getImageUrl(mission.imageUrl)} 
            alt={mission.missionTitle}
            className="mission-image" 
            onError={(e) => {
              console.error("Error loading image:", e);
              e.target.style.display = "none";
            }}
          />
        </div>
      )}
      
      {/* Chapter Navigation */}
      {mission.content.chapters.length > 1 && (
        <div className="chapter-navigation">
          <button 
            onClick={prevChapter} 
            disabled={currentChapterIndex === 0}
            className="chapter-nav-button"
          >
            Previous Chapter
          </button>
          <span className="chapter-indicator">
            Chapter {currentChapterIndex + 1} of {mission.content.chapters.length}
          </span>
          <button 
            onClick={nextChapter} 
            disabled={currentChapterIndex === mission.content.chapters.length - 1}
            className="chapter-nav-button"
          >
            Next Chapter
          </button>
        </div>
      )}
      
      <div className="mission-scenario">
        <div className="scenario-label">Chapter {currentChapterIndex + 1}: {currentChapter.title}</div>
        <div className="scenario-content">
          <p>{currentChapter.story}</p>
        </div>
      </div>
      
      <div className="mission-questions">
        {currentChapter.questions && Array.isArray(currentChapter.questions) && 
          currentChapter.questions.map((question, qIndex) => {
            const globalQuestionIndex = getGlobalQuestionIndex(currentChapterIndex, qIndex);
            
            return (
              <div key={`${currentChapterIndex}-${qIndex}`} className="question-container">
                <div className="question-number">Question {qIndex + 1}</div>
                <div className="question-text">{question.questionText || question.question}</div>
                
                {question.type === "mcq" && question.options && Array.isArray(question.options) && (
                  <div className="mcq-options">
                    {question.options.map((option, optIndex) => {
                      // Handle option structure - can be string or object
                      const optionId = typeof option === 'object' ? option.id : option;
                      const optionText = typeof option === 'object' ? option.text : option;
                      
                      const isSelected = userAnswers[globalQuestionIndex] === optionId;
                      const isCorrect = submitted && question.answer === optionId;
                      const isIncorrect = submitted && isSelected && !isCorrect;
                      
                      return (
                        <div 
                          key={optIndex}
                          className={`mcq-option ${isSelected ? 'selected' : ''} ${
                            submitted && isCorrect ? 'correct' : ''
                          } ${
                            isIncorrect ? 'incorrect' : ''
                          }`}
                          onClick={() => handleMCQSelect(currentChapterIndex, qIndex, optionId)}
                        >
                          {optionText}
                          {submitted && isCorrect && <span className="correct-indicator">✓</span>}
                          {isIncorrect && <span className="incorrect-indicator">✗</span>}
                        </div>
                      );
                    })}
                  </div>
                )}
                
                {question.type === "dragdrop" && question.options && Array.isArray(question.options) && 
                 question.blanks && Array.isArray(question.blanks) && (
                  <DndProvider backend={HTML5Backend}>
                    <div className="drag-drop-container">
                      <div className="draggable-items">
                        {question.options.map((item, itemIndex) => {
                          // Handle item structure - can be string or object
                          const itemId = typeof item === 'object' ? item.id : item;
                          const itemText = typeof item === 'object' ? item.text : item;
                          
                          return (
                            <DraggableItem
                              key={itemIndex}
                              id={itemId}
                              text={itemText}
                              index={itemIndex}
                            />
                          );
                        })}
                      </div>
                      
                      <div className="drop-targets">
                        {question.blanks.map((blank, blankIndex) => {
                          // Determine if this blank is optional
                          const optional = isOptionalBlank(question, blankIndex);
                          
                          return (
                            <DropTarget
                              key={blankIndex}
                              id={blank}
                              label={blank}
                              isOptional={optional}
                              placedItem={dragDropState[globalQuestionIndex]?.[blank]}
                              onDrop={(dropId, itemId) => handleDragDrop(currentChapterIndex, qIndex, dropId, itemId)}
                            />
                          );
                        })}
                      </div>
                      
                      {submitted && question.answers && Array.isArray(question.answers) && (
                        <div className="correct-answers">
                          <h4>Correct Answer:</h4>
                          <ul>
                            {question.blanks.map((blank, blankIndex) => {
                              if (blankIndex < question.answers.length) {
                                const correctAnswer = question.answers[blankIndex];
                                return (
                                  <li key={blankIndex}>
                                    {blank}: <strong>{correctAnswer}</strong>
                                  </li>
                                );
                              }
                              return null;
                            })}
                          </ul>
                        </div>
                      )}
                    </div>
                  </DndProvider>
                )}
              </div>
            );
          })}
      </div>
      
      {!submitted ? (
        <div className="mission-controls">
          <button className="submit-button" onClick={handleSubmit}>
            Submit Answers
          </button>
        </div>
      ) : (
        <div className="result-container">
          <div className="result-header">
            {result.completed ? "Mission Accomplished!" : "Mission Incomplete"}
          </div>
          <div className="result-score">{result.score}%</div>
          <div className="result-message">
            {result.completed 
              ? "Great job! You've successfully completed this mission." 
              : "Keep trying! You need to score at least 70% to complete this mission."}
          </div>
          
          {result.xpAwarded && (
            <div className="xp-awarded">
              <span className="xp-icon">⭐</span>
              You earned {result.xpAwarded} XP!
            </div>
          )}
          
          <div className="result-actions">
            {!result.completed && (
              <button className="retry-button" onClick={handleRetry}>
                Try Again
              </button>
            )}
            <button className="back-to-missions-button" onClick={handleBack}>
              Back to Missions
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default MissionDetail;