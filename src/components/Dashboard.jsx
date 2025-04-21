import "../css/dashboard.css";
import {useEffect,useState} from "react";
import { useNavigate } from "react-router-dom";
import ProfilePicture from "./ProfilePicture";
import Insights from "./Insights";
import StreakCalendar from "./Calendar";
import {Loader} from "lucide-react";
import SuggestionBox from "./SuggestionBox";
import RadarChart from "./RadarGraph";


const API_PROFILE        = "http://127.0.0.1:8080/api/user-profile2";
const API_ANALYSE_UNIT   = id => `http://127.0.0.1:8080/api/performance/unit/${id}`;
const API_OBJECTIVES     = unitId => `http://127.0.0.1:8080/api/performance/objectives/${unitId}`;
const API_SKILL_UPDATE   = "http://127.0.0.1:8080/api/performance/skill-level";

const Dashboard = () => {
  const nav = useNavigate();
  const token = localStorage.getItem("token");

  const [user, setUser] = useState(null);
  const [profileLoad, setProfileLoad] = useState(true);
  const [tagInsights, setTagInsights] = useState([]);
  const [unitSummary, setUnitSummary] = useState(null);
  const [lessonStats, setLessonStats] = useState("Loading lesson stats...");
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
        const res = await fetch(API_PROFILE, { headers: { Authorization: `Bearer ${token}` } });
        const profileList = await res.json();
        const p = Array.isArray(profileList) ? profileList[0] : profileList;

        const userInfo = {
          username: p.userName ?? "Student",
          pictureId: p.profilePicture ?? null,
          points: p.points ?? 0,
          unitId: p.currentUnit ?? 1,
          subUnitId: p.currentSubUnit ?? 1,
          streak: p.streakLength ?? 0,
        };
        setUser(userInfo);

        const streakDates = [];
        for (let i = 0; i < userInfo.streak; i++) {
          const d = new Date();
          d.setDate(d.getDate() - i);
          streakDates.push(d.toDateString());
        }
        setCalendarMarks(streakDates);

        await Promise.all([
          analyseLastCompletedUnit(userInfo.unitId),
          fetchLessonStats(userInfo.unitId, userInfo.subUnitId),
          fetchObjectives(userInfo.unitId)
        ]);

        setProfileLoad(false);
      } catch (e) {
        setErrorMsg(e.message);
        setProfileLoad(false);
      }
    })();
  }, []);

  const analyseLastCompletedUnit = async unitId => {
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
          return;
        }
      } catch {}
    }
    setUnitLocked(true);
  };

  const fetchLessonStats = async (unitId) => {
    try {
      const res = await fetch(API_OBJECTIVES(unitId), {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      const summaries = (data?.objectives ?? [])
        .filter(obj => obj.completed && obj.aiSummary)
        .map(obj => `${obj.subUnitName}: ${obj.aiSummary}`);
      
      if (summaries.length) {
        setLessonStats(summaries.join("\n"));
      } else {
        setLessonStats("No recent lesson data.");
      }
    } catch {
      setLessonStats("Unable to load lesson summaries.");
    }
  };
  
  const fetchObjectives = async unitId => {
    try {
      const res = await fetch(API_OBJECTIVES(unitId), {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setObjectives(data?.objectives ?? []);
    } catch {
      setObjectives([]);
    }
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

  const Loading = () => (
    <div className="loading-fallback">
      <Loader className="spin" /> <p>Loading…</p>
    </div>
  );

  if (profileLoad) return <Loading />;

  return (
    <div className="dashboard-page">
      <h2 className="dashboard-heading">Welcome {user.username}!</h2>

      <div className="cards-container">
        <ProfilePicture currentPictureId={user.pictureId} />
        <StreakCalendar calendarMarks={calendarMarks} date={date} setDate={setDate}/>

        <div className="card points-card">
          <h3>Your Points</h3>
          <p className="points-value">{user.points}</p>
        </div>
      </div>

      <div className="cards-container">
        <div className="card">
          <h3 className="section-title">Progress Chart – {unitSummary?.unitName}</h3>
          {unitLocked || !tagInsights.length ? (
            <p>Finish Unit {user.unitId} to unlock your chart.</p>
          ) : (
            <RadarChart tagInsights={tagInsights} />
          )}
        </div>

        <SuggestionBox
          unitId={user.unitId}
          unitSummary={unitSummary}
          unitLocked={unitLocked}
          feedbackHandled={feedbackHandled}
          showPrompt={showPrompt}
          handleLevelOk={handleLevelOk}
          onDismissPrompt={() => {
            setShowPrompt(false);
            setFeedbackHandled(true);
          }}
        />

      </div>

      <Insights
          lessonStats={lessonStats}
          objectives={objectives}
          unitId={user.unitId}
        />
      {errorMsg && <p className="error-text">{errorMsg}</p>}
    </div>
  );
};

export default Dashboard;
