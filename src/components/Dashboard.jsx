import "../css/dashboard.css";
import { useEffect, useState, Suspense, lazy } from "react";
import { useNavigate } from "react-router-dom";
import ProfilePicture from "./ProfilePicture";

import {
  BookOpen,
  Clock,
  MessageSquare,
  ListChecks,
  Loader
} from "lucide-react";

// Lazy load components
const Calendar = lazy(() => import("react-calendar"));
const Objectives = lazy(() => import("./Objectives"));
const Radar = lazy(() => import("react-chartjs-2").then(module => ({ default: module.Radar })));

// Chart.js registration can be moved to a separate file or lazy-loaded too
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
const API_DASHBOARD = "http://127.0.0.1:8080/api/performance/dashboard";
const API_HISTORY = (subunitId) =>
  `http://127.0.0.1:8080/api/performance/history/${subunitId}`;
const API_TAGS = "http://127.0.0.1:8080/api/performance/tags";
const API_UNIT_FEEDBACK = (unitId) =>
  `http://127.0.0.1:8080/api/performance/unit-feedback/${unitId}`;
const API_SKILL_UPDATE = "http://127.0.0.1:8080/api/performance/skill-level";

// Timeout for data fetching in milliseconds
const FETCH_TIMEOUT = 8000;

function Dashboard() {
  const [date, setDate] = useState(new Date());
  const [userData, setUserData] = useState({
    streakLength: 0,
    lastLogin: null,
    profilePicture: null,
    username: "Student",
    currentUnit: 1,
    currentSubUnit: null,
    points: 0,
  });
  
  // Individual loading states
  const [profileLoading, setProfileLoading] = useState(true);
  const [feedbackLoading, setFeedbackLoading] = useState(true);
  const [tagsLoading, setTagsLoading] = useState(true);
  const [activityLoading, setActivityLoading] = useState(true);
  const [dashboardLoading, setDashboardLoading] = useState(true);

  // Data states
  const [feedbackData, setFeedbackData] = useState(null);
  const [activityLog, setActivityLog] = useState([]);
  const [tagPerformance, setTagPerformance] = useState({});
  const [loadErrors, setLoadErrors] = useState({});

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

  const fetchWithTimeout = async (promise, timeoutMs, errorMessage) => {
    let timeoutId;
    
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error(errorMessage || "Request timed out"));
      }, timeoutMs);
    });

    try {
      const result = await Promise.race([promise, timeoutPromise]);
      clearTimeout(timeoutId);
      return result;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  };

  const fetchUserData = async () => {
    // Start with fetching the user profile
    try {
      const res = await fetchWithTimeout(
        fetch(API_PROFILE, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        FETCH_TIMEOUT,
        "Profile data loading timed out"
      );

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
      setProfileLoading(false);

      // Now fetch all other data in parallel
      fetchFeedback(profile.currentUnit);
      fetchTagPerformance();
      fetchDashboardSummary();
      if (profile.currentSubUnit) {
        fetchActivity(profile.currentSubUnit);
      } else {
        setActivityLoading(false);
        setLoadErrors(prev => ({ ...prev, activity: "No current subunit available" }));
      }
    } catch (err) {
      console.error("Failed to fetch user data:", err);
      setProfileLoading(false);
      setLoadErrors(prev => ({ ...prev, profile: err.message }));
    }
  };

  const fetchFeedback = async (unitId) => {
    try {
      const res = await fetchWithTimeout(
        fetch(API_UNIT_FEEDBACK(unitId), {
          headers: { Authorization: `Bearer ${token}` },
        }),
        FETCH_TIMEOUT,
        "Feedback data loading timed out"
      );

      if (!res.ok) {
        if (res.status !== 404) {
          throw new Error(`Error ${res.status}: ${await res.text()}`);
        }
        setLoadErrors(prev => ({ ...prev, feedback: "No feedback available" }));
      } else {
        const result = await res.json();
        setFeedbackData(result);
      }
    } catch (err) {
      console.error("Failed to fetch feedback:", err);
      setLoadErrors(prev => ({ ...prev, feedback: err.message }));
    } finally {
      setFeedbackLoading(false);
    }
  };

  const fetchTagPerformance = async () => {
    try {
      const res = await fetchWithTimeout(
        fetch(API_TAGS, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        FETCH_TIMEOUT,
        "Tag performance data loading timed out"
      );

      if (!res.ok) {
        throw new Error(`Error ${res.status}: ${await res.text()}`);
      }

      const data = await res.json();
      setTagPerformance(data);
    } catch (err) {
      console.error("Failed to fetch tag performance:", err);
      setLoadErrors(prev => ({ ...prev, tags: err.message }));
    } finally {
      setTagsLoading(false);
    }
  };

  const fetchDashboardSummary = async () => {
    try {
      const res = await fetchWithTimeout(
        fetch(API_DASHBOARD, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        FETCH_TIMEOUT,
        "Dashboard summary loading timed out"
      );

      if (!res.ok) {
        throw new Error(`Error ${res.status}: ${await res.text()}`);
      }
      
      // Handle dashboard data as needed
    } catch (err) {
      console.error("Failed to fetch dashboard summary:", err);
      setLoadErrors(prev => ({ ...prev, dashboard: err.message }));
    } finally {
      setDashboardLoading(false);
    }
  };

  const fetchActivity = async (subunitId) => {
    try {
      const res = await fetchWithTimeout(
        fetch(API_HISTORY(subunitId), {
          headers: { Authorization: `Bearer ${token}` },
        }),
        FETCH_TIMEOUT,
        "Activity history loading timed out"
      );

      if (!res.ok) {
        throw new Error(`Error ${res.status}: ${await res.text()}`);
      }

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
      setLoadErrors(prev => ({ ...prev, activity: err.message }));
    } finally {
      setActivityLoading(false);
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
    if (!feedbackData || !feedbackData.levelSuggestion) return;
    
    try {
      const res = await fetch(API_SKILL_UPDATE, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ skillLevel: feedbackData.levelSuggestion }),
      });

      if (!res.ok) {
        console.error("Skill update failed:", await res.text());
        return;
      }

      // Refresh data after successful update
      fetchUserData();
    } catch (err) {
      console.error("Skill update error:", err);
    }
  };

  const prepareTagInsights = () => {
    // Convert tag performance data to format needed for radar chart
    if (!Object.keys(tagPerformance).length) return [];
    
    return Object.keys(tagPerformance).map(tag => ({
      tag,
      score: tagPerformance[tag].percentage || 0
    }));
  };

  const radarData = {
    labels: prepareTagInsights().map(t => t.tag),
    datasets: [
      {
        label: "Progress",
        data: prepareTagInsights().map(t => t.score),
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
      correct += c || 0;
      totalQ += t || 0;
      minutes += parseInt(log.time) || 0;
    });

    const acc = totalQ ? Math.round((correct / totalQ) * 100) : 0;
    return `This week you answered ${totalQ} questions with ${acc}% accuracy over ${minutes}m`;
  };

  // Loading fallback component
  const LoadingFallback = () => (
    <div className="loading-fallback">
      <Loader className="animate-spin" size={24} />
      <p>Loading...</p>
    </div>
  );

  // Error component
  const ErrorMessage = ({ message }) => (
    <div className="error-message">
      <p>{message || "No data available"}</p>
    </div>
  );

  // Only show loading screen for the initial profile data
  if (profileLoading) {
    return <div className="full-page-loading"><LoadingFallback /></div>;
  }

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
          <Suspense fallback={<LoadingFallback />}>
            <Calendar 
              onChange={setDate}
              value={date}
              tileClassName={tileClassName}
            />
          </Suspense>
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
          <Suspense fallback={<LoadingFallback />}>
            <Objectives onPointsEarned={handlePointsUpdate} />
          </Suspense>
        </div>
      </div>

      <div className="cards-container">
        <div className="card">
          <div className="card-header">
            <h3>Activity Log</h3>
            <BookOpen className="card-icon" />
          </div>
          {activityLoading ? (
            <LoadingFallback />
          ) : activityLog.length > 0 ? (
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
            <ErrorMessage message={loadErrors.activity || "No activity yet."} />
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Weekly Stats</h3>
            <Clock className="card-icon" />
          </div>
          {activityLoading ? (
            <LoadingFallback />
          ) : (
            <p>{calcStats()}</p>
          )}
        </div>
      </div>

      <div className="cards-container">
        <div className="card">
          <h3 className="section-title">Progress Chart</h3>
          {tagsLoading ? (
            <LoadingFallback />
          ) : prepareTagInsights().length > 0 ? (
            <Suspense fallback={<LoadingFallback />}>
              <Radar data={radarData} options={radarOptions} />
            </Suspense>
          ) : (
            <ErrorMessage message={loadErrors.tags || "No chart data yet"} />
          )}
        </div>

        <div className="card suggestion-box">
          <div className="card-header">
            <h3>Quick Note</h3>
            <MessageSquare className="card-icon" />
          </div>
          {feedbackLoading ? (
            <LoadingFallback />
          ) : (
            <>
              <p className="note-text">{feedbackData?.aiSummary || "No feedback available yet."}</p>
              {feedbackData?.feedbackPrompt && (
                <p className="suggestion-text">{feedbackData.feedbackPrompt}</p>
              )}
              {feedbackData?.levelSuggestion && (
                <button className="confirm-button" onClick={confirmLevelSuggestion}>
                  Ok!
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;