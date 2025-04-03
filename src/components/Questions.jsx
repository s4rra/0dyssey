import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function Questions() {
    const [questions, setQuestions] = useState([]);
    const [userAnswers, setUserAnswers] = useState({});
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
    }, [subunitId]);

    const fetchQuestions = async () => {
        setLoading(true);
        try {
            const res = await fetch(API_URL, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = await res.json();
            setQuestions(data);
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
        const answersData = questions.map(q => ({
            questionId: q.questionID,
            questionTypeId: q.questionTypeID,
            userAnswer: userAnswers[q.questionID] || '',
            correctAnswer: q.correctAnswer,
            constraints: q.constraints || ''
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
        const resultsMap = {};
        result.results.forEach(r => {
            resultsMap[r.questionId] = r;
        });
        setSubmissionResults(resultsMap);
    };

    const renderMCQ = (q, i) => (
        <div key={q.questionID}>
            <p>{i + 1}. {q.questionText}</p>
            {q.options && Object.entries(q.options).map(([key, value]) => (
                <label key={key}>
                    <input
                        type="radio"
                        name={q.questionID}
                        value={key}
                        checked={userAnswers[q.questionID] === key}
                        onChange={() => handleAnswerChange(q.questionID, key)}
                        disabled={!!submissionResults[q.questionID]}
                    />
                    {value}
                </label>
            ))}
            {submissionResults[q.questionID] && (
                <div>{submissionResults[q.questionID].isCorrect ? "Correct!" : "Incorrect"}</div>
            )}
        </div>
    );

    const renderFillIn = (q, i) => {
        const parts = q.questionText.split("_____");
        const blanksCount = parts.length - 1;
        const answers = userAnswers[q.questionID] || [];

        return (
            <div key={q.questionID}>
                <p>
                    {i + 1}. {parts.map((part, index) => (
                        <span key={index}>
                            {part}
                            {index < blanksCount && (
                                <input
                                    type="text"
                                    value={answers[index] || ""}
                                    onChange={e => handleFillBlankChange(q.questionID, index, e.target.value)}
                                    disabled={!!submissionResults[q.questionID]}
                                />
                            )}
                        </span>
                    ))}
                </p>
                {submissionResults[q.questionID] && (
                    <>
                        <div>{submissionResults[q.questionID].isCorrect ? "Correct!" : "Incorrect"}</div>
                        {submissionResults[q.questionID].feedback && <div><strong>Feedback:</strong> {submissionResults[q.questionID].feedback}</div>}
                        {submissionResults[q.questionID].hint && (
                            <>
                                <button onClick={() => toggleHint(q.questionID)}>Hint?</button>
                                {showHints[q.questionID] && <div><strong>Hint:</strong> {submissionResults[q.questionID].hint}</div>}
                            </>
                        )}
                    </>
                )}
            </div>
        );
    };

    const renderDragDrop = (question, questionNumber) => {
        const result = submissionResults[question.questionID];
    
        const blankCount = (question.questionText.match(/_____/g) || []).length;
    
        const blanks = userAnswers[question.questionID] || Array(blankCount).fill("");
    
        const handleDrop = (e, index) => {
            const data = e.dataTransfer.getData("text/plain");
            const updated = [...blanks];
            updated[index] = data;
            setUserAnswers(prev => ({ ...prev, [question.questionID]: updated }));
        };
    
        const allowDrop = (e) => e.preventDefault();
    
        const handleDragStart = (e, text) => {
            e.dataTransfer.setData("text/plain", text);
        };
    
        const handleClearBlank = (index) => {
            const updated = [...blanks];
            updated[index] = "";
            setUserAnswers(prev => ({ ...prev, [question.questionID]: updated }));
        };
    
        const parts = question.questionText.split("_____");
    
        return (
            <div key={question.questionID}>
                <p><strong>{questionNumber}.</strong>{" "}
                    {parts.map((part, i) => (
                        <span key={i}>
                            {part}
                            {i < blankCount && (
                                <span
                                    onDrop={(e) => handleDrop(e, i)}
                                    onDragOver={allowDrop}
                                    style={{
                                        display: "inline-block",
                                        minWidth: "60px",
                                        minHeight: "25px",
                                        border: "1px dashed gray",
                                        margin: "0 5px",
                                        padding: "2px 4px",
                                        textAlign: "center",
                                        backgroundColor: "#f7f7f7",
                                        cursor: "pointer"
                                    }}
                                    title="   "
                                >
                                    {blanks[i]}
                                    {blanks[i] && (
                                        <button onClick={() => handleClearBlank(i)} style={{
                                            marginLeft: "5px",
                                            cursor: "pointer",
                                            fontSize: "12px",
                                            background: "none",
                                            border: "none",
                                            color: "red"
                                        }}>X</button>
                                    )}
                                </span>
                            )}
                        </span>
                    ))}
                </p>
    
                <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginTop: "10px" }}>
                    {question.options.map((option, index) => (
                        <div
                            key={index}
                            draggable
                            onDragStart={(e) => handleDragStart(e, option)}
                            style={{
                                padding: "6px 10px",
                                border: "1px solid #aaa",
                                borderRadius: "4px",
                                backgroundColor: "#eee",
                                cursor: "grab"
                            }}
                        >
                            {option}
                        </div>
                    ))}
                </div>
    
                {result && (
                    <div style={{ marginTop: "10px" }}>
                        <div>{result.isCorrect ? "Correct!" : "Incorrect"}</div>
                        {result.hint && (
                            <div>
                                <button onClick={() => toggleHint(question.questionID)}>
                                    {showHints[question.questionID] ? 'Hide Hint' : 'Show Hint'}
                                </button>
                                {showHints[question.questionID] && <p><strong>Hint:</strong> {result.hint}</p>}
                            </div>
                        )}
                        {result.feedback && <p><strong>Feedback:</strong> {result.feedback}</p>}
                    </div>
                )}
            </div>
        );
    };
    

    const renderCoding = (q, i) => (
        <div key={q.questionID}>
            <p>{i + 1}. {q.questionText}</p>
            <textarea
                rows="4"
                value={userAnswers[q.questionID] || ""}
                onChange={e => handleAnswerChange(q.questionID, e.target.value)}
                disabled={!!submissionResults[q.questionID]}
            />
            {submissionResults[q.questionID] && (
                <>
                    <div>{submissionResults[q.questionID].isCorrect ? "Correct!" : "Incorrect"}</div>
                    {submissionResults[q.questionID].feedback && <div><strong>Feedback:</strong> {submissionResults[q.questionID].feedback}</div>}
                    {submissionResults[q.questionID].hint && (
                        <>
                            <button onClick={() => toggleHint(q.questionID)}>Hint?</button>
                            {showHints[q.questionID] && <div><strong>Hint:</strong> {submissionResults[q.questionID].hint}</div>}
                        </>
                    )}
                </>
            )}
        </div>
    );

    if (loading) return <p>Loading...</p>;

    return (
        <div>
            <h3>Questions</h3>
            {questions.map((q, i) => {
                if (q.questionTypeID === 1) return renderMCQ(q, i);
                if (q.questionTypeID === 2) return renderCoding(q, i);
                if (q.questionTypeID === 3) return renderFillIn(q, i);
                if (q.questionTypeID === 4) return renderDragDrop(q, i);
                return null;
            })}
            <div>
                {Object.keys(submissionResults).length === 0 && (
                    <button onClick={submitAnswers} disabled={Object.keys(userAnswers).length !== questions.length}>
                        Submit
                    </button>
                )}
                <button onClick={generateMoreQuestions}>More Questions?</button>
            </div>
        </div>
    );
}

export default Questions;
