import "../css/dashboard.css";
import "../css/calendar.css";
import Calendar from "react-calendar";
import { useState } from "react";

function Dashboard() {
  const [date, setDate] = useState(new Date());

  return (
    <main className="main-content">
      <section className="dashboard-content">
        <div className="cards-container">
          <div className="card calendar-card">
            <Calendar onChange={setDate} value={date} />
          </div>
        </div>
      </section>
    </main>
  );
}

export default Dashboard;
