import { useState, useEffect } from 'react';
import '../css/profilePicture.css';

function ProfilePicture({ onPictureSelect, currentPictureId }) {
  const [pictures, setPictures] = useState([]);
  const [showSelector, setShowSelector] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentPicture, setCurrentPicture] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = "http://127.0.0.1:8080/api";

  // Fetch available profile pictures
  useEffect(() => {
    const fetchProfilePictures = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/profile-pictures`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setPictures(data);
        
        // If we have a currentPictureId, find that picture
        if (currentPictureId) {
          const current = data.find(pic => pic.pictureID === currentPictureId);
          setCurrentPicture(current || null);
        }
      } catch (err) {
        setError(err.message);
        console.error("Error fetching profile pictures:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfilePictures();
  }, [currentPictureId]);

  // Handle picture selection
  const handlePictureSelect = async (picture) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Authentication required");
        return;
      }

      const response = await fetch(`${API_URL}/update-profile-picture`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ pictureID: picture.pictureID })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      setCurrentPicture(picture);
      setShowSelector(false);
      
      // Call parent callback if provided
      if (onPictureSelect) {
        onPictureSelect(picture);
      }
    } catch (err) {
      setError(err.message);
      console.error("Error updating profile picture:", err);
    }
  };

  // Toggle the picture selector
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
          <div className="no-picture">
            Select Picture
          </div>
        )}
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      {showSelector && (
        <div className="picture-selector">
          <h3>Select a Profile Picture</h3>
          <div className="pictures-grid">
            {pictures.map((picture) => (
              <div 
                key={picture.pictureID}
                className={`picture-item ${currentPicture?.pictureID === picture.pictureID ? 'selected' : ''}`}
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
          <button className="close-selector" onClick={toggleSelector}>Cancel</button>
        </div>
      )}
    </div>
  );
}

export default ProfilePicture;