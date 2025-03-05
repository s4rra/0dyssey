import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from "./components/Dashboard";
import Profile from "./components/Profile";
import Courses from "./components/Courses";
import Missions from "./components/Missions";
import Shop from "./components/Shop";
import Settings from "./components/Settings";
import Page from "./components/Page";
import Questions from "./components/Questions";

// import './assets/fontello/css/fontello.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Page><Dashboard /></Page>} />
          <Route path="/profile" element={<Page><Profile /></Page>} />
          <Route path="/courses" element={<Page><Courses /></Page>} />
          <Route path="/missions" element={<Page><Missions /></Page>} />
          <Route path="/shop" element={<Page><Shop /></Page>} />
          <Route path="/settings" element={<Page><Settings /></Page>} />
          <Route path="/questions" element={<Page><Questions /></Page>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;