import "../css/dashboard.css";
import "../css/calendar.css";
import Calendar from "react-calendar";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const [date, setDate] = useState(new Date());
  const [streakInfo, setStreakInfo] = useState({
    streakLength: 0,
    lastLogin: null
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8080/api/user-profile";

  useEffect(() => {
    // Fetch user streak information when component mounts
    const fetchUserData = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Please log in first.");
        navigate("/login");
        return;
      }

      try {
        const response = await fetch(API_URL, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const userData = await response.json();
        
        setStreakInfo({
          streakLength: userData.streakLength || 0,
          lastLogin: userData.lastLogin ? new Date(userData.lastLogin) : null
        });
        setLoading(false);
      } catch (error) {
        console.error("Error fetching user data:", error);
        setLoading(false);
      }
    };
    
    fetchUserData();
  }, [navigate]);

  // Function to check if a date is part of the streak
  const isStreakDay = (date) => {
    if (!streakInfo.lastLogin) return false;
    
    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);
    
    // Calculate the start date of the streak
    const startDate = new Date(streakInfo.lastLogin);
    startDate.setHours(0, 0, 0, 0);
    startDate.setDate(startDate.getDate() - (streakInfo.streakLength - 1));
    
    // Check if the date is between the start date and last login date (inclusive)
    return checkDate >= startDate && checkDate <= new Date(streakInfo.lastLogin);
  };

  // Function to add custom classes to calendar tiles
  const tileClassName = ({ date, view }) => {
    if (view !== 'month') return '';
    
    // Check if this date is part of the streak
    if (isStreakDay(date)) {
      // Check if it's the last login date
      const lastLoginDate = streakInfo.lastLogin ? new Date(streakInfo.lastLogin) : null;
      lastLoginDate?.setHours(0, 0, 0, 0);
      
      const tileDate = new Date(date);
      tileDate.setHours(0, 0, 0, 0);
      
      if (lastLoginDate && tileDate.getTime() === lastLoginDate.getTime()) {
        return 'streak-day current-streak-day';
      }
      return 'streak-day';
    }
    
    return '';
  };

  // No content in tiles, just coloring
  const tileContent = null;

  if (loading) return <p>Loading...</p>;

  return (
    <main className="main-content">
      <section className="dashboard-content">
        <div className="cards-container">
          <div className="card calendar-card">
            <Calendar 
              onChange={setDate} 
              value={date}
              tileClassName={tileClassName}
            />
          </div>
        </div>
      </section>
    </main>
  );
}

export default Dashboard;