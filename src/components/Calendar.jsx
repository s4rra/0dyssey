import { useState, useEffect, lazy, Suspense } from "react";
import "../css/calendar.css";
import { Loader } from "lucide-react";
const Calendar = lazy(() => import("react-calendar"));

const Loading = () => (
  <div className="loading-fallback">
    <Loader className="spin" /> <p>Loading calendar…</p>
  </div>
);

const StreakCalendar = () => {
  const [date, setDate] = useState(new Date());
  const [calendarMarks, setCalendarMarks] = useState([]);
  const [lastLogin, setLastLogin] = useState(null);
  const [streakLength, setStreakLength] = useState(0);

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const res = await fetch("http://127.0.0.1:8080/api/user-profile2", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        const user = Array.isArray(data) ? data[0] : data;

        const streak = user.streakLength ?? 0;
        const last = user.lastLogin ? new Date(user.lastLogin) : null;
        setStreakLength(streak);
        setLastLogin(last);

        if (streak && last) {
          const marks = [];
          for (let i = 0; i < streak; i++) {
            const d = new Date(last);
            d.setDate(d.getDate() - i);
            marks.push(d.toDateString());
          }
          setCalendarMarks(marks);
        }
      } catch (err) {
        console.error("Failed to fetch user streak:", err);
      }
    };

    fetchUserData();
  }, []);

  const isStreakDay = (date) => {
    if (!lastLogin) return false;

    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);

    const startDate = new Date(lastLogin);
    startDate.setHours(0, 0, 0, 0);
    startDate.setDate(startDate.getDate() - (streakLength - 1));

    return checkDate >= startDate && checkDate <= new Date(lastLogin);
  };

  const tileClassName = ({ date, view }) => {
    if (view !== "month") return "";

    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);

    if (!lastLogin) return "";

    const isCurrent = checkDate.getTime() === new Date(lastLogin).setHours(0, 0, 0, 0);

    if (isStreakDay(date)) {
      return isCurrent ? "streak-day current-streak-day" : "streak-day";
    }

    return "";
  };

  return (
    <Suspense fallback={<Loading />}>
      <Calendar
        value={date}
        onChange={setDate}
        tileClassName={tileClassName}
      />
    </Suspense>
  );
};

export default StreakCalendar;
