/* Dashboard.jsx  –– no inline CSS */

import "../css/dashboard.css";
import {
  useEffect,
  useState,
  Suspense,
  lazy,
  Fragment,
} from "react";
import { useNavigate } from "react-router-dom";
import ProfilePicture from "./ProfilePicture";
import {
  BookOpen,
  Clock,
  MessageSquare,
  ListChecks,
  Loader,
  X,
} from "lucide-react";

/* lazy‑loaded pieces */
const Calendar   = lazy(() => import("react-calendar"));
const Objectives = lazy(() => import("./Objectives"));
const Radar      = lazy(() =>
  import("react-chartjs-2").then(m => ({ default: m.Radar })),
);

/* chart.js deps */
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

/* API constants */
const API_PROFILE      = "http://127.0.0.1:8080/api/user-profile2";
const API_ANALYSE_UNIT = id => `http://127.0.0.1:8080/api/performance/unit/${id}`;
const API_SKILL_UPDATE = "http://127.0.0.1:8080/api/performance/skill-level";

/* helper for time‑out fetch */
const timeoutFetch = (promise, ms, msg) =>
  new Promise((res, rej) => {
    const id = setTimeout(() => rej(new Error(msg)), ms);
    promise.then(r => { clearTimeout(id); res(r); })
           .catch(e => { clearTimeout(id); rej(e); });
  });

function Dashboard() {
  const nav   = useNavigate();
  const token = localStorage.getItem("token");

  /* STATE */
  const [user,         setUser]         = useState(null);
  const [profileLoad,  setProfileLoad]  = useState(true);
  const [tagInsights,  setTagInsights]  = useState([]);
  const [unitSummary,  setUnitSummary]  = useState(null);
  const [lessonStats,  setLessonStats]  = useState(null);
  const [showPrompt,   setShowPrompt]   = useState(false);
  const [updatingLvl,  setUpdatingLvl]  = useState(false);
  const [errorMsg,     setErrorMsg]     = useState(null);
  const [date,         setDate]         = useState(new Date());

  /* ───────── load profile → then analyse unit */
  useEffect(() => {
    if (!token) { nav("/login"); return; }
    (async () => {
      try {
        const res = await timeoutFetch(
          fetch(API_PROFILE, { headers: { Authorization:`Bearer ${token}` }}),
          8000,
          "Profile request timed‑out"
        );
        const p = await res.json();
        setUser({
          username:  p.userName       ?? "Student",
          pictureId: p.profilePicture ?? null,
          points:    p.points         ?? 0,
          unitId:    p.currentUnit    ?? 1,
        });
        setProfileLoad(false);
        analyseUnit(p.currentUnit ?? 1);
      } catch (e) { setErrorMsg(e.message); setProfileLoad(false); }
    })();
  }, []);

  /* ───────── analyse unit */
  const analyseUnit = async unitId => {
    try {
      const res = await timeoutFetch(
        fetch(API_ANALYSE_UNIT(unitId), {
          method:"POST",
          headers:{ Authorization:`Bearer ${token}` },
        }),
        8000,
        "Analyse unit timed‑out"
      );
      const { feedback, subunitFeedback } = await res.json();
      setTagInsights(feedback.tagPerformance ?? feedback.tagInsights ?? []);
      setUnitSummary({
        summary:  feedback.aiSummary,
        prompt:   feedback.feedbackPrompt,
        levelSug: feedback.levelSuggestion,
      });
      setShowPrompt(!!feedback.feedbackPrompt);
      if (subunitFeedback?.length)
        setLessonStats(subunitFeedback[0].text ?? subunitFeedback[0].aiSummary);
    } catch (e) { setErrorMsg(e.message); }
  };

  /* ───────── chart data */
  const radarData = {
    labels: tagInsights.map(t => t.tag),
    datasets: [{
      label: "Progress",
      data: tagInsights.map(t => t.percentage),
      backgroundColor: "rgba(34,197,94,0.2)",
      borderColor:     "rgba(34,197,94,1)",
      borderWidth: 2,
    }],
  };
  const radarOptions = {
    scales:{ r:{ min:0,max:100,
      ticks:{ stepSize:20,backdropColor:"transparent" } } },
    plugins:{ legend:{ display:false }}
  };

  /* ───────── accept level change */
  const handleLevelOk = async () => {
    if (updatingLvl) return;
    setUpdatingLvl(true);
    try {
      await fetch(API_SKILL_UPDATE, {
        method:"POST",
        headers:{
          Authorization:`Bearer ${token}`,
          "Content-Type":"application/json",
        },
        body: JSON.stringify({ skillLevel: unitSummary.levelSug }),
      });
      setShowPrompt(false);
      alert("Skill level updated successfully!");
    } catch (e) { alert("Level update failed: " + e.message); }
    setUpdatingLvl(false);
  };

  /* ───────── loading component */
  const Loading = () => (
    <div className="loading-fallback">
      <Loader className="spin" /> <p>Loading…</p>
    </div>
  );
  if (profileLoad) return <Loading />;

  return (
    <div className="dashboard-page">
      <h2 className="dashboard-heading">Welcome {user.username}!</h2>

      {/* TOP ROW */}
      <div className="cards-container">
        <ProfilePicture currentPictureId={user.pictureId} />
        <Suspense fallback={<Loading />}><Calendar value={date} onChange={setDate}/></Suspense>
        <div className="card points-card">
          <h3>Your Points</h3><p className="points-value">{user.points}</p>
        </div>
      </div>

      {/* PROGRESS & QUICK NOTE */}
      <div className="cards-container">
        <div className="card">
          <h3 className="section-title">Progress Chart</h3>
          {tagInsights.length
            ? <Suspense fallback={<Loading />}><Radar data={radarData} options={radarOptions}/></Suspense>
            : <p>No data yet</p>}
        </div>

        <div className="card suggestion-box">
          <div className="card-header">
            <h3>Quick Note</h3><MessageSquare className="card-icon"/>
          </div>
          {unitSummary
            ? <Fragment>
                <p className="note-text">{unitSummary.summary}</p>
                {showPrompt &&
                  <Fragment>
                    <p className="suggestion-text">{unitSummary.prompt}</p>
                    <div className="btn-row">
                      <button className="btn confirm" onClick={handleLevelOk}>OK</button>
                      <button className="btn cancel"  onClick={()=>setShowPrompt(false)}><X size={14}/></button>
                    </div>
                  </Fragment>}
              </Fragment>
            : <p>No feedback yet</p>}
        </div>
      </div>

      {/* LESSON STATS */}
      <div className="cards-container">
        <div className="card">
          <div className="card-header"><h3>Lesson Stats</h3><Clock className="card-icon"/></div>
          <p>{lessonStats ?? "No recent lesson data"}</p>
        </div>
      </div>

      {/* OBJECTIVES 
      <div className="cards-container">
        <div className="card objectives-card">
          <div className="card-header"><h3>Objectives</h3><ListChecks className="card-icon"/></div>
          <Suspense fallback={<Loading />}><Objectives/></Suspense>
        </div>
      </div>*/}

      {/* ACTIVITY PLACEHOLDER */}
      <div className="cards-container">
        <div className="card">
          <div className="card-header"><h3>Activity Log</h3><BookOpen className="card-icon"/></div>
          <p>Coming soon …</p>
        </div>
      </div>

      {errorMsg && <p className="error-text">{errorMsg}</p>}
    </div>
  );
}

export default Dashboard;
