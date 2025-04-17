import "../css/dashboard.css";
import "../css/calendar.css";
import "../css/objectives.css";
import Calendar from "react-calendar";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ProfilePicture from "./ProfilePicture";
import Objectives from "./Objectives";

function Dashboard() {
  const [date, setDate] = useState(new Date());
  const [userData, setUserData] = useState({
    username: "",
    streakLength: 0,
    lastLogin: null,
    profilePicture: null,
    points: 0,
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8080/api/user-profile";

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Please log in first.");
        navigate("/login");
        return;
      }

      try {
        const response = await fetch(API_URL, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        setUserData({
          username: data.userName,
          streakLength: data.streakLength || 0,
          lastLogin: data.lastLogin ? new Date(data.lastLogin) : null,
          profilePicture: data.profilePicture || null,
          points: data.points || 0,
        });
      } catch (error) {
        console.error("Error fetching user data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const isStreakDay = (date) => {
    if (!userData.lastLogin) return false;

    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);

    const startDate = new Date(userData.lastLogin);
    startDate.setHours(0, 0, 0, 0);
    startDate.setDate(startDate.getDate() - (userData.streakLength - 1));

    return checkDate >= startDate && checkDate <= new Date(userData.lastLogin);
  };

  const tileClassName = ({ date, view }) => {
    if (view !== "month") return "";

    if (isStreakDay(date)) {
      const lastLoginDate = new Date(userData.lastLogin);
      lastLoginDate.setHours(0, 0, 0, 0);

      const tileDate = new Date(date);
      tileDate.setHours(0, 0, 0, 0);

      return tileDate.getTime() === lastLoginDate.getTime()
        ? "streak-day current-streak-day"
        : "streak-day";
    }

    return "";
  };

  const handleProfilePictureUpdate = (picture) => {
    setUserData((prev) => ({
      ...prev,
      profilePicture: picture.pictureID,
    }));
  };
  
  const handlePointsUpdate = (pointsAwarded) => {
    setUserData((prev) => ({
      ...prev,
      points: prev.points + pointsAwarded,
    }));
  };

  if (loading) return <p>Loading...</p>;

  return (
    <main className="main-content">
      <section className="dashboard-content">
        <h2>Welcome, {userData.username}!</h2>

        <div className="cards-container">
          <div className="card profile-card">
            <ProfilePicture
              onPictureSelect={handleProfilePictureUpdate}
              currentPictureId={userData.profilePicture}
              userPoints={userData.points}
            />
          </div>
          <div className="card calendar-card">
            <Calendar
              onChange={setDate}
              value={date}
              tileClassName={tileClassName}
            />
          </div>
          <div className="card objectives-card">
            <Objectives onPointsEarned={handlePointsUpdate} />
          </div>
        </div>
      </section>
    </main>
  );
}

export default Dashboard;