import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function Questions() {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [userAnswers, setUserAnswers] = useState({});
    const [submissionResults, setSubmissionResults] = useState({});
    const [showHints, setShowHints] = useState({});
    const navigate = useNavigate();
    const { subunitId } = useParams();
    const API_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/questions`;
    const SUBMIT_URL = "http://127.0.0.1:8080/api/submit-answers";
    const GENERATE_URL = `http://127.0.0.1:8080/api/subunits/${subunitId}/generate-questions`;

    const fetchQuestions = async () => {
        const token = localStorage.getItem("token");
        try {
            const response = await fetch(API_URL, {
                headers: { 
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch questions');
            }

            const data = await response.json();
            setQuestions(data);
            setLoading(false);
            // Reset states
            setUserAnswers({});
            setSubmissionResults({});
            setShowHints({});
        } catch (error) {
            console.error("Error fetching questions:", error);
            alert(error.message);
            setLoading(false);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please log in first.");
            navigate("/login");
            return;
        }

        fetchQuestions();
    }, [subunitId, navigate]);

    const handleAnswer = (questionId, value) => {
        setUserAnswers(prev => ({...prev, [questionId]: value}));
    };

    const toggleHint = (questionId) => {
        setShowHints(prev => ({...prev, [questionId]: !prev[questionId]}));
    };

    const generateMoreQuestions = async () => {
        const token = localStorage.getItem("token");
        setLoading(true);
        
        try {
            const response = await fetch(GENERATE_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to generate questions');
            }

            fetchQuestions();
        } catch (error) {
            console.error("Error generating questions:", error);
            alert(error.message);
            setLoading(false);
        }
    };

    const submitAnswers = async () => {
        const token = localStorage.getItem("token");
        
        // Prepare answers data
        const answersData = questions.map(question => ({
            questionId: question.questionID,
            questionTypeId: question.questionTypeID,
            userAnswer: userAnswers[question.questionID] || '',
            correctAnswer: question.correctAnswer,
            constraints: question.constraints || ''
        }));

        try {
            const response = await fetch(SUBMIT_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(answersData)
            });

            if (!response.ok) {
                throw new Error('Failed to submit answers');
            }

            const results = await response.json();
            setSubmissionResults(
                results.results.reduce((acc, result) => {
                    acc[result.questionId] = result;
                    return acc;
                }, {})
            );
        } catch (error) {
            console.error("Error submitting answers:", error);
            alert(error.message);
        }
    };

    const renderFillInAndMCQ = (question, questionNumber) => {
        const result = submissionResults[question.questionID];
        return (
            <div className="question-box" key={question.questionID}>
                <p className="question-text">
                    <strong>{questionNumber}. </strong>
                    {question.questionText}
                </p>
                <div className="options-container">
                    {question.options && Object.entries(question.options).map(([key, value]) => (
                        <label key={key} className="option-label">
                            <input
                                type="radio"
                                name={`question_${question.questionID}`}
                                value={key}
                                checked={userAnswers[question.questionID] === key}
                                onChange={() => handleAnswer(question.questionID, key)}
                                disabled={!!submissionResults[question.questionID]}
                            />
                            {value}
                        </label>
                    ))}
                </div>
                {result && (
                    <div className={`result ${result.isCorrect ? 'correct' : 'incorrect'}`}>
                        {result.isCorrect ? 'Correct!' : 'Incorrect'}
                    </div>
                )}
            </div>
        );
    };

    const renderCoding = (question, questionNumber) => {
        const result = submissionResults[question.questionID];
        return (
            <div className="question-box" key={question.questionID}>
                <p className="question-text">
                    <strong>{questionNumber}. </strong>
                    {question.questionText}
                </p>
                <textarea
                    className="coding-textarea"
                    value={userAnswers[question.questionID] || ''}
                    onChange={(e) => handleAnswer(question.questionID, e.target.value)}
                    placeholder="Write your code..."
                    disabled={!!submissionResults[question.questionID]}
                />
                {question.constraints && (
                    <p className="constraints">
                        <strong>Constraints:</strong> {question.constraints}
                    </p>
                )}
                {result && (
                    <div className="coding-result">
                        {result.hint && (
                            <div>
                                <button 
                                    className="hint-button"
                                    onClick={() => toggleHint(question.questionID)}
                                >
                                    {showHints[question.questionID] ? 'Hide Hint' : 'Show Hint'}
                                </button>
                                {showHints[question.questionID] && (
                                    <div className="hint">
                                        <strong>Hint:</strong> {result.hint}
                                    </div>
                                )}
                            </div>
                        )}
                        {result.feedback && (
                            <div className="feedback">
                                <strong>Feedback:</strong> {result.feedback}
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    };

    if (loading) return <p className="loading-text">Loading...</p>;

    return (
        <div className="questions-container">
            <h1 className="questions-title">Questions</h1>
            
            <div className="question-list">
                {questions.map((question, index) => (
                    question.questionTypeID === 1 ? 
                        renderFillInAndMCQ(question, index + 1) : 
                    question.questionTypeID === 2 ? 
                        renderCoding(question, index + 1) : 
                        null
                ))}
            </div>

            <div className="action-buttons">
                {Object.keys(submissionResults).length === 0 && (
                    <button 
                        className="submit-answers-btn"
                        onClick={submitAnswers}
                        disabled={Object.keys(userAnswers).length !== questions.length}
                    >
                        Submit Answers
                    </button>
                )}

                <button 
                    className="more-questions-btn"
                    onClick={generateMoreQuestions}
                >
                    Generate More Questions
                </button>
            </div>
        </div>
    );
}

export default Questions;