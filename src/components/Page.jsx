import { NavLink } from 'react-router-dom';
import PropTypes from 'prop-types';
import "../css/page.css";

function Page({ children }) {
  return (
    <div className="dashboard">
      <aside className="sidebar">
        <h2 className="logo">Odyssey</h2>
        <nav>
          <ul>
            <li>
              <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>Profile</NavLink>
            </li>
            <li>
              <NavLink to="/courses" className={({ isActive }) => isActive ? "active" : ""}>Courses</NavLink>
            </li>
            <li>
              <NavLink to="/" end className={({ isActive }) => isActive ? "active" : ""}>Home</NavLink>
            </li>
            <li>
              <NavLink to="/missions" className={({ isActive }) => isActive ? "active" : ""}>Missions</NavLink>
            </li>
            <li>
              <NavLink to="/shop" className={({ isActive }) => isActive ? "active" : ""}>Shop</NavLink>
            </li>
            <li>
              <NavLink to="/settings" className={({ isActive }) => isActive ? "active" : ""}>Settings</NavLink>
            </li>
          </ul>
        </nav>
      </aside>
      <main className="main-content">
        <header className="header">
          <div className="profile">
            <span>0 ⚡</span>
            <img
              src="https://via.placeholder.com/30"
              alt="profile"
              className="avatar"
            />
          </div>
        </header>
        <section className="dashboard-content">
          {children}
        </section>
      </main>
    </div>
  );
}

Page.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Page;