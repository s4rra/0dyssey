import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
// import "../css/bookmarks.css";

const BookmarksPage = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in to view bookmarks.");
      navigate("/login");
      return;
    }

    const fetchBookmarks = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://127.0.0.1:8080/api/bookmarks", {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (!response.ok) {
          throw new Error("Failed to fetch bookmarks");
        }
        
        const data = await response.json();
        setBookmarks(data.bookmarks || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBookmarks();
  }, [navigate]);

  const handleRemoveBookmark = async (subUnitId) => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8080/api/bookmark/${subUnitId}`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        setBookmarks(bookmarks.filter(bookmark => bookmark.subUnitID !== subUnitId));
      }
    } catch (error) {
      console.error("Error removing bookmark:", error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your bookmarks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Bookmarks</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="bookmarks-container">
      <div className="bookmarks-header">
        <h1>Your Bookmarked Lessons</h1>
        <p>{bookmarks.length} {bookmarks.length === 1 ? "bookmark" : "bookmarks"}</p>
      </div>

      {bookmarks.length === 0 ? (
        <div className="empty-bookmarks">
          <p>You haven&apos;t bookmarked any lessons yet.</p>
          <Link to="/courses" className="explore-link">
            Explore Courses
          </Link>
        </div>
      ) : (
        <div className="bookmarks-grid">
          {bookmarks.map((bookmark) => (
            <div key={bookmark.subUnitID} className="bookmark-card">
              <div className="bookmark-content">
                <h3>{bookmark.subUnitName}</h3>
                {bookmark.subUnitDescription && (
                  <p className="description">{bookmark.subUnitDescription}</p>
                )}
                <div className="bookmark-actions">
                  <Link
                    to={`/subunit/${bookmark.subUnitID}`}
                    className="view-link"
                  >
                    View Lesson
                  </Link>
                  <button
                    onClick={() => handleRemoveBookmark(bookmark.subUnitID)}
                    className="remove-btn"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BookmarksPage;