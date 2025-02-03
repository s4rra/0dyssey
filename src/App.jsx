import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from "./components/Dashboard";
import Profile from "./components/Profile";
import Courses from "./components/Courses";
import Missions from "./components/Missions";
import Shop from "./components/Shop";
import Settings from "./components/Settings";
import Page from "./components/Page";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Page><Dashboard /></Page>} />
          <Route path="/Profile" element={<Page><Profile /></Page>} />
          <Route path="/Courses" element={<Page><Courses /></Page>} />
          <Route path="/Missions" element={<Page><Missions /></Page>} />
          <Route path="/Shop" element={<Page><Shop /></Page>} />
          <Route path="/Settings" element={<Page><Settings /></Page>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;