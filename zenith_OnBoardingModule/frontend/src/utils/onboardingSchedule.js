// Oct 12, 2026 is a working day for onboarding even if imported as a holiday.
const onboardingWorkingDayOverrides = new Set(['2026-10-12'])
const onboardingNextDayCutoffHour = 14

function dateKey(day) {
  return [
    day.getFullYear(),
    String(day.getMonth() + 1).padStart(2, '0'),
    String(day.getDate()).padStart(2, '0')
  ].join('-')
}

function isWorkingDay(day, holidayDatesByYear) {
  const holidayDates = holidayDatesByYear[day.getFullYear()] || new Set()
  const key = dateKey(day)
  return ![0, 6].includes(day.getDay()) &&
    (!holidayDates.has(key) || onboardingWorkingDayOverrides.has(key))
}

function nextWorkingDay(day, holidayDatesByYear) {
  const nextDate = new Date(day)
  nextDate.setDate(nextDate.getDate() + 1)
  while (!isWorkingDay(nextDate, holidayDatesByYear)) {
    nextDate.setDate(nextDate.getDate() + 1)
  }
  return nextDate
}

export function getOnboardingDaySchedule(completionTime, holidayDatesByYear = {}) {
  const startDate = new Date(completionTime)
  if (completionTime.getHours() >= onboardingNextDayCutoffHour) {
    startDate.setDate(startDate.getDate() + 1)
  }
  startDate.setHours(0, 0, 0, 0)

  while (!isWorkingDay(startDate, holidayDatesByYear)) {
    startDate.setDate(startDate.getDate() + 1)
  }

  const schedule = [startDate]
  for (let dayNumber = 2; dayNumber <= 5; dayNumber += 1) {
    schedule.push(nextWorkingDay(schedule[dayNumber - 2], holidayDatesByYear))
  }
  return schedule
}

export function getWorkingDayDeadline(dateValue, daysAfter, holidayDatesByYear = {}) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateValue || '')) {
    return null
  }

  const date = new Date(`${dateValue}T00:00:00`)
  const [year, month, day] = dateValue.split('-').map(Number)
  if (
    !Number.isFinite(date.getTime()) ||
    date.getFullYear() !== year ||
    date.getMonth() + 1 !== month ||
    date.getDate() !== day ||
    !Number.isInteger(daysAfter) ||
    daysAfter < 0
  ) {
    return null
  }

  let workingDaysAdded = 0
  while (workingDaysAdded < daysAfter) {
    date.setDate(date.getDate() + 1)
    if (isWorkingDay(date, holidayDatesByYear)) {
      workingDaysAdded += 1
    }
  }
  date.setHours(23, 59, 59, 999)
  return date
}

export function isVdiActivationActivityRow(row) {
  const normalizedDay = String(row?.day || '')
    .trim()
    .toLowerCase()
    .replace(/[\s_-]+/g, '')
  if (normalizedDay === 'vdiactivation') {
    return true
  }

  const activity = String(row?.activity || '').trim().toLowerCase()
  const action = String(row?.action || row?.relevantLink || '').trim().toLowerCase()
  return normalizedDay === 'week0' && activity === 'client vdi' && action === 'vdi activation'
}

export function getPhaseActivityRows(rows, dayNumber) {
  const targetDay = `day${dayNumber}`
  return (Array.isArray(rows) ? rows : []).filter((row) => {
    const normalizedDay = String(row?.day || '')
      .trim()
      .toLowerCase()
      .replace(/[\s_-]+/g, '')
    return normalizedDay === targetDay || normalizedDay === `${targetDay}a`
  })
}

export function isCompletedActivityStatus(status) {
  return ['completed', 'complete', 'not applicable', 'not_applicable', 'n/a']
    .includes(String(status || '').trim().toLowerCase())
}

export function getPhaseCompletionTimestamp(rows) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return null
  }

  const completedRows = rows.filter((row) => isCompletedActivityStatus(row?.status))
  if (completedRows.length !== rows.length) {
    return null
  }

  const completionTimes = completedRows
    .map((row) => {
      const value = row?.completedAt
      if (!value) return null

      const timestamp = new Date(value)
      return Number.isNaN(timestamp.getTime()) ? null : timestamp
    })
    .filter((timestamp) => timestamp !== null)
  if (completionTimes.length === 0) {
    return null
  }

  return completionTimes.reduce((latest, current) => (
    current.getTime() > latest.getTime() ? current : latest
  ))
}

export function getSameDayDeadline(dateValue) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateValue || '')) {
    return null
  }

  const [year, month, day] = dateValue.split('-').map(Number)
  const deadline = new Date(year, month - 1, day, 23, 59, 59, 999)
  if (
    Number.isNaN(deadline.getTime()) ||
    deadline.getFullYear() !== year ||
    deadline.getMonth() + 1 !== month ||
    deadline.getDate() !== day
  ) {
    return null
  }
  return deadline
}

export function getSameDaySlaStatus(deadline, nowTimestamp, completedAt = null, isCompleted = false) {
  const deadlineTimestamp = deadline?.getTime()
  if (!Number.isFinite(deadlineTimestamp)) {
    return null
  }
  if (isCompleted && !completedAt) {
    return { label: 'Completed', isOverdue: false }
  }

  const referenceTimestamp = completedAt
    ? new Date(completedAt).getTime()
    : nowTimestamp
  if (!Number.isFinite(referenceTimestamp)) {
    return null
  }

  const difference = deadlineTimestamp - referenceTimestamp
  if (completedAt && difference >= 0) {
    return { label: 'Completed on time', isOverdue: false }
  }

  const totalMinutes = Math.floor(Math.abs(difference) / 60000)
  const days = Math.floor(totalMinutes / (24 * 60))
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60)
  const minutes = totalMinutes % 60
  const duration = [
    days ? `${days}d` : '',
    hours ? `${hours}h` : '',
    minutes || (!days && !hours) ? `${minutes}m` : ''
  ].filter(Boolean).join(' ')
  const isOverdue = difference < 0

  return {
    label: isOverdue ? `Overdue by ${duration}` : `${duration} left`,
    isOverdue
  }
}

function getWorkingTimeDifference(startTimestamp, endTimestamp, holidayDatesByYear) {
  const direction = endTimestamp >= startTimestamp ? 1 : -1
  const firstTimestamp = Math.min(startTimestamp, endTimestamp)
  const lastTimestamp = Math.max(startTimestamp, endTimestamp)
  let elapsedMs = 0
  let cursor = new Date(firstTimestamp)

  while (cursor.getTime() < lastTimestamp) {
    const nextDay = new Date(cursor)
    nextDay.setHours(24, 0, 0, 0)
    const segmentEnd = Math.min(nextDay.getTime(), lastTimestamp)
    if (isWorkingDay(cursor, holidayDatesByYear)) {
      elapsedMs += segmentEnd - cursor.getTime()
    }
    cursor = new Date(segmentEnd)
  }

  return elapsedMs * direction
}

export function getPhaseTimerLabel(deadline, nowTimestamp, completedAt = null, holidayDatesByYear = {}) {
  const deadlineTimestamp = deadline.getTime()
  const referenceTimestamp = completedAt
    ? new Date(completedAt).getTime()
    : nowTimestamp
  if (!Number.isFinite(deadlineTimestamp) || !Number.isFinite(referenceTimestamp)) {
    return null
  }

  const remainingMs = getWorkingTimeDifference(
    referenceTimestamp,
    deadlineTimestamp,
    holidayDatesByYear
  )
  if (completedAt && remainingMs >= 0) {
    return null
  }

  const isOverdue = remainingMs < 0
  const totalMinutes = Math.floor(Math.abs(remainingMs) / 60000)
  const days = Math.floor(totalMinutes / (24 * 60))
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60)
  const minutes = totalMinutes % 60
  const duration = [
    days ? `${days}d` : '',
    hours ? `${hours}h` : '',
    minutes || (!days && !hours) ? `${minutes}m` : ''
  ].filter(Boolean).join(' ')

  return isOverdue ? `Overdue by ${duration}` : `${duration} left`
}
