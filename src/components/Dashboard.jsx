import "../css/dashboard.css";
import {useEffect,useState} from "react";
import { useNavigate } from "react-router-dom";
import ProfilePicture from "./ProfilePicture";
import Insights from "./Insights";
import StreakCalendar from "./Calendar";
import {Loader} from "lucide-react";
import SuggestionBox from "./SuggestionBox";
import RadarChart from "./RadarGraph";

const API_PROFILE = "http://127.0.0.1:8080/api/user-profile";
const Dashboard = () => {
  const nav = useNavigate();
  const token = localStorage.getItem("token");

  const [user, setUser] = useState(null);
  const [profileLoad, setProfileLoad] = useState(true);
  const [tagInsights, setTagInsights] = useState([]);
  const [chartUnitLabel, setChartUnitLabel] = useState("");
  const [errorMsg, setErrorMsg] = useState(null);

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
          hints: p.hints ?? 0,
          unitId: p.currentUnit ?? 1,
          subUnitId: p.currentSubUnit ?? 1,
        };
        setUser(userInfo);

        setProfileLoad(false);
      } catch (e) {
        setErrorMsg(e.message);
        setProfileLoad(false);
      }
    })();
  }, []);

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
        {/* Left column with profile, calendar, and suggestion box stacked vertically */}
        <div className="profile-calendar-column">
          <div className="profile-card">
            <ProfilePicture userPoints={user.points} userHints={user.hints} />
          </div>
          <div className="calendar-card card">
            <StreakCalendar />
          </div>
          {/* SuggestionBox directly below calendar with reduced margins */}
          <div className="suggestion-card reduced-margin">
            <SuggestionBox
              unitId={user.unitId}
              onFeedback={({ tagInsights, unitLabel }) => {
                setTagInsights(tagInsights);
                setChartUnitLabel(unitLabel);
              }}
            />
          </div>
        </div>

        {/* Combined Progress Chart and Insights Card */}
        <div className="card objectives-card">
          {/* Progress Chart Section */}
          <div className="chart-section">
            <h3 className="section-title">
              {tagInsights.length ? `Progress Chart – ${chartUnitLabel}` : "Progress Chart"}
            </h3>

            {!tagInsights.length ? (
              <div className="loading-fallback">
                <p>Complete a unit to see your progress</p>
              </div>
            ) : (
              <RadarChart tagInsights={tagInsights} />
            )}
          </div>
          
          {/* Divider between chart and insights */}
          <div className="section-divider"></div>
          
          {/* Insights Section */}
          <div className="insights-section">
            <h3 className="section-title">Insights</h3>
            <Insights unitId={user.unitId} />
          </div>
        </div>
      </div>
      
      {errorMsg && <p className="error-text">{errorMsg}</p>}
    </div>
  );
};

export default Dashboard;