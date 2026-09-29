import { Link } from 'react-router-dom'
import { useAuth } from '../auth/useAuth.js'

function HomePage() {
  const { user } = useAuth()

  return (
    <main className="home-page">
      <section className="home-content">
        <p className="eyebrow">A PERSONAL DAILY PLANNER</p>
        <h1>Make room for what matters.</h1>
        <p className="home-description">
          Keep today&apos;s priorities clear, plan what&apos;s next, and track what you&apos;ve finished.
        </p>
        <div className="home-actions">
          <Link className="home-primary-action" to={user ? '/dashboard' : '/login'}>
            {user ? 'Open dashboard' : 'Sign in'}
          </Link>
          {!user && <Link className="home-secondary-action" to="/register">Create an account</Link>}
        </div>
      </section>
      <aside className="home-note" aria-label="Planner overview">
        <span className="note-dot" />
        <p>Today, coming up, completed. One calm place for the whole list.</p>
      </aside>
    </main>
  )
}

export default HomePage