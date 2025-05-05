import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Courses from "./components/Courses";
import Shop from "./components/Shop";
import Bookmarks from "./components/Bookmarks"; //new
import Settings from "./components/Settings";
import Page from "./components/Page";
import Login from "./components/Login";
import Signup from "./components/Signup";
import SubUnit from "./components/Subunit"; //new
import Questions from "./components/Questions";
import MissionList from "./components/MissionList"; // Import MissionList component
import MissionDetail from "./components/MissionDetail"; // Import MissionDetail component

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
                <Route path="/shop" element={<Page><Shop /></Page>} />
                <Route path="/bookmarks" element={<Page><Bookmarks /></Page>} />
                <Route path="/settings" element={<Page><Settings /></Page>} />
                
                {/* Adding routes for missions */}
                <Route path="/missions" element={<Page><MissionList /></Page>} />
                <Route path="/missions/:missionId" element={<Page><MissionDetail /></Page>} />
                <Route path="/missions/unit/:unitId" element={<Page><MissionList /></Page>} />
                <Route path="/missions/unit/:unitId/subunit/:subUnitId" element={<Page><MissionList /></Page>} />
            </Routes>
        </div>
    );
}

export default App;