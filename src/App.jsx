import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Courses from "./components/Courses";
import Missions from "./components/Missions";
import MissionDetail from "./components/MissionDetail"; // Make sure to import this
import Shop from "./components/Shop";
import Bookmarks from "./components/Bookmarks"; //new
import Settings from "./components/Settings";
import Page from "./components/Page";
import Login from "./components/Login";
import Signup from "./components/Signup";
import SubUnit from "./components/Subunit"; //new
import Questions from "./components/Questions"; 

function App() {
    return (
        <div className="App">
            <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/dashboard" element={<Page><Dashboard /></Page>} />
                <Route path="/courses" element={<Page><Courses /></Page>}>
                    <Route path="subunit/:unitId/:subUnitId" element={<SubUnit />} />
                    <Route path="questions/:unitId/:subunitId" element={<Questions/>} />
                </Route>
                <Route path="/missions" element={<Page><Missions /></Page>} />
                <Route path="/missions/:missionId" element={<Page><MissionDetail /></Page>} />
                <Route path="/shop" element={<Page><Shop /></Page>} />
                <Route path="/bookmarks" element={<Page><Bookmarks /></Page>} />
                <Route path="/settings" element={<Page><Settings /></Page>} />
            </Routes>
        </div>
    );
}

export default App;