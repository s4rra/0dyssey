import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/bookmarks.css"; // You'll need to create this CSS file

const Bookmarks = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    // Fetch user's bookmarks
    fetch("http://127.0.0.1:8080/api/bookmarks", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch bookmarks");
        }
        return res.json();
      })
      .then((data) => {
        setBookmarks(data.bookmarks || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching bookmarks:", error);
        setError("Failed to load bookmarks. Please try again later.");
        setLoading(false);
      });
  }, [navigate]);

  const handleRemoveBookmark = async (subUnitID) => {
    const token = localStorage.getItem("token");
    try {
      const response = await fetch(`http://127.0.0.1:8080/api/bookmark/${subUnitID}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (!response.ok) {
        throw new Error("Failed to remove bookmark");
      }
      
      // Update local state to remove the bookmark
      setBookmarks(bookmarks.filter(bookmark => bookmark.subUnitID !== subUnitID));
    } catch (error) {
      console.error("Error removing bookmark:", error);
      alert("Failed to remove bookmark. Please try again.");
    }
  };

  const navigateToSubunit = (subUnitID) => {
    navigate(`/courses/subunit/${subUnitID}`);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading bookmarks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate("/courses")} className="back-button">
          Back to Courses
        </button>
      </div>
    );
  }

  return (
    <div className="bookmarks-container">
      <h1>My Bookmarks</h1>
      
      {bookmarks.length === 0 ? (
        <div className="no-bookmarks">
          <p>You don&apos;t have any bookmarks yet.</p>
          <button onClick={() => navigate("/courses")} className="browse-button">
            Browse Courses
          </button>
        </div>
      ) : (
        <div className="bookmarks-list">
          {bookmarks.map((bookmark) => (
            <div key={bookmark.bookmarkID} className="bookmark-item">
              <div className="bookmark-content" onClick={() => navigateToSubunit(bookmark.subUnitID)}>
                <h3>{bookmark.subUnitName}</h3>
              </div>
              <button
                className="remove-bookmark-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveBookmark(bookmark.subUnitID);
                }}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
      
      <button onClick={() => navigate("/courses")} className="back-button">
        Back to Courses
      </button>
    </div>
  );
};

export default Bookmarks;