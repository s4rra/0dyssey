import { useState, useEffect } from "react";
import "../css/profilePicture.css";

function ProfilePicture({ onPictureSelect }) {
  const [pictures, setPictures] = useState([]);
  const [showSelector, setShowSelector] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentPicture, setCurrentPicture] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = "http://127.0.0.1:8080/api";

  useEffect(() => {
    const fetchProfilePictures = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setError("Authentication required");
          return;
        }

        const response = await fetch(`${API_URL}/profile-pictures`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const availablePictures = data.filter((pic) => pic.available);
        setPictures(availablePictures);
        return availablePictures;
      } catch (err) {
        setError(err.message);
        console.error("Error fetching profile pictures:", err);
        return [];
      }
    };

    const fetchCurrentUserPicture = async (availablePictures) => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const res = await fetch(`${API_URL}/user-profile`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Failed to fetch user profile");

        const data = await res.json();
        const profile = Array.isArray(data) ? data[0] : data;

        if (profile?.profilePicture) {
          const pic = availablePictures.find(
            (p) => p.pictureID === profile.profilePicture
          );
          if (pic) setCurrentPicture(pic);
        }
      } catch (err) {
        console.error("Error fetching current user picture:", err);
      }
    };

    const init = async () => {
      setLoading(true);
      const availablePictures = await fetchProfilePictures();
      await fetchCurrentUserPicture(availablePictures);
      setLoading(false);
    };

    init();
  }, []);

  const handlePictureSelect = async (picture) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Authentication required");
        return;
      }

      const updateResponse = await fetch(`${API_URL}/update-profile-picture`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ pictureID: picture.pictureID }),
      });

      if (!updateResponse.ok) {
        const errorData = await updateResponse.json();
        throw new Error(
          errorData.error || `HTTP error! Status: ${updateResponse.status}`
        );
      }

      setCurrentPicture(picture);
      setShowSelector(false);

      if (onPictureSelect) {
        onPictureSelect(picture);
      }
    } catch (err) {
      setError(err.message);
      console.error("Error updating profile picture:", err);
    }
  };

  const toggleSelector = () => {
    setShowSelector(!showSelector);
    setError(null);
  };

  if (loading && !currentPicture) {
    return <div className="profile-picture loading">Loading...</div>;
  }

  return (
    <div className="profile-picture-container">
      <div className="current-picture" onClick={toggleSelector}>
        {currentPicture ? (
          <img
            src={currentPicture.imagePath}
            alt={currentPicture.displayName}
            className="profile-image"
          />
        ) : (
          <div className="no-picture">Select Picture</div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {showSelector && (
        <div className="picture-selector">
          <h3>Select a Profile Picture</h3>
          {pictures.length === 0 ? (
            <div className="no-pictures-message">
              <p>You don&apos;t have any profile pictures yet.</p>
              <p>
                Visit the <a href="/shop">Shop</a> to purchase some!
              </p>
            </div>
          ) : (
            <div className="pictures-grid">
              {pictures.map((picture) => (
                <div
                  key={picture.pictureID}
                  className={`picture-item ${
                    currentPicture?.pictureID === picture.pictureID
                      ? "selected"
                      : ""
                  }`}
                  onClick={() => handlePictureSelect(picture)}
                >
                  <img
                    src={picture.imagePath}
                    alt={picture.displayName}
                    className="selector-image"
                  />
                  <span className="picture-name">{picture.displayName}</span>
                </div>
              ))}
            </div>
          )}
          <button className="close-selector" onClick={toggleSelector}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

export default ProfilePicture;
