import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../css/subunit.css";

const SubUnit = () => {
  const { subUnitId } = useParams();
  const [subUnitContent, setSubUnitContent] = useState(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarkLoading, setBookmarkLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = `http://127.0.0.1:8080/api/subunit/${subUnitId}`;
  const BOOKMARK_API_URL = `http://127.0.0.1:8080/api/bookmark/${subUnitId}`;

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    // Fetch subunit content
    setLoading(true);
    fetch(API_URL, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched subunit content:", data);
        setSubUnitContent(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching subunit content:", error);
        setLoading(false);
      });

    // Check if current subunit is bookmarked
    fetch(`http://127.0.0.1:8080/api/bookmarks`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.bookmarks) {
          const bookmarked = data.bookmarks.some(
            (bookmark) => bookmark.subUnitID === parseInt(subUnitId)
          );
          setIsBookmarked(bookmarked);
        }
      })
      .catch((error) => {
        console.error("Error checking bookmark status:", error);
      });
  }, [subUnitId, navigate, API_URL]);

  const handleBackClick = (e) => {
    e.preventDefault();
    navigate("/courses"); 
  };

  const toggleBookmark = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in to bookmark lessons.");
      navigate("/login");
      return;
    }

    setBookmarkLoading(true);
    try {
      if (isBookmarked) {
        // Remove bookmark
        await fetch(BOOKMARK_API_URL, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        setIsBookmarked(false);
      } else {
        // Add bookmark
        await fetch(BOOKMARK_API_URL, {
          method: "POST",
          headers: { 
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({}),
        });
        setIsBookmarked(true);
      }
    } catch (error) {
      console.error("Error toggling bookmark:", error);
      alert("Failed to update bookmark. Please try again.");
    } finally {
      setBookmarkLoading(false);
    }
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
        <p>We couldn&apos;t find the lesson you&apos;re looking for.</p>
        <button onClick={handleBackClick} className="back-button">
          Back to Courses
        </button>
      </div>
    );
  }

  const {
    subUnitName,
    subUnitDescription,
    subUnitContent: content,
  } = subUnitContent;

  return (
    <div className="subunit-container">
      <div className="subunit-header">
        <button onClick={handleBackClick} className="back-link">
          ← Back to Courses
        </button>
        
        <button
          onClick={toggleBookmark}
          disabled={bookmarkLoading}
          className={`bookmark-btn ${isBookmarked ? "bookmarked" : ""}`}
        >
          {isBookmarked ? "★ Bookmarked" : "☆ Bookmark"}
        </button>
      </div>

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

              {section.text && <p className="section-text">{section.text}</p>}

              {section.list && (
                <ul className="section-list">
                  {section.list.map((item, i) => (
                    <li key={i} className="list-item">
                      {item}
                    </li>
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
        <button className="quiz-button">Take Quiz on {subUnitName}</button>
      </div>
    </div>
  );
};

export default SubUnit;