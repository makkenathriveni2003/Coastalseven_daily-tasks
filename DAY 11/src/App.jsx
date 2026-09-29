import { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { Link, Navigate, Outlet, Route, Routes, useLocation, useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { apiClient } from './api/client.js'
import { useAuth } from './auth/useAuth.js'
import NavigationBar from './components/NavigationBar.jsx'
import Sidebar from './components/Sidebar.jsx'
import TaskComposer from './components/TaskComposer.jsx'
import TaskList from './components/TaskList.jsx'
import AddTaskPage from './pages/AddTaskPage.jsx'
import HomePage from './pages/HomePage.jsx'
import { getLocalDateKey } from './data/tasks.js'
import './App.css'

function ProtectedRoute() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <div className="app-loading" role="status">Checking your session...</div>
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  return <Outlet />
}

function AuthPage({ mode }) {
  const isRegister = mode === 'register'
  const { user, isLoading, authenticate } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isLoading) return <div className="app-loading" role="status">Checking your session...</div>
  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await authenticate(mode, { email, password })
      const requestedPath = location.state?.from?.pathname
      const returnPath = requestedPath === '/dashboard'
        || requestedPath === '/dashboard/add-task'
        || /^\/dashboard\/tasks\/[a-f\d-]+$/i.test(requestedPath)
        ? requestedPath
        : '/dashboard'
      navigate(returnPath, { replace: true })
    } catch (requestError) {
      const detail = requestError.response?.data?.detail
      setError(Array.isArray(detail) ? detail.map((item) => item.msg).join(' ') : detail || 'Could not connect to the server.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">YOUR DAY, IN GOOD ORDER</p>
        <h1>{isRegister ? 'Make space.' : 'Welcome back.'}</h1>
        <p className="auth-intro">
          {isRegister ? 'Create an account to keep your tasks in sync.' : 'Sign in to pick up where you left off.'}
        </p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label htmlFor="auth-email">Email</label>
          <input
            autoComplete="email"
            autoFocus
            id="auth-email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
          <label htmlFor="auth-password">Password</label>
          <input
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            id="auth-password"
            minLength={isRegister ? 8 : undefined}
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button className="auth-submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? 'Please wait...' : isRegister ? 'Create account' : 'Sign in'}
          </button>
        </form>
        <p className="auth-switch">
          {isRegister ? 'Already have an account?' : 'New to daybook?'}{' '}
          <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Create an account'}</Link>
        </p>
      </section>
    </main>
  )
}

AuthPage.propTypes = {
  mode: PropTypes.oneOf(['login', 'register']).isRequired,
}

function PlannerLayout() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tasks, setTasks] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeView, setActiveView] = useState('today')
  const [statusFilter, setStatusFilter] = useState('all')
  const today = getLocalDateKey()
  const todayTasks = tasks.filter((task) => task.date === today)

  useEffect(() => {
    let isActive = true
    apiClient.get('/tasks')
      .then(({ data }) => {
        if (isActive) setTasks(data)
      })
      .catch(() => {
        if (isActive) setError('Tasks could not be loaded. Check that the API server is running.')
      })
      .finally(() => {
        if (isActive) setIsLoading(false)
      })
    return () => { isActive = false }
  }, [])

  async function addTask(taskDetails) {
    try {
      const { data } = await apiClient.post('/tasks', { ...taskDetails, date: today })
      setTasks((currentTasks) => [data, ...currentTasks])
      setError('')
      return true
    } catch {
      setError('That task could not be saved. Please try again.')
      return false
    }
  }

  async function toggleTask(taskId) {
    const task = tasks.find((item) => item.id === taskId)
    if (!task) return
    try {
      const { data } = await apiClient.patch(`/tasks/${taskId}`, { completed: !task.completed })
      setTasks((currentTasks) => currentTasks.map((item) => item.id === taskId ? data : item))
      setError('')
    } catch {
      setError('That task could not be updated. Please try again.')
    }
  }

  async function removeTask(taskId) {
    try {
      await apiClient.delete(`/tasks/${taskId}`)
      setTasks((currentTasks) => currentTasks.filter((task) => task.id !== taskId))
      setError('')
      return true
    } catch {
      setError('That task could not be removed. Please try again.')
      return false
    }
  }

  function changeView(view) {
    setActiveView(view)
    setStatusFilter('all')
    navigate('/dashboard')
  }

  return (
    <div className="app-shell">
      <Sidebar
        activeView={activeView}
        onViewChange={changeView}
        todayCount={todayTasks.filter((task) => !task.completed).length}
        upcomingCount={tasks.filter((task) => task.date > today && !task.completed).length}
        completedCount={tasks.filter((task) => task.completed).length}
        user={user}
      />
      <main className="main-panel">
        <Outlet context={{
          tasks, isLoading, error, activeView, statusFilter, setStatusFilter,
          addTask, toggleTask, removeTask, setError,
        }} />
      </main>
    </div>
  )
}

function PlannerDashboard() {
  const { tasks, isLoading, error, activeView, statusFilter, setStatusFilter, addTask, toggleTask, removeTask } = useOutletContext()
  const today = getLocalDateKey()
  const todayTasks = tasks.filter((task) => task.date === today)
  const completedToday = todayTasks.filter((task) => task.completed).length
  const viewTitles = { today: 'Today', upcoming: 'Coming up', completed: 'Completed' }
  const visibleTasks = tasks.filter((task) => {
    if (activeView === 'today' && task.date !== today) return false
    if (activeView === 'upcoming' && task.date <= today) return false
    if (activeView === 'completed' && !task.completed) return false
    if (statusFilter === 'open' && task.completed) return false
    if (statusFilter === 'done' && !task.completed) return false
    return true
  })

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">YOUR DAY, IN GOOD ORDER</p>
          <h1>{viewTitles[activeView]}</h1>
          <p className="date-line">
            {new Intl.DateTimeFormat('en', {
              weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
            }).format(new Date())}
          </p>
        </div>
        <div className="day-progress" aria-label={`${completedToday} of ${todayTasks.length} tasks complete`}>
          <span className="progress-number">{String(completedToday).padStart(2, '0')}</span>
          <span className="progress-divider">/</span>
          <span className="progress-total">{String(todayTasks.length).padStart(2, '0')}</span>
          <span className="progress-caption">done today</span>
        </div>
      </header>

      <section className="planner-content" aria-label={`${viewTitles[activeView]} tasks`}>
        <TaskComposer onAddTask={addTask} />
        {error && <p className="api-error" role="alert">{error}</p>}
        <div className="list-toolbar">
          <div>
            <h2>{activeView === 'today' ? 'Your list' : viewTitles[activeView]}</h2>
            <span className="task-count">{visibleTasks.length} {visibleTasks.length === 1 ? 'task' : 'tasks'}</span>
          </div>
          <div className="filter-control" role="group" aria-label="Filter tasks">
            {['all', 'open', 'done'].map((filter) => (
              <button
                className={statusFilter === filter ? 'filter-button active' : 'filter-button'}
                key={filter}
                onClick={() => setStatusFilter(filter)}
                type="button"
              >
                {filter === 'all' ? 'All' : filter === 'open' ? 'To do' : 'Done'}
              </button>
            ))}
          </div>
        </div>
        {isLoading
          ? <p className="list-loading" role="status">Loading tasks...</p>
          : <TaskList tasks={visibleTasks} onToggle={toggleTask} onRemove={removeTask} />}
      </section>
      <footer className="page-footer">
        <span>Make room for what matters.</span>
        <span className="footer-mark">DAYBOOK <span> / </span> 01</span>
      </footer>
    </>
  )
}

function TaskDetailPage() {
  const { taskId } = useParams()
  const navigate = useNavigate()
  const { tasks, isLoading, error, toggleTask, removeTask, setError } = useOutletContext()
  const [routeTask, setRouteTask] = useState(null)
  const [isDetailLoading, setIsDetailLoading] = useState(true)

  useEffect(() => {
    let isActive = true
    setIsDetailLoading(true)
    apiClient.get(`/tasks/${taskId}`)
      .then(({ data }) => {
        if (isActive) setRouteTask(data)
      })
      .catch(() => {
        if (isActive) setRouteTask(null)
      })
      .finally(() => {
        if (isActive) setIsDetailLoading(false)
      })
    return () => { isActive = false }
  }, [taskId])

  const task = tasks.find((item) => item.id === taskId)
    || (routeTask?.id === taskId ? routeTask : null)

  if (isLoading || isDetailLoading) return <p className="list-loading" role="status">Loading task...</p>
  if (!task) return <Navigate to="/" replace />

  async function handleRemove() {
    if (await removeTask(task.id)) navigate('/dashboard', { replace: true })
  }

  return (
    <>
      <header className="page-header detail-header">
        <div>
          <p className="eyebrow">TASK DETAILS</p>
          <h1>One thing at a time.</h1>
          <p className="date-line">{task.date}</p>
        </div>
        <button className="detail-back" onClick={() => navigate('/dashboard')} type="button">Back to list</button>
      </header>
      <section className="task-detail">
        {error && <p className="api-error" role="alert">{error}</p>}
        <div className="detail-title-row">
          <button
            aria-label={task.completed ? 'Mark task as to do' : 'Complete task'}
            aria-pressed={task.completed}
            className={task.completed ? 'task-check is-checked' : 'task-check'}
            onClick={() => { setError(''); toggleTask(task.id) }}
            type="button"
          >
            {task.completed && <span aria-hidden="true">&#10003;</span>}
          </button>
          <h2>{task.title}</h2>
        </div>
        <dl className="detail-meta">
          <div><dt>Date</dt><dd>{task.date}</dd></div>
          <div><dt>Time</dt><dd>{task.time || 'Anytime'}</dd></div>
          <div><dt>Priority</dt><dd className={`priority-value ${task.priority}`}>{task.priority}</dd></div>
          <div><dt>Status</dt><dd>{task.completed ? 'Completed' : 'To do'}</dd></div>
        </dl>
        <button className="detail-remove" onClick={handleRemove} type="button">Remove task</button>
      </section>
      <footer className="page-footer">
        <span>Make room for what matters.</span>
        <span className="footer-mark">DAYBOOK <span> / </span> 01</span>
      </footer>
    </>
  )
}

function App() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    signOut()
    navigate('/login', { replace: true })
  }

  return (
    <>
      <NavigationBar onLogout={handleLogout} user={user} />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<PlannerLayout />}>
            <Route index element={<PlannerDashboard />} />
            <Route path="add-task" element={<AddTaskPage />} />
            <Route path="tasks/:taskId" element={<TaskDetailPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
