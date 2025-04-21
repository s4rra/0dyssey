import React, { lazy, Suspense } from "react";
import { Loader } from "lucide-react";

const Calendar = lazy(() => import("react-calendar"));

const Loading = () => (
  <div className="loading-fallback">
    <Loader className="spin" /> <p>Loading calendar…</p>
  </div>
);

const StreakCalendar = ({ calendarMarks, date, setDate }) => {
  const tileClassName = ({ date }) => {
    if (calendarMarks.includes(date.toDateString())) return "streak-day";
    return null;
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
