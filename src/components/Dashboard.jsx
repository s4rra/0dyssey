import Page from './Page';

function Dashboard() {
  return (
    <Page>
      <div className="cards-container">
        <div className="card blank">Daily Goal</div>
        <div className="card blank">Course Progress</div>
        <div className="card blank">October 2024</div>
        <div className="weekly-overview card blank">Weekly Overview</div>
      </div>
    </Page>
  );
}

export default Dashboard;