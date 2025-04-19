import "../css/dashboard.css";
import Calendar from "react-calendar";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Radar } from "react-chartjs-2";

import ProfilePicture from "./ProfilePicture";
import Objectives from "./Objectives";

import {
  BookOpen,
  Clock,
  MessageSquare,
  ListChecks,
} from "lucide-react";

import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const API_PROFILE = "http://127.0.0.1:8080/api/user-profile2";
const API_FEEDBACK = (unitId) =>
  `http://127.0.0.1:8080/api/performance/unit/${unitId}`;
const API_HISTORY = (subunitId) =>
  `http://127.0.0.1:8080/api/performance/history/${subunitId}`;
const API_SKILL_UPDATE = "http://127.0.0.1:8080/api/performance/skill-level";

function Dashboard() {
  const [date, setDate] = useState(new Date());
  const [feedbackData, setFeedbackData] = useState({
    aiSummary: "",
    feedbackPrompt: "",
    levelSuggestion: null,
    tagInsights: [],
    subunitFeedback: [],
  });

  const [activityLog, setActivityLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userData, setUserData] = useState({
    streakLength: 0,
    lastLogin: null,
    profilePicture: null,
    username: "Student",
    currentUnit: 1,
    currentSubUnit: null,
    points: 0,
  });

  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const res = await fetch(API_PROFILE, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();

      const profile = {
        streakLength: data.streakLength || 0,
        lastLogin: data.lastLogin ? new Date(data.lastLogin) : null,
        profilePicture: data.profilePicture || null,
        username: data.userName || "Student",
        currentUnit: data.currentUnit || 1,
        currentSubUnit: data.currentSubUnit || null,
        points: data.points || 0,
      };

      setUserData(profile);

      await fetchFeedback(profile.currentUnit);
      if (profile.currentSubUnit) {
        await fetchActivity(profile.currentSubUnit);
      }
    } catch (err) {
      console.error("Failed to fetch user data:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFeedback = async (unitId) => {
    try {
      const res = await fetch(API_FEEDBACK(unitId), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const result = await res.json();
      const feedback = result.feedback || {};
      const subunitFeedback = result.subunitFeedback || [];

      const tagInsights = feedback.tagPerformance
        ? Object.entries(feedback.tagPerformance).map(([tag, data]) => ({
            tag,
            score: data.percentage || 0,
          }))
        : [];

      setFeedbackData({
        aiSummary: feedback.aiSummary || "",
        feedbackPrompt: feedback.feedbackPrompt || "",
        levelSuggestion: feedback.levelSuggestion || null,
        tagInsights,
        subunitFeedback,
      });
    } catch (err) {
      console.error("Failed to fetch feedback:", err);
    }
  };

  const fetchActivity = async (subunitId) => {
    try {
      const res = await fetch(API_HISTORY(subunitId), {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();
      const log = data.map((entry) => ({
        lesson: entry.subUnitDescription || `Subunit ${entry.subUnitID}`,
        score: `${entry.correctAnswers}/${entry.totalQuestions}`,
        time: `${Math.round(entry.totalTimeTaken / 60)}m`,
        date: formatDate(entry.updatedAt),
      }));

      setActivityLog(log);
    } catch (err) {
      console.error("Failed to fetch activity:", err);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const isStreakDay = (dateToCheck) => {
    if (!userData?.lastLogin) return false;

    const checkDate = new Date(dateToCheck);
    checkDate.setHours(0, 0, 0, 0);

    const lastLogin = new Date(userData.lastLogin);
    lastLogin.setHours(0, 0, 0, 0);

    const startDate = new Date(lastLogin);
    startDate.setDate(startDate.getDate() - (userData.streakLength - 1));

    return checkDate >= startDate && checkDate <= lastLogin;
  };

  const tileClassName = ({ date, view }) => {
    if (view !== "month") return "";
    const tileDate = new Date(date);
    tileDate.setHours(0, 0, 0, 0);
    const lastLoginDate = new Date(userData?.lastLogin);
    lastLoginDate.setHours(0, 0, 0, 0);
    if (isStreakDay(tileDate)) {
      return tileDate.getTime() === lastLoginDate.getTime()
        ? "streak-day current-streak-day"
        : "streak-day";
    }
    return "";
  };

  const handlePictureChange = (pic) => {
    setUserData((prev) => ({ ...prev, profilePicture: pic.pictureID }));
  };

  const handlePointsUpdate = (pointsAwarded) => {
    if (pointsAwarded > 0) {
      setUserData((prev) => ({
        ...prev,
        points: prev.points + pointsAwarded,
      }));
    }
  };

  const confirmLevelSuggestion = async () => {
    try {
      const res = await fetch(API_SKILL_UPDATE, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ skillLevel: feedbackData.levelSuggestion }),
      });

      const result = await res.json();
      if (!result.success) console.warn("Skill update failed", result);
    } catch (err) {
      console.error("Skill update error:", err);
    }
  };

  const radarData = {
    labels: feedbackData?.tagInsights.map((t) => t.tag) || [],
    datasets: [
      {
        label: "Progress",
        data: feedbackData?.tagInsights.map((t) => t.score) || [],
        backgroundColor: "rgba(34,197,94,0.2)",
        borderColor: "rgba(34,197,94,1)",
        borderWidth: 2,
      },
    ],
  };

  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { stepSize: 20, backdropColor: "transparent" },
      },
    },
    plugins: { legend: { display: false } },
    interaction: {
      mode: "nearest",
      axis: "x",
      intersect: false,
    },
  };

  const calcStats = () => {
    let totalQ = 0,
      correct = 0,
      minutes = 0;

    activityLog.forEach((log) => {
      const [c, t] = log.score.split("/").map(Number);
      correct += c;
      totalQ += t;
      minutes += parseInt(log.time) || 0;
    });

    const acc = totalQ ? Math.round((correct / totalQ) * 100) : 0;
    return `This week you answered ${totalQ} questions with ${acc}% accuracy over ${minutes}m`;
  };

  if (loading || !userData) return <p>Loading...</p>;

  return (
    <div className="dashboard-page">
      <h2 className="dashboard-heading">Welcome {userData.username}!</h2>

      <div className="cards-container">
        <div>
          <ProfilePicture
            onPictureSelect={handlePictureChange}
            currentPictureId={userData.profilePicture}
          />
        </div>

        <div>
          <Calendar
            onChange={setDate}
            value={date}
            tileClassName={tileClassName}
          />
        </div>

        <div className="card points-card">
          <h3>Your Points</h3>
          <p className="points-value">{userData.points}</p>
        </div>
      </div>

      <div className="cards-container">
        <div className="card objectives-card">
          <div className="card-header">
            <h3>Objectives</h3>
            <ListChecks className="card-icon" />
          </div>
          <Objectives onPointsEarned={handlePointsUpdate} />
        </div>
      </div>

      <div className="cards-container">
        <div className="card">
          <div className="card-header">
            <h3>Activity Log</h3>
            <BookOpen className="card-icon" />
          </div>
          {activityLog.length > 0 ? (
            activityLog.map((a, i) => (
              <div key={i} className="log-row">
                <div>
                  <p className="log-title">{a.lesson}</p>
                  <p className="log-date">{a.date}</p>
                </div>
                <div className="log-metrics">
                  <p className="log-score">{a.score}</p>
                  <p className="log-time">{a.time}</p>
                </div>
              </div>
            ))
          ) : (
            <p>No activity yet.</p>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Weekly Stats</h3>
            <Clock className="card-icon" />
          </div>
          <p>{calcStats()}</p>
        </div>
      </div>

      <div className="cards-container">
        <div className="card">
          <h3 className="section-title">Progress Chart</h3>
          {feedbackData?.tagInsights?.length > 0 ? (
            <Radar data={radarData} options={radarOptions} />
          ) : (
            <p>No chart data yet</p>
          )}
        </div>

        <div className="card suggestion-box">
          <div className="card-header">
            <h3>Quick Note</h3>
            <MessageSquare className="card-icon" />
          </div>
          <p className="note-text">{feedbackData?.aiSummary}</p>
          <p className="suggestion-text">{feedbackData?.feedbackPrompt}</p>

          {feedbackData?.subunitFeedback.length > 0 && (
            <div className="subunit-feedback">
              <h4>Subunit Insights</h4>
              {feedbackData.subunitFeedback.map((fb, idx) => (
                <div key={idx} className="subunit-item">
                  <p><strong>{fb.subUnitDescription}</strong></p>
                  <p>{fb.aiSummary}</p>
                </div>
              ))}
            </div>
          )}

          {feedbackData?.levelSuggestion && (
            <button className="confirm-button" onClick={confirmLevelSuggestion}>
              Ok!
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
