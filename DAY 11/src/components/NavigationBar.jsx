import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

function NavigationBar({ user = null, onLogout }) {
  return (
    <header className="site-header">
      <NavLink className="site-brand" to="/" aria-label="Daybook home">
        <span className="brand-symbol">d.</span>
        <span>daybook</span>
      </NavLink>
      <nav aria-label="Main navigation" className="site-nav-links">
        <NavLink className="site-nav-link" end to="/">Home</NavLink>
        {user ? (
          <>
            <NavLink className="site-nav-link" to="/dashboard">Dashboard</NavLink>
            <NavLink className="site-nav-link" to="/dashboard/add-task">Add task</NavLink>
            <button className="site-nav-link site-nav-button" onClick={onLogout} type="button">Sign out</button>
          </>
        ) : (
          <>
            <NavLink className="site-nav-link" to="/login">Login</NavLink>
            <NavLink className="site-nav-link nav-register" to="/register">Create account</NavLink>
          </>
        )}
      </nav>
    </header>
  )
}

NavigationBar.propTypes = {
  user: PropTypes.shape({ email: PropTypes.string.isRequired }),
  onLogout: PropTypes.func.isRequired,
}

export default NavigationBar