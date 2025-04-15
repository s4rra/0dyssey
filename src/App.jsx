import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Profile from "./components/Profile";
import Courses from "./components/Courses";
import Missions from "./components/Missions";
import Shop from "./components/Shop";
import Bookmarks from "./components/Bookmarks";
import Settings from "./components/Settings";
import Page from "./components/Page";
import Login from "./components/Login";
import Signup from "./components/Signup";
import SubUnit from "./components/Subunit";

function App() {
    return (
        <div className="App">
            <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/dashboard" element={<Page><Dashboard /></Page>} />
                <Route path="/profile" element={<Page><Profile /></Page>} />
                <Route path="/courses" element={<Page><Courses /></Page>}>
                    <Route path="subunit/:subUnitId" element={<SubUnit />} />
                </Route>
                <Route path="/missions" element={<Page><Missions /></Page>} />
                <Route path="/shop" element={<Page><Shop /></Page>} />
                <Route path="/bookmarks" element={<Page><Bookmarks /></Page>} />
                <Route path="/settings" element={<Page><Settings /></Page>} />
                <Route path="/subunit/:subunitId/questions" element={<Page><Questions /></Page>} />

            </Routes>
        </div>
    );
}

export default App;
