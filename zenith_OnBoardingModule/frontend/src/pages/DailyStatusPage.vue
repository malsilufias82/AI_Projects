<template>
  <q-page class="Daily-Status-page">
    <!-- Status Report -->
    <div class="status-report-container">
      <q-card class="status-report-card">
        <q-card-section class="row items-center justify-between q-pb-none">
          <div>
            <div class="text-subtitle1 text-bold">  Daily Status Report</div>
            <div class="text-caption text-grey-6">Rolling 7-day timeline</div>
          </div>
          <div class="row items-center q-gutter-sm">
            <q-btn
              round
              flat
              dense
              icon="chevron_left"
              @click="navigateTimeline(-1)"
              class="date-nav-btn"
            />
            <div class="text-subtitle2 text-grey-7 q-px-md">
              {{ weekRangeText }}
            </div>
            <q-btn
              round
              flat
              dense
              icon="chevron_right"
              @click="navigateTimeline(1)"
              class="date-nav-btn"
            />
            <q-icon name="event" class="cursor-pointer q-ml-sm" size="20px">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-date
                  v-model="calendarDate"
                  mask="YYYY-MM-DD"
                  today-btn
                  minimal
                  @update:model-value="onCalendarDateChange"
                >
                  <div class="row items-center justify-end q-pa-sm">
                    <q-btn v-close-popup label="Close" color="primary" flat />
                  </div>
                </q-date>
              </q-popup-proxy>
            </q-icon>
            <q-icon
              v-if="isSaving"
              name="sync"
              class="q-ml-sm"
              size="20px"
              color="primary"
            >
              <q-tooltip>Saving...</q-tooltip>
            </q-icon>
          </div>
        </q-card-section>

        <q-card-section>
          <div ref="weeklyGridRef" class="weekly-grid">
            <div
              v-for="day in weekDays"
              :key="day.key"
              class="day-column"
              :class="{ 'weekend-day': day.isWeekend }"
            >
              <div class="day-header">
                <div class="column items-center" style="width: 100%;">
                  <div class="row items-center justify-between" style="width: 100%;">
                    <div class="text-subtitle2 text-bold">{{ day.label }}</div>
                  </div>
                  <div class="text-caption text-grey-6">{{ day.date }}</div>
                  <q-select
                    v-if="!day.isWeekend"
                    v-model="dailyReports[day.fullDate].leaveType"
                    :options="leaveOptions"
                    outlined
                    dense
                    style="width: 100%; font-size: 13px; margin-top: 8px;"
                    emit-value
                    map-options
                    @update:model-value="selectLeave(day.fullDate, $event)"
                  />
                </div>
              </div>
              <div v-if="!day.isWeekend" class="day-status-grid">
                <div
                  v-for="col in statusColumns"
                  :key="col.key"
                  class="status-item"
                  :style="{ borderTopColor: col.color, backgroundColor: getDayBackgroundColor(day.fullDate) }"
                >
                  <div class="row items-center q-mb-xs justify-between">
                    <div class="row items-center">
                      <q-icon :name="col.icon" :color="col.iconColor" size="16px" />
                      <span class="text-caption q-ml-xs">{{ col.label }}</span>
                    </div>
                    <!-- Add 'No Updates' checkbox for all sections - only visible when leaveType is 'Working' -->
                    <q-checkbox
                      v-if="dailyReports[day.fullDate].leaveType === 'Working'"
                      v-model="dailyReports[day.fullDate][`${col.key}NoUpdates`]"
                      dense
                      size="sm"
                      color="primary"
                    >
                      <q-tooltip style="font-size: 13px;">
                        Check this box if you don't have any updates for this section. If unchecked, you are expected to provide details.
                      </q-tooltip>
                    </q-checkbox>
                  </div>
                  <q-input
                    v-model="dailyReports[day.fullDate][col.key]"
                    type="textarea"
                    autogrow
                    borderless
                    :placeholder="col.placeholder"
                    input-style="min-height: 250px; max-height: 500px; font-size: 14px;"
                    class="compact-input"
                    :disable="dailyReports[day.fullDate].leaveType === 'Working' && dailyReports[day.fullDate][`${col.key}NoUpdates`]"
                    @update:model-value="handleSectionInput(day.fullDate, col.key)"
                  />
                </div>
              </div>
              <div v-else class="weekend-notes">
                <q-input
                  v-model="dailyReports[day.fullDate].notes"
                  type="textarea"
                  autogrow
                  borderless
                  placeholder=""
                  input-style="min-height: 1500px; max-height: 700px; font-size: 2px;"
                  class="compact-input"
                />
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { date as qDateUtils, Notify } from 'quasar'
import { api } from 'src/boot/axios'

// Debounce utility
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const fetchReports = async (start, end) => {
  const { data } = await api.get('/v1/daily-reports/', { params: { start, end } })
  return data
}

const saveReports = async (reports) => {
  const { data } = await api.post('/v1/daily-reports/', { reports })
  return data
}

// ----------  Daily Status Report (week-based) ----------
const statusColumns = ref([
  { key: 'completed', label: 'Completed', icon: 'check', iconColor: 'green', color: '#639922', placeholder: 'What did you finish today?' },
  { key: 'inProgress', label: 'In Progress', icon: 'sync', iconColor: 'blue', color: '#378ADD', placeholder: "What's still in motion?" },
  { key: 'blockers', label: 'Blockers', icon: 'error_outline', iconColor: 'red', color: '#E24B4A', placeholder: "What's holding things up?" },
  { key: 'nextPlan', label: 'Next Plan', icon: 'event', iconColor: 'purple', color: '#7F77DD', placeholder: "What's next on deck?" },
  { key: 'notes', label: 'Notes', icon: 'notes', iconColor: 'grey', color: '#888780', placeholder: 'Anything else worth flagging?' }
])

// Current timeline end date (today by default for rolling 7-day window)
const timelineEndDate = ref(new Date())

// Calendar date for popup
const calendarDate = ref(qDateUtils.formatDate(new Date(), 'YYYY-MM-DD'))

// Loading state
const isLoading = ref(false)

// Saving state for auto-save indicator
const isSaving = ref(false)

// Ref for scrolling
const weeklyGridRef = ref(null)

// Scroll to rightmost position on mount
onMounted(() => {
  nextTick(() => {
    if (weeklyGridRef.value) {
      weeklyGridRef.value.scrollLeft = weeklyGridRef.value.scrollWidth
    }
  })
})

// Handle calendar date selection - sets the end date of the timeline
const onCalendarDateChange = (date) => {
  if (date) {
    timelineEndDate.value = new Date(date)
  }
}

// Week days - rolling 7-day window
const weekDays = computed(() => {
  const days = []
  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const dayKeys = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

  // Start from 6 days before the end date to show 7-day window
  const startDate = new Date(timelineEndDate.value)
  startDate.setDate(startDate.getDate() - 6)

  for (let i = 0; i < 7; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    const dayIndex = date.getDay() // 0 = Sunday, 1 = Monday, etc.
    days.push({
      key: dayKeys[dayIndex === 0 ? 6 : dayIndex - 1], // Map Sunday to 'sun', Monday to 'mon', etc.
      label: dayNames[dayIndex === 0 ? 6 : dayIndex - 1],
      date: qDateUtils.formatDate(date, 'MMM DD'),
      fullDate: qDateUtils.formatDate(date, 'YYYY-MM-DD'),
      isWeekend: dayIndex === 0 || dayIndex === 6 // Sunday (0) or Saturday (6)
    })
  }
  return days
})

// Week range text for display
const weekRangeText = computed(() => {
  const firstDay = weekDays.value[0]
  const lastDay = weekDays.value[6]
  return `${firstDay.date} - ${lastDay.date}`
})

// Navigate timeline by days (not weeks)
const navigateTimeline = (days) => {
  const newDate = new Date(timelineEndDate.value)
  newDate.setDate(newDate.getDate() + days)
  timelineEndDate.value = newDate
}

// Daily report data structure - keyed by date (YYYY-MM-DD)
const dailyReports = ref({})

const emptyDayEntry = () => ({ completed: '', inProgress: '', blockers: '', nextPlan: '', notes: '', leaveType: 'Working', noAdditionalUpdates: false, completedNoUpdates: false, inProgressNoUpdates: false, blockersNoUpdates: false, nextPlanNoUpdates: false, notesNoUpdates: false })

// Leave options for dropdown
const leaveOptions = [
  { label: 'Working', value: 'Working' },
  { label: 'Sick Leave', value: 'Sick Leave' },
  { label: 'Planned Leave', value: 'Planned Leave' },
  { label: 'Casual Leave', value: 'Casual Leave' },
  { label: 'Restricted Leave', value: 'Restricted Leave' },
  { label: 'Official Leave', value: 'Official Leave' }
]

// Leave type to color mapping
const leaveColors = {
  'Working': '#ffffff', // white
  'Sick Leave': '#fff9c4', // light yellow
  'Planned Leave': '#c8e6c9', // light green
  'Casual Leave': '#bbdefb', // light blue
  'Restricted Leave': '#ffcdd2', // light red
  'Official Leave': '#e0e0e0' // grey
}

// Get background color for a day based on leave type
const getDayBackgroundColor = (date) => {
  const leaveType = dailyReports.value[date]?.leaveType
  return leaveType ? leaveColors[leaveType] : ''
}

// Select leave type for a specific day
const selectLeave = (date, leaveType) => {
  if (!dailyReports.value[date]) {
    dailyReports.value[date] = emptyDayEntry()
  }
  dailyReports.value[date].leaveType = leaveType
  // Reset all checkboxes when leave type changes
  dailyReports.value[date].noAdditionalUpdates = false
  dailyReports.value[date].completedNoUpdates = false
  dailyReports.value[date].inProgressNoUpdates = false
  dailyReports.value[date].blockersNoUpdates = false
  dailyReports.value[date].nextPlanNoUpdates = false
  dailyReports.value[date].notesNoUpdates = false
  // Only populate text areas with leave type if it's not 'Working'
  if (leaveType !== 'Working') {
    dailyReports.value[date].completed = leaveType
    dailyReports.value[date].inProgress = leaveType
    dailyReports.value[date].blockers = leaveType
    dailyReports.value[date].nextPlan = leaveType
    dailyReports.value[date].notes = leaveType
  } else {
    // Clear text areas when switching to 'Working'
    dailyReports.value[date].completed = ''
    dailyReports.value[date].inProgress = ''
    dailyReports.value[date].blockers = ''
    dailyReports.value[date].nextPlan = ''
    dailyReports.value[date].notes = ''
  }
}

// Handle section input - uncheck checkbox if user types in the field
const handleSectionInput = (date, key) => {
  if (dailyReports.value[date] && dailyReports.value[date][`${key}NoUpdates`]) {
    dailyReports.value[date][`${key}NoUpdates`] = false
  }
}

// Watch for checkbox changes to clear/enable text inputs
watch(dailyReports, (newVal) => {
  Object.keys(newVal).forEach(date => {
    const dayData = newVal[date]
    if (dayData && dayData.leaveType === 'Working') {
      // Check each section's checkbox
      ['completed', 'inProgress', 'blockers', 'nextPlan', 'notes'].forEach(key => {
        const checkboxKey = `${key}NoUpdates`
        if (dayData[checkboxKey] && dayData[key]) {
          // If checkbox is checked, clear the text input
          dayData[key] = ''
        }
      })
    }
  })
}, { deep: true })

// Fetch reports from API whenever the visible window changes
watch(weekDays, async (days) => {
  days.forEach(day => {
    if (!dailyReports.value[day.fullDate]) {
      dailyReports.value[day.fullDate] = emptyDayEntry()
    }
  })

  isLoading.value = true
  try {
    const start = days[0].fullDate
    const end = days[days.length - 1].fullDate
    const fetched = await fetchReports(start, end)
    Object.entries(fetched).forEach(([date, data]) => {
      dailyReports.value[date] = { ...emptyDayEntry(), ...data }
    })
  } catch (err) {
    console.error('Failed to load reports', err)
    Notify.create({ type: 'negative', message: 'Could not load status reports' })
  } finally {
    isLoading.value = false
  }
}, { immediate: true, deep: true })


// Auto-save with debounce
const autoSave = debounce(async () => {
  const weekData = {}
  let hasContent = false

  weekDays.value.forEach(day => {
    const dayData = dailyReports.value[day.fullDate]
    // Check if any field has content (including leave type and checkbox states)
    const hasDayContent = (
      (dayData.completed && dayData.completed.trim() !== '') ||
      (dayData.inProgress && dayData.inProgress.trim() !== '') ||
      (dayData.blockers && dayData.blockers.trim() !== '') ||
      (dayData.nextPlan && dayData.nextPlan.trim() !== '') ||
      (dayData.notes && dayData.notes.trim() !== '') ||
      (dayData.leaveType && dayData.leaveType.trim() !== '') ||
      // Include checkbox states as content
      dayData.completedNoUpdates ||
      dayData.inProgressNoUpdates ||
      dayData.blockersNoUpdates ||
      dayData.nextPlanNoUpdates ||
      dayData.notesNoUpdates
    )

    // Always include the day data if it exists (even if empty) to handle resets
    if (dayData) {
      weekData[day.fullDate] = dayData
      if (hasDayContent) {
        hasContent = true
      }
    }
  })

  console.log('Week data to save:', weekData)
  console.log('Has content:', hasContent)

  isSaving.value = true
  try {
    console.log('Saving reports...')
    const result = await saveReports(weekData)
    console.log('Save successful:', result)
  } catch (err) {
    console.error('Failed to auto-save report', err)
  } finally {
    isSaving.value = false
  }
}, 1000) // 1 second debounce

// Watch for changes and auto-save
watch(dailyReports, () => {
  autoSave()
}, { deep: true })

</script>

<style scoped>
.Daily-Status-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.status-report-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 16px 16px 0;
}

.status-report-card {
  border: 2px solid #e0e0e0;
  box-shadow: none;
  border-radius: 8px;
}

.status-date-input {
  width: 150px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.date-nav-btn {
  color: #666;
}

.date-nav-btn:hover {
  color: #1976d2;
  background-color: rgba(25, 118, 210, 0.08);
}

.weekly-grid {
  display: flex;
  gap: 10px;
  align-items: stretch;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-behavior: smooth;
}

.day-column {
  flex: 1 0 220px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
}

.day-column.weekend-day {
  background-color: #f9f9f9;
  opacity: 0.85;
  min-width: 80px;
  max-width: 80px;
  padding: 8px;
}

.day-header {
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 8px;
}

.day-status-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.status-item {
  border: 1px solid #e0e0e0;
  border-top: 2px solid;
  border-radius: 4px;
  padding: 6px;
}

.weekend-notes {
  padding: 6px;
}

.compact-input :deep(.q-field__control) {
  padding: 4px 0;
}

.compact-input :deep(.q-field__native) {
  font-size: 12px;
  line-height: 1.3;
}
</style>
