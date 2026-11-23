import assert from 'node:assert/strict'
import test from 'node:test'
import {
  getPhaseActivityRows,
  getPhaseCompletionTimestamp,
  getSameDayDeadline,
  getSameDaySlaStatus,
  getWorkingDayDeadline,
  getOnboardingDaySchedule,
  getPhaseTimerLabel,
  isCompletedActivityStatus,
  isVdiActivationActivityRow
} from './onboardingSchedule.js'

test('treats Not Applicable and Completed as completed activity statuses', () => {
  for (const status of ['Completed', 'Not Applicable', 'complete', 'n/a']) {
    assert.equal(isCompletedActivityStatus(status), true)
  }
  for (const status of ['In Progress', 'Pending', 'Blocked']) {
    assert.equal(isCompletedActivityStatus(status), false)
  }
})

test('recognizes the Week0-labelled Client VDI task as a VDI Activation task', () => {
  assert.equal(isVdiActivationActivityRow({
    day: 'Week0',
    activity: 'Client VDI',
    action: 'VDI Activation'
  }), true)
  assert.equal(isVdiActivationActivityRow({
    day: 'Week0',
    activity: 'Other activity',
    action: 'VDI Activation'
  }), false)
})

test('calculates a same-day SLA deadline at the end of the credentials received date', () => {
  const deadline = getSameDayDeadline('2026-10-10')

  assert.deepEqual(
    [deadline.getFullYear(), deadline.getMonth(), deadline.getDate(), deadline.getHours(), deadline.getMinutes()],
    [2026, 9, 10, 23, 59]
  )
})

test('rejects invalid same-day SLA dates', () => {
  assert.equal(getSameDayDeadline('not-a-date'), null)
  assert.equal(getSameDayDeadline('2026-02-31'), null)
})

test('calculates a working-day deadline while skipping weekends and holidays', () => {
  const deadline = getWorkingDayDeadline('2026-10-10', 5, {
    2026: new Set(['2026-10-13', '2026-10-19'])
  })

  assert.deepEqual(
    [deadline.getFullYear(), deadline.getMonth(), deadline.getDate(), deadline.getHours()],
    [2026, 9, 20, 23]
  )
})

test('shows same-day SLA completion and overdue status with elapsed overdue duration', () => {
  const deadline = new Date(2026, 9, 10, 23, 59, 59, 999)

  assert.deepEqual(
    getSameDaySlaStatus(deadline, new Date(2026, 9, 11, 12).getTime(), new Date(2026, 9, 10, 20), true),
    { label: 'Completed on time', isOverdue: false }
  )
  assert.deepEqual(
    getSameDaySlaStatus(deadline, new Date(2026, 9, 12, 12).getTime(), new Date(2026, 10, 1, 0), true),
    { label: 'Overdue by 21d', isOverdue: true }
  )
  assert.deepEqual(
    getSameDaySlaStatus(deadline, new Date(2026, 9, 11, 1).getTime()),
    { label: 'Overdue by 1h', isOverdue: true }
  )
})

test('rejects invalid calendar deadline inputs', () => {
  assert.equal(getWorkingDayDeadline('not-a-date', 5), null)
  assert.equal(getWorkingDayDeadline('2026-02-31', 5), null)
  assert.equal(getWorkingDayDeadline('2026-10-10', -1), null)
})

test('starts Day 1 the same day when Week 0 completes before 2 PM', () => {
  const schedule = getOnboardingDaySchedule(new Date(2026, 9, 13, 13, 59))

  assert.deepEqual(
    schedule.slice(0, 2).map((day) => [day.getFullYear(), day.getMonth(), day.getDate()]),
    [
      [2026, 9, 13],
      [2026, 9, 14]
    ]
  )
})

test('starts Day 1 on the next working day when Week 0 completes at or after 2 PM', () => {
  const schedule = getOnboardingDaySchedule(new Date(2026, 9, 13, 14, 0))

  assert.deepEqual(
    schedule.slice(0, 2).map((day) => [day.getFullYear(), day.getMonth(), day.getDate()]),
    [
      [2026, 9, 14],
      [2026, 9, 15]
    ]
  )
})

test('keeps October 12, 2026 as an onboarding working day when it is in the holiday calendar', () => {
  const schedule = getOnboardingDaySchedule(
    new Date(2026, 9, 9, 14, 1),
    { 2026: new Set(['2026-10-12']) }
  )

  assert.deepEqual(
    schedule.map((day) => [day.getFullYear(), day.getMonth(), day.getDate()]),
    [
      [2026, 9, 12],
      [2026, 9, 13],
      [2026, 9, 14],
      [2026, 9, 15],
      [2026, 9, 16]
    ]
  )
})

test('continues to skip other holidays and weekends', () => {
  const schedule = getOnboardingDaySchedule(
    new Date(2026, 9, 12, 14, 1),
    { 2026: new Set(['2026-10-13', '2026-10-19']) }
  )

  assert.deepEqual(
    schedule.map((day) => [day.getFullYear(), day.getMonth(), day.getDate()]),
    [
      [2026, 9, 14],
      [2026, 9, 15],
      [2026, 9, 16],
      [2026, 9, 20],
      [2026, 9, 21]
    ]
  )
})

test('does not show overdue time when a day is completed within its ETA', () => {
  const deadline = new Date(2026, 9, 16, 20, 0)

  assert.equal(
    getPhaseTimerLabel(deadline, new Date(2026, 9, 18, 12, 0).getTime(), new Date(2026, 9, 16, 19, 30)),
    null
  )
})

test('freezes overdue time at the day completion timestamp', () => {
  const deadline = new Date(2026, 9, 16, 20, 0)

  assert.equal(
    getPhaseTimerLabel(deadline, new Date(2026, 9, 18, 12, 0).getTime(), new Date(2026, 9, 17, 21, 30)),
    'Overdue by 4h'
  )
})

test('excludes weekends and holidays when calculating overdue time', () => {
  const deadline = new Date(2026, 9, 16, 20, 0)
  const now = new Date(2026, 9, 21, 11, 14)
  const holidayDatesByYear = { 2026: new Set(['2026-10-20']) }

  assert.equal(
    getPhaseTimerLabel(deadline, now.getTime(), null, holidayDatesByYear),
    'Overdue by 1d 15h 14m'
  )
})

test('uses the latest activity completion timestamp to stop the day timer', () => {
  const firstCompletion = new Date(2026, 9, 14, 16, 0)
  const finalCompletion = new Date(2026, 9, 14, 21, 0)
  const rows = [
    { status: 'Completed', completedAt: firstCompletion.toISOString() },
    { status: 'Completed', completedAt: finalCompletion.toISOString(), updatedAt: new Date(2026, 9, 16, 17, 8) },
    { status: 'Completed', updatedAt: new Date(2026, 9, 16, 17, 8) }
  ]
  const completionTimestamp = getPhaseCompletionTimestamp(rows)

  assert.equal(completionTimestamp.getTime(), finalCompletion.getTime())
  assert.equal(
    getPhaseTimerLabel(
      new Date(2026, 9, 12, 20, 0),
      new Date(2026, 9, 16, 12, 0).getTime(),
      completionTimestamp
    ),
    'Overdue by 2d 1h'
  )
})

test('does not treat edited timestamps as completion timestamps', () => {
  assert.equal(getPhaseCompletionTimestamp([
    { status: 'Completed', updatedAt: '2026-10-16T11:38:00.000Z' },
    { status: 'Completed', updatedAt: '2026-10-16T11:38:00.000Z' }
  ]), null)
})

test('ignores October 16 edits when completion timestamps are from October 14', () => {
  const rows = [
    {
      status: 'Completed',
      completedAt: '2026-10-14T14:11:24.480Z',
      updatedAt: '2026-10-16T11:38:28.544Z'
    },
    { status: 'Completed', updatedAt: '2026-10-16T11:38:28.544Z' }
  ]
  const completionTimestamp = getPhaseCompletionTimestamp(rows)

  assert.equal(
    getPhaseTimerLabel(
      new Date('2026-10-12T14:30:00.000Z'),
      new Date('2026-10-16T12:00:00.000Z').getTime(),
      completionTimestamp
    ),
    'Overdue by 1d 23h 41m'
  )
})

test('shows 2d 1h overdue when the final Day1-A activity completed October 14 at 9 PM', () => {
  const rows = [
    { day: 'Day1', status: 'Completed', completedAt: new Date(2026, 9, 14, 16, 0) },
    { day: 'Day1-A', status: 'Completed', completedAt: new Date(2026, 9, 14, 21, 0) }
  ]
  const completionTimestamp = getPhaseCompletionTimestamp(getPhaseActivityRows(rows, 1))

  assert.equal(
    getPhaseTimerLabel(
      new Date(2026, 9, 12, 20, 0),
      new Date(2026, 9, 16, 18, 0).getTime(),
      completionTimestamp
    ),
    'Overdue by 2d 1h'
  )
})

test('does not mark the day finished until every activity is completed', () => {
  assert.equal(getPhaseCompletionTimestamp([
    { status: 'Completed', completedAt: '2026-10-14T11:00:00.000Z' },
    { status: 'Pending' }
  ]), null)
})

test('includes Day1-A through Day5-A rows when resolving each day', () => {
  for (let dayNumber = 1; dayNumber <= 5; dayNumber += 1) {
    const rows = [
      { day: `Day${dayNumber}`, activity: 'Primary' },
      { day: `Day${dayNumber}-A`, activity: 'Additional' },
      { day: `Day${dayNumber + 1}`, activity: 'Next day' }
    ]

    assert.deepEqual(
      getPhaseActivityRows(rows, dayNumber).map((row) => row.activity),
      ['Primary', 'Additional']
    )
  }
})

test('freezes the overdue timer for each completed day from Day1 through Day5', () => {
  const schedule = getOnboardingDaySchedule(new Date(2026, 9, 12, 10, 0))
  const laterTimestamp = new Date(2026, 9, 30, 12, 0).getTime()

  for (const day of schedule) {
    const deadline = new Date(day)
    deadline.setHours(20, 0, 0, 0)
    const completedAt = new Date(day)
    completedAt.setHours(22, 0, 0, 0)

    assert.equal(
      getPhaseTimerLabel(deadline, laterTimestamp, completedAt),
      'Overdue by 2h'
    )
  }
})

test('shows a live countdown only while the day is incomplete', () => {
  const deadline = new Date(2026, 9, 16, 20, 0)

  assert.equal(
    getPhaseTimerLabel(deadline, new Date(2026, 9, 16, 19, 0).getTime()),
    '1h left'
  )
  assert.equal(
    getPhaseTimerLabel(deadline, new Date(2026, 9, 16, 20, 30).getTime()),
    'Overdue by 30m'
  )
})
