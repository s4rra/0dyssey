import { useEffect, useState} from "react";
import axios from "axios";
//import "../css/questions.css";

function Questions() {
    const [questions, setQuestions] = useState({});
    const [loading, setLoading] = useState(true);
    const [userAnswers, setUserAnswers] = useState({});

    const API_URL = "http://127.0.0.1:8080/questions";

    useEffect(() => { 
        axios
            .get(API_URL)
            .then((response) => {
                setQuestions(response.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching questions:", error);
                setLoading(false);
            });
    }, []);

    if (loading) return <p className="loading-text">Loading...</p>;

    const handleAnswer =(questionkey, value) => setUserAnswers({...userAnswers,[questionkey]:value});

      const renderFillInAndMCQ = (questionKey, question, questionNumber) => (
        <div className="question-box">
          <p className="question-text">
            <strong>{questionNumber}. </strong>
            {question.question}
          </p>
          <div className="options-container" >
            {question.options && Object.entries(question.options).map(([key, value]) => (
              <label key={key} className="option-label">
                <input
                  type="radio"
                  name={questionKey}
                  value={key}
                  checked={userAnswers[questionKey] === key}
                  onChange={(e) => handleAnswer(questionKey, e.target.value)}
                  
                />
                {value}
              </label>
            ))}
          </div>
        </div>
      );

      /*
       const renderDropDown = (questionKey, question, questionNumber) => {
        return 
      };*/
    
      const renderCoding = (questionKey, question, questionNumber) => (
        <div className="question-box">
          <p className="question-text">
            <strong>{questionNumber}. </strong>
            {question.question}
          </p>
          <textarea
            className="coding-textarea"
            value={userAnswers[questionKey] || ''}
            onChange={(e) => handleAnswer(questionKey, e.target.value)}
            placeholder="Write your code..."
          />
        </div>
      );
      
      return (
        <div className="questions-container">
          <h1 className="questions-title">
            Questions
          </h1>
          
          <div className="question-list">
            {//convert questions object to array pair, loops
            Object.entries(questions).map(([key, question], index) => (
              <div key={key}>
                {question.type === 'multiple_choice' && renderFillInAndMCQ(key, question, index + 1)}
                {question.type === 'fill_in_the_blanks' && renderFillInAndMCQ(key, question, index + 1)}
                {/*question.type === 'drop_down' && renderDropDown(key, question, index + 1)*/}
                {question.type === 'coding' && renderCoding(key, question, index + 1)}
              </div>
            ))}
          </div>
        </div>
      );
}
export default Questions;
