import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Profile from "./components/Profile";
import Courses from "./components/Courses";
import Missions from "./components/Missions";
import Shop from "./components/Shop";
import Settings from "./components/Settings";
import Page from "./components/Page";
import Questions from "./components/Questions";

// import './assets/fontello/css/fontello.css';
import Login from "./components/Login";
import Signup from "./components/Signup";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  const [user, setUser] = useState(null); // Store logged-in user state

  const handleLogin = (userData) => {
    setUser(userData);  // Store user data in state
  };

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
          {/* Redirect root path to /login */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* Login and Signup routes (public) */}
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/signup" element={<Signup onSignup={handleLogin} />} />

          {/* Protected routes (require authentication) */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute isAuthenticated={!!user}>
                <Page><Dashboard /></Page>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute isAuthenticated={!!user}>
                <Page><Profile /></Page>
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses"
            element={
              <ProtectedRoute isAuthenticated={!!user}>
                <Page><Courses /></Page>
              </ProtectedRoute>
            }
          />
          <Route
            path="/missions"
            element={
              <ProtectedRoute isAuthenticated={!!user}>
                <Page><Missions /></Page>
              </ProtectedRoute>
            }
          />
          <Route
            path="/shop"
            element={
              <ProtectedRoute isAuthenticated={!!user}>
                <Page><Shop /></Page>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute isAuthenticated={!!user}>
                <Page><Settings /></Page>
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
