import { useState } from 'react'
import PropTypes from 'prop-types'

function TaskComposer({ onAddTask }) {
  const [title, setTitle] = useState('')
  const [time, setTime] = useState('')
  const [priority, setPriority] = useState('normal')

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmedTitle = title.trim()
    if (!trimmedTitle) return

    const added = await onAddTask({ title: trimmedTitle, time, priority })
    if (added === false) return
    setTitle('')
    setTime('')
    setPriority('normal')
  }

  return (
    <form className="task-composer" onSubmit={handleSubmit}>
      <label className="visually-hidden" htmlFor="new-task">Add a task</label>
      <input
        autoComplete="off"
        id="new-task"
        maxLength={100}
        onChange={(event) => setTitle(event.target.value)}
        placeholder="What needs your attention?"
        value={title}
      />
      <div className="composer-options">
        <label className="time-input-label" htmlFor="task-time">TIME</label>
        <input
          aria-label="Task time"
          className="time-input"
          id="task-time"
          onChange={(event) => setTime(event.target.value)}
          type="time"
          value={time}
        />
        <label className="priority-label" htmlFor="task-priority">PRIORITY</label>
        <select
          aria-label="Task priority"
          id="task-priority"
          onChange={(event) => setPriority(event.target.value)}
          value={priority}
        >
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
        </select>
        <button className="add-task-button" type="submit">Add task <span aria-hidden="true">+</span></button>
      </div>
    </form>
  )
}

TaskComposer.propTypes = {
  onAddTask: PropTypes.func.isRequired,
}

export default TaskComposer