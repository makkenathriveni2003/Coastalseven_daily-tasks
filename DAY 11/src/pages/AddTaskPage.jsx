import { useNavigate, useOutletContext } from 'react-router-dom'
import TaskComposer from '../components/TaskComposer.jsx'

function AddTaskPage() {
  const { addTask, error } = useOutletContext()
  const navigate = useNavigate()

  async function handleAddTask(task) {
    const added = await addTask(task)
    if (added) navigate('/dashboard')
    return added
  }

  return (
    <>
      <header className="page-header add-page-header">
        <div>
          <p className="eyebrow">YOUR DAY, IN GOOD ORDER</p>
          <h1>Add a task</h1>
          <p className="date-line">Plan one clear next step.</p>
        </div>
      </header>
      <section className="add-task-content" aria-label="Create a task">
        <TaskComposer onAddTask={handleAddTask} />
        {error && <p className="api-error" role="alert">{error}</p>}
      </section>
      <footer className="page-footer">
        <span>Make room for what matters.</span>
        <span className="footer-mark">DAYBOOK <span> / </span> 01</span>
      </footer>
    </>
  )
}

export default AddTaskPage