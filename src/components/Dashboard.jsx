import "../css/dashboard.css";
function Dashboard() {
  return (
    <main className="main-content">
      <section className="dashboard-content">
        <div className="cards-container">
          <div className="card blank">Daily Goal</div>
          <div className="card blank">Course Progress</div>
          <div className="card blank">Calendar</div>
          <div className="weekly-overview card blank">Weekly Overview</div>
        </div>
      </section>
    </main>
  );
}

export default Dashboard;
