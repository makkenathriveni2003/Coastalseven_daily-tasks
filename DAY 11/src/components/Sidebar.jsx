import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

function Sidebar({ activeView, onViewChange, todayCount, upcomingCount, completedCount, user }) {
  const navigation = [
    { id: 'today', label: 'Today', count: todayCount },
    { id: 'upcoming', label: 'Coming up', count: upcomingCount },
    { id: 'completed', label: 'Completed', count: completedCount },
  ]

  return (
    <aside className="sidebar">
      <Link className="brand" to="/dashboard" aria-label="Daybook dashboard">
        <span className="brand-symbol">d.</span>
        <span>daybook</span>
      </Link>
      <div className="sidebar-rule" />
      <p className="nav-label">WORKSPACE</p>
      <nav className="primary-nav" aria-label="Task views">
        {navigation.map((item) => (
          <button
            aria-current={activeView === item.id ? 'page' : undefined}
            className={activeView === item.id ? 'nav-item active' : 'nav-item'}
            key={item.id}
            onClick={() => onViewChange(item.id)}
            type="button"
          >
            <span>{item.label}</span>
            <span className="nav-count">{item.count}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-note">
        <span className="note-dot" />
        <p>A calmer way to get things done.</p>
      </div>
      <div className="sidebar-bottom">
        <span className="avatar">{user.email.slice(0, 1).toUpperCase()}</span>
        <span className="profile-name" title={user.email}>{user.email}</span>
        <span className="profile-status">PERSONAL</span>
      </div>
    </aside>
  )
}

Sidebar.propTypes = {
  activeView: PropTypes.string.isRequired,
  onViewChange: PropTypes.func.isRequired,
  todayCount: PropTypes.number.isRequired,
  upcomingCount: PropTypes.number.isRequired,
  completedCount: PropTypes.number.isRequired,
  user: PropTypes.shape({ email: PropTypes.string.isRequired }).isRequired,
}

export default Sidebar