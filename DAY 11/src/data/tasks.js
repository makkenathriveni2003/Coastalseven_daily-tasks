export function getLocalDateKey(date = new Date()) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function addDays(date, days) {
  const nextDate = new Date(date)
  nextDate.setDate(nextDate.getDate() + days)
  return getLocalDateKey(nextDate)
}

export function createInitialTasks() {
  const today = new Date()
  const todayKey = getLocalDateKey(today)

  return [
    { id: 'task-1', title: 'Plan the week and set priorities', time: '09:00', priority: 'high', date: todayKey, completed: true },
    { id: 'task-2', title: 'Finish the landing page wireframes', time: '10:30', priority: 'high', date: todayKey, completed: false },
    { id: 'task-3', title: 'Send project notes to the team', time: '13:00', priority: 'normal', date: todayKey, completed: false },
    { id: 'task-4', title: 'Take a proper lunch break', time: '12:00', priority: 'low', date: todayKey, completed: false },
    { id: 'task-5', title: 'Review tomorrow’s meeting notes', time: '09:30', priority: 'normal', date: addDays(today, 1), completed: false },
  ]
}