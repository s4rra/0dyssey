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
          <Route path="/dashboard" element={<Page><Dashboard /></Page>} />
          <Route path="/profile" element={<Page><Profile /></Page>} />
          <Route path="/courses" element={<Page><Courses /></Page>} />
          <Route path="/missions" element={<Page><Missions /></Page>} />
          <Route path="/shop" element={<Page><Shop /></Page>} />
          <Route path="/settings" element={<Page><Settings /></Page>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;