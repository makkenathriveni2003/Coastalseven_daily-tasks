import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

function formatTime(time) {
  if (!time) return 'Anytime'
  const [hours, minutes] = time.split(':').map(Number)
  return new Intl.DateTimeFormat('en', {
    hour: 'numeric', minute: '2-digit',
  }).format(new Date(2000, 0, 1, hours, minutes))
}

function TaskList({ tasks, onToggle, onRemove }) {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-mark" aria-hidden="true">+</span>
        <h3>Nothing on this list.</h3>
        <p>Add a task above and give your day a little shape.</p>
      </div>
    )
  }

  return (
    <ul className="task-list">
      {tasks
        .slice()
        .sort((first, second) => (first.time || '99:99').localeCompare(second.time || '99:99'))
        .map((task) => (
          <li className={task.completed ? 'task-row completed' : 'task-row'} key={task.id}>
            <button
              aria-label={task.completed ? `Mark ${task.title} as to do` : `Complete ${task.title}`}
              aria-pressed={task.completed}
              className="task-check"
              onClick={() => onToggle(task.id)}
              type="button"
            >
              {task.completed && <span aria-hidden="true">&#10003;</span>}
            </button>
            <div className="task-main">
              <p className="task-title"><Link to={`/dashboard/tasks/${task.id}`}>{task.title}</Link></p>
              <div className="task-meta">
                <span>{formatTime(task.time)}</span>
                {task.date && <span>{task.date}</span>}
              </div>
            </div>
            <span className={`priority-dot ${task.priority}`} title={`${task.priority} priority`} />
            <span className={`priority-text ${task.priority}`}>{task.priority}</span>
            <button className="remove-task" onClick={() => onRemove(task.id)} type="button">
              Remove
            </button>
          </li>
        ))}
    </ul>
  )
}

TaskList.propTypes = {
  tasks: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    time: PropTypes.string,
    priority: PropTypes.oneOf(['low', 'normal', 'high']).isRequired,
    date: PropTypes.string.isRequired,
    completed: PropTypes.bool.isRequired,
  })).isRequired,
  onToggle: PropTypes.func.isRequired,
  onRemove: PropTypes.func.isRequired,
}

export default TaskList