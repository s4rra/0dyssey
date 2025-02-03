import { NavLink } from 'react-router-dom';
import PropTypes from 'prop-types';
import "../css/page.css";

function Page({ children }) {
  return (
    <div className="dashboard">
      <aside className="sidebar">
        <NavLink to="/" className="logo">
          Odyssey
        </NavLink>
        <nav>
          <ul>
            <li>
              <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>Profile</NavLink>
            </li>
            <li>
              <NavLink to="/courses" className={({ isActive }) => isActive ? "active" : ""}>Courses</NavLink>
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
      {children}
    </div>
  );
}

Page.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Page;