import { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import "../css/SubUnit.css"; 

const SubUnit = () => {
  const { subUnitId } = useParams();
  const [subUnitContent, setSubUnitContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    axios.get(`http://127.0.0.1:8080/subunit/${subUnitId}`)
      .then(response => {
        console.log("Fetched subunit content:", response.data);
        setSubUnitContent(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching subunit content:", error);
        setLoading(false);
      });
  }, [subUnitId]);

  const handleBackClick = (e) => {
  e.preventDefault();
  navigate("/courses"); // Navigate to the courses page
};

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading lesson content...</p>
      </div>
    );
  }

  if (!subUnitContent) {
    return (
      <div className="error-container">
        <h2>Content Not Found</h2>
        <p>We couldn't find the lesson you're looking for.</p>
        <button onClick={handleBackClick} className="back-button">Back to Courses</button>
      </div>
    );
  }

  const { subUnitName, subUnitDescription, subUnitContent: content } = subUnitContent;

  return (
    <div className="subunit-container">
      <button onClick={handleBackClick} className="back-link">
        ← Back to Courses
      </button>
      
      <div className="lesson-header">
        <h1 className="lesson-title">{subUnitName}</h1>
        {subUnitDescription && (
          <p className="lesson-description">{subUnitDescription}</p>
        )}
      </div>

      <div className="lesson-content">
        {content && content.title && (
          <h2 className="content-title">{content.title}</h2>
        )}

        {content && content.content && Array.isArray(content.content) ? (
          content.content.map((section, index) => (
            <div key={index} className="content-section">
              {section.heading && (
                <h3 className="section-heading">{section.heading}</h3>
              )}
              
              {section.text && (
                <p className="section-text">{section.text}</p>
              )}

              {section.list && (
                <ul className="section-list">
                  {section.list.map((item, i) => (
                    <li key={i} className="list-item">{item}</li>
                  ))}
                </ul>
              )}

              {section.code && (
                <div className="code-block">
                  <pre className="code-example">{section.code.example}</pre>
                  <div className="code-explanation">
                    <h4>Explanation:</h4>
                    <p>{section.code.explanation}</p>
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="no-content-message">
            <p>No lesson content available yet.</p>
            <p>Check back soon!</p>
          </div>
        )}
      </div>
      
      <div className="lesson-footer">
        <button className="quiz-button">
          Take Quiz on {subUnitName}
        </button>
      </div>
    </div>
  );
};

export default SubUnit;