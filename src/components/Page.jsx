import { Link, NavLink } from "react-router-dom";
import PropTypes from "prop-types";
import "../css/page.css";


function Page({ children }) {
  return (
    <div className="dashboard">
      <aside className="sidebar">
        <Link to="/" className="logo">
          Odyssey
        </Link>
        <nav>
          <ul>
            <li>
              <NavLink
                to="/courses"
                className={({ isActive }) => (isActive ? "active" : "")}
                style={{ textDecoration: "none" }}
              >
                 {/* <i className="icon-book"></i> */}
                  Courses
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/missions"
                className={({ isActive }) => (isActive ? "active" : "")}
                style={{ textDecoration: "none" }}
              >
                Missions
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/shop"
                className={({ isActive }) => (isActive ? "active" : "")}
                style={{ textDecoration: "none" }}
              >
                Shop
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/settings"
                className={({ isActive }) => (isActive ? "active" : "")}
                style={{ textDecoration: "none" }}
              >
                Settings
              </NavLink>
            </li>
          </ul>
        </nav>
      </aside>
      <main className="main-content">
        <header className="header">
          {/* <NavLink to="/" className="logo">
            Odyssey
          </NavLink> */}
          <div>
            <span>0⚡</span>
            <NavLink
              to="/profile"
              className={({ isActive }) => (isActive ? "active" : "")}
              style={{ textDecoration: "none" }}
            >
              Profile
            </NavLink>
          </div>
        </header>
        <section className="dashboard-content">{children}</section>
      </main>
    </div>
  );
}

Page.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Page;
