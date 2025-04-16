import { Link, NavLink } from "react-router-dom";
import PropTypes from "prop-types";
import { useState } from "react";
import "../css/page.css";
import {
  FiMenu,
  FiBook,
  FiTarget,
  FiShoppingCart,
  FiSettings,
  FiHome,
  FiBookmark,
} from "react-icons/fi";

function Page({ children }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-content">
          <button
            className="menu-toggle"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            <FiMenu size={24} />
          </button>
          <Link to="/dashboard" className="logo">
            Odyssey
          </Link>
        </div>
      </header>
      <aside className={`sidebar ${isSidebarOpen ? "open" : "closed"}`}>
        <nav>
          <ul className="sidebar-nav-list">
            <li className="sidebar-item">
              <NavLink
                to="/dashboard"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                <FiHome className="sidebar-icon" />
                <span className="sidebar-text">Home</span>
              </NavLink>
            </li>
            <li className="sidebar-item">
              <NavLink
                to="/courses"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                <FiBook className="sidebar-icon" />
                <span className="sidebar-text">Lessons</span>
              </NavLink>
            </li>
            <li className="sidebar-item">
              <NavLink
                to="/missions"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                <FiTarget className="sidebar-icon" />
                <span className="sidebar-text">Missions</span>
              </NavLink>
            </li>
            <li className="sidebar-item">
              <NavLink
                to="/bookmarks"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                <FiBookmark className="sidebar-icon" />
                <span className="sidebar-text">Bookmarks</span>
              </NavLink>
            </li>
            <li className="sidebar-item">
              <NavLink
                to="/shop"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                <FiShoppingCart className="sidebar-icon" />
                <span className="sidebar-text">Shop</span>
              </NavLink>
            </li>
          </ul>
          <ul className="sidebar-settings-list">
            <li className="sidebar-item">
              <NavLink
                to="/settings"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                <FiSettings className="sidebar-icon" />
                <span className="sidebar-text">Settings</span>
              </NavLink>
            </li>
          </ul>
        </nav>
      </aside>
      <main
        className={`main-content ${isSidebarOpen ? "expanded" : "collapsed"}`}
      >
        <section className="dashboard-content">{children}</section>
      </main>
    </div>
  );
}

Page.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Page;
