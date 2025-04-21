import "../css/dashboard.css";
import {
  useEffect,
  useState,
  Suspense,
  lazy,
  Fragment
} from "react";
import { useNavigate } from "react-router-dom";
import ProfilePicture from "./ProfilePicture";
import {
  BookOpen,
  Clock,
  MessageSquare,
  Loader,
  X,
} from "lucide-react";

const Calendar = lazy(() => import("react-calendar"));
const Radar = lazy(() =>
  import("react-chartjs-2").then(m => ({ default: m.Radar })),
);

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
  Legend,
);

const API_PROFILE      = "http://127.0.0.1:8080/api/user-profile2";
const API_ANALYSE_UNIT = id => `http://127.0.0.1:8080/api/performance/unit/${id}`;
const API_REF_SUBUNIT  = id => `http://127.0.0.1:8080/api/ref-subunit/${id}`;
const API_ALL_SUBUNITS = unitId => `http://127.0.0.1:8080/api/ref-subunit/all/${unitId}`;
const API_SKILL_UPDATE = "http://127.0.0.1:8080/api/performance/skill-level";

const timeoutFetch = (promise, ms, msg) =>
  new Promise((res, rej) => {
    const id = setTimeout(() => rej(new Error(msg)), ms);
    promise.then(r => { clearTimeout(id); res(r); })
           .catch(e => { clearTimeout(id); rej(e); });
  });

function Dashboard() {
  const nav = useNavigate();
  const token = localStorage.getItem("token");

  const [user, setUser] = useState(null);
  const [profileLoad, setProfileLoad] = useState(true);
  const [loadingUnitPerformance, setLoadingUnitPerformance] = useState(true);
  const [tagInsights, setTagInsights] = useState([]);
  const [unitSummary, setUnitSummary] = useState(null);
  const [lessonStats, setLessonStats] = useState(null);
  const [objectives, setObjectives] = useState([]);
  const [unitLocked, setUnitLocked] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const [updatingLvl, setUpdatingLvl] = useState(false);
  const [feedbackHandled, setFeedbackHandled] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [date, setDate] = useState(new Date());
  const [calendarMarks, setCalendarMarks] = useState([]);

  useEffect(() => {
    if (!token) { nav("/login"); return; }

    (async () => {
      try {
        const res = await timeoutFetch(
          fetch(API_PROFILE, { headers: { Authorization: `Bearer ${token}` } }),
          8000,
          "Profile request timed‑out"
        );
        const profileList = await res.json();
        const p = Array.isArray(profileList) ? profileList[0] : profileList;

        const streakDates = getStreakDates(p.streakLength);
        setCalendarMarks(streakDates);

        setUser({
          username: p.userName ?? "Student",
          pictureId: p.profilePicture ?? null,
          points: p.points ?? 0,
          unitId: p.currentUnit ?? 1,
          subUnitId: p.currentSubUnit ?? 1,
          streak: p.streakLength ?? 0,
        });

        setProfileLoad(false);
        analyseLastCompletedUnit(p.currentUnit);
        getSubunitObjectives(p.currentUnit);
        getLessonStats(p.currentUnit, p.currentSubUnit);

      } catch (e) {
        setErrorMsg(e.message);
        setProfileLoad(false);
      }
    })();
  }, []);

  const getStreakDates = streakLength => {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < streakLength; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() - i);
      dates.push(d.toDateString());
    }
    return dates;
  };

  const tileClassName = ({ date }) => {
    if (calendarMarks.includes(date.toDateString())) return "streak-day";
    if (date.toDateString() === new Date().toDateString()) return "current-streak-day";
    return null;
  };

  const analyseLastCompletedUnit = async unitId => {
    setLoadingUnitPerformance(true);
    for (let i = unitId - 1; i >= 1; i--) {
      try {
        const res = await fetch(API_ANALYSE_UNIT(i), {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        });
        const result = await res.json();
        if (result.success) {
          setTagInsights(result.feedback.tagPerformance ?? []);
          setUnitSummary({
            summary: result.feedback.aiSummary,
            prompt: result.feedback.feedbackPrompt,
            levelSug: result.feedback.levelSuggestion,
            unitName: `Unit ${i}`,
          });
          setUnitLocked(false);
          setShowPrompt(!!result.feedback.feedbackPrompt);
          setLoadingUnitPerformance(false);
          return;
        }
      } catch (e) {
        continue;
      }
    }

    setUnitLocked(true);
    setLoadingUnitPerformance(false);
  };

  const getLessonStats = async (unitId, subUnitId) => {
    try {
      const res = await fetch(`http://127.0.0.1:8080/api/performance/submit/${unitId}/${subUnitId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify([])
      });
      const result = await res.json();
      if (result?.subunitHistory?.length) {
        const stats = result.subunitHistory[0];
        setLessonStats(`In lesson ${subUnitId}, you answered ${stats.correctAnswers} questions over ${Math.round(stats.avgTime)}m`);
      }
    } catch {}
  };

  const getSubunitObjectives = async (unitId) => {
    try {
      const res = await fetch(API_ALL_SUBUNITS(unitId), {
        headers: { Authorization: `Bearer ${token}` }
      });
      const refList = await res.json();
      const allSubunits = refList.subunits ?? [];

      const perfRes = await fetch(`http://127.0.0.1:8080/api/performance/unit/${unitId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });

      const perfData = await perfRes.json();
      const completedIds = perfData?.feedback?.tagPerformance
        ? allSubunits.map(s => s.subUnitID).filter(id => perfData.feedback.tagPerformance[id])
        : [];

      const pending = allSubunits
        .filter(sub => !completedIds.includes(sub.subUnitID))
        .map(sub => sub.subUnitName ?? `Subunit ${sub.subUnitID}`);

      setObjectives(pending);
    } catch {}
  };

  const handleLevelOk = async () => {
    if (updatingLvl) return;
    setUpdatingLvl(true);
    try {
      await fetch(API_SKILL_UPDATE, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ skillLevel: unitSummary.levelSug }),
      });
      setShowPrompt(false);
      setFeedbackHandled(true);
    } catch (e) {
      alert("Level update failed: " + e.message);
    }
    setUpdatingLvl(false);
  };

  const radarData = {
    labels: tagInsights.map(t => t.tag),
    datasets: [{
      label: "Progress",
      data: tagInsights.map(t => t.percentage),
      backgroundColor: "rgba(34,197,94,0.2)",
      borderColor: "rgba(34,197,94,1)",
      borderWidth: 2,
    }],
  };

  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { stepSize: 20, backdropColor: "transparent" }
      }
    },
    plugins: { legend: { display: false } }
  };

  const Loading = () => (
    <div className="loading-fallback">
      <Loader className="spin" /> <p>Loading…</p>
    </div>
  );

  if (profileLoad) return <Loading />;

  return (
    <div className="dashboard-page">
      <h2 className="dashboard-heading">Welcome {user.username}!</h2>

      {/* PROFILE + CALENDAR + POINTS */}
      <div className="cards-container">
        <ProfilePicture currentPictureId={user.pictureId} />
        <Suspense fallback={<Loading />}>
          <Calendar value={date} onChange={setDate} tileClassName={tileClassName} />
        </Suspense>
        <div className="card points-card">
          <h3>Your Points</h3>
          <p className="points-value">{user.points}</p>
          <p className="streak-text">🔥 Streak: {user.streak} day{user.streak === 1 ? '' : 's'}</p>
        </div>
      </div>

      {/* PROGRESS + QUICK NOTE */}
      <div className="cards-container">
        <div className="card">
          <h3 className="section-title">Progress Chart – {unitSummary?.unitName}</h3>
          {loadingUnitPerformance ? (
            <p>Loading your progress…</p>
          ) : unitLocked || !tagInsights.length ? (
            <p>📌 Finish Unit {user.unitId} to unlock your chart.</p>
          ) : (
            <Suspense fallback={<Loading />}><Radar data={radarData} options={radarOptions} /></Suspense>
          )}
        </div>

        <div className="card suggestion-box">
          <div className="card-header">
            <h3>Quick Note</h3><MessageSquare className="card-icon" />
          </div>
          {loadingUnitPerformance ? (
            <p>Loading feedback…</p>
          ) : unitLocked || !unitSummary ? (
            <p>📌 Keep going! Finish Unit {user.unitId} to get feedback.</p>
          ) : feedbackHandled ? (
            <p>🎯 Keep going! Finish Unit {user.unitId} for your next AI review.</p>
          ) : (
            <Fragment>
              <p className="note-text">{unitSummary.summary}</p>
              {showPrompt && (
                <Fragment>
                  <p className="suggestion-text">{unitSummary.prompt}</p>
                  <div className="btn-row">
                    <button className="btn confirm" onClick={handleLevelOk}>OK</button>
                    <button className="btn cancel" onClick={() => {
                      setShowPrompt(false);
                      setFeedbackHandled(true);
                    }}>
                      <X size={14} />
                    </button>
                  </div>
                </Fragment>
              )}
            </Fragment>
          )}
        </div>
      </div>

      {/* LESSON STATS */}
      <div className="cards-container">
        <div className="card">
          <div className="card-header"><h3>Lesson Stats</h3><Clock className="card-icon" /></div>
          <p>{lessonStats ?? "No recent lesson data"}</p>
        </div>
      </div>

      {/* OBJECTIVES */}
      <div className="cards-container">
        <div className="card">
          <div className="card-header"><h3>Objectives</h3><BookOpen className="card-icon" /></div>
          {objectives.length ? (
            <ul className="activity-list">
              {objectives.map((item, idx) => (
                <li key={idx}>📝 {item}</li>
              ))}
            </ul>
          ) : (
            <p>All lessons in Unit {user.unitId} are done 🎉</p>
          )}
        </div>
      </div>

      {errorMsg && <p className="error-text">{errorMsg}</p>}
    </div>
  );
}

export default Dashboard;
