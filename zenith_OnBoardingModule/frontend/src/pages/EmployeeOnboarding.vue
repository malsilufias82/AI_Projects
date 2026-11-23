<template>
  <q-page class="bg-grey-2 q-pa-lg">
    <q-inner-loading :showing="loading" color="primary" />
    <div class="page-content q-gutter-y-lg">
      <div class="page-header">
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">Employee Onboarding Tracker</h1>
          <p class="text-grey-7 q-mt-sm q-mb-none">
            Track onboarding milestones, credential availability, background verification, and VCF completion.
          </p>
        </div>
        <q-btn outline icon="arrow_back" label="Back" to="/onboarding-dashboard" />
      </div>

      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Employee Information</div>
          <div class="row q-col-gutter-md">
            <div v-for="field in employeeFields" :key="field.label" class="col-approx-12">
              <div class="info-field">
                <div class="text-caption text-grey-7">{{ field.label }}</div>
                <div class="text-weight-medium q-py-none">{{ field.value }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

       <div class="phase-header q-mb-md">
          <div class="text-h6">Employee onboarding phases</div>
          <div class="phase-legend" >
            <q-badge color="warning" label="In-progress" class="legend-badge" />
            <q-badge color="positive" label="Completed" class="legend-badge" />
            <q-badge color="grey-6" label="To be started" class="legend-badge" />
          </div>
        </div>
          <div class="row q-col-gutter-x-xl q-col-gutter-y-md">
            <div v-for="field in employeePhases" :key="field.label" class="col-approx-10">
              <div class="info-field">
                <div class="phase-label text-caption text-bold text-black-7">
                  <q-btn
                    v-if="clickableTrackerPhases.has(field.label)"
                    flat
                    dense
                    no-caps
                    color="primary"
                    class="tracker-text-btn clickable-label text-primary cursor-pointer"
                    :label="field.label"
                    :disable="isDayPhaseLocked(field.label)"
                    @click="openTrackerPhase(field.label)"
                  />
                  <template v-else>
                    <span class="non-clickable-label">{{ field.label }}</span>
                  </template>
                </div>
                <div class="badge-container">
                  <q-badge :color="field.color" :label="field.value" style="padding: 6px 10px !important;" />
                  <div
                    v-if="['Week0', 'VDI Activation', 'Day1', 'Day2', 'Day3', 'Day4', 'Day5'].includes(field.label) && field.pendingCount !== null && field.pendingCount !== undefined"
                    class="phase-pending-count text-caption text-grey-7 q-mt-xs"
                  >
                    Pending: {{ field.pendingCount }}
                  </div>
                  <div
                    v-if="field.targetLabel"
                    class="phase-target-label text-caption text-grey-7 q-mt-xs"
                  >
                    {{ field.targetLabel }}
                  </div>
                  <div
                    v-if="field.timeRemainingLabel"
                    class="phase-target-label text-caption"
                    :class="[field.timeRemainingColor, { 'text-weight-bold': field.isOverdue }]"
                  >
                    {{ field.timeRemainingLabel }}
                  </div>
                </div>
              </div>
            </div>
          </div>

      <div class="q-gutter-y-md">
        <q-card v-for="item in orderedTrackingData" :key="item.title" flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">{{ item.title }}</div>

              <q-input
                v-if="showRequestedDate(item)"
                v-model="item.requestedDate"
                type="date"
                outlined
                dense
                :label="item.label1"
                class="q-mb-md date-field"
                :readonly="isViewMode"
                inputmode="none"
                @keydown.prevent
                @focus="(event) => openDateSelector(event)"
                @update:model-value="(value) => handleRequestedDateChange(item, value)"
              />

              <q-input
                v-model="item.completedDate"
                type="date"
                outlined
                dense
                :label="item.label2"
                class="q-mb-md date-field"
                :readonly="isViewMode"
                :min="item.requestedDate || undefined"
                inputmode="none"
                @keydown.prevent
                @focus="(event) => openDateSelector(event)"
                @update:model-value="(value) => handleCompletedDateChange(item, value)"
              />

              <q-select
                v-model="item.status"
                outlined
                dense
                label="Current Status"
                :options="trackingStatusOptionsFor(item)"
                class="q-mb-md"
                :readonly="isViewMode"
                @update:model-value="handleTrackingStatusChange(item, $event)"
              />

            <div v-if="item.title !== 'Client Credentials'" class="row q-col-gutter-sm">
              <div v-if="showWaitingDays(item)" class="col-6">
                <div class="info-field">
                  <div class="text-caption text-grey-7">Waiting Days</div>
                  <div class="text-h6 q-mt-xs">{{ waitingDays(item) }}</div>
                </div>
              </div>
              <div :class="showWaitingDays(item) ? 'col-6' : 'col-12'">
                <div class="info-field">
                  <div class="text-caption text-grey-7">RAG Status</div>
                  <div class="rag-actions q-mt-sm">
                    <q-badge :color="ragColors[getDisplayRag(item)]" :label="getDisplayRag(item)" />
                    
                    
                    <!-- Email button for BGV completion email, only shown when the phase is 'Background Verification' and its status is 'Completed' -->
                  <!--  <q-btn
                      v-if="item.title === 'Background Verification' && item.status === 'Completed'"
                      outline
                      dense
                      color="secondary"
                      label="EmailToUser"
                      :loading="emailSending"
                      :disable="emailSending"
                      @click="sendBgvCompletionEmail"
                    >
                      
                
                    </q-btn> -->



                    <q-btn
                    v-if="item.title === 'Background Verification' && item.status === 'Completed'"
                   unelevated rounded
                   color="blue"
                   icon="mark_email_read"
                   label="Send BGVCompletion Email"
                   :loading="emailSending"
                    :disable="emailSending"
                    @click="sendBgvCompletionEmail">
                      <q-tooltip>Email will be send to the user on clicking it</q-tooltip>
                    </q-btn>

                    <q-btn
                      v-if="item.title === 'VCF Tracking' && isClientCredentialsCompleted()"
                      unelevated
                      rounded
                      color="blue"
                      icon="mark_email_read"
                      label="Send Credential Received Email"
                      :loading="emailSending"
                      :disable="emailSending"
                      @click="sendClientCredentialEmail"
                    >
                      <q-tooltip>Email will be sent to the user on clicking it</q-tooltip>
                    </q-btn>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Overall Onboarding Status</div>
          <div class="row q-col-gutter-md">
            <q-select
              v-model="overallStatus"
              outlined
              dense
              label="Onboarding Status"
              :options="onboardingStatusOptions"
              class="col-12 col-md-4"
              :readonly="isViewMode"
              @update:model-value="handleOverallStatusChange"
            />
            <q-input v-model="remarks" outlined dense type="textarea" label="Remarks" class="col-12 col-md-8" :readonly="isViewMode" />
          </div>
        </q-card-section>
      </q-card>

      <q-card v-if="!isViewMode" flat bordered>
        <q-card-actions align="right" class="q-pa-md q-gutter-sm">
          <q-btn outline label="Reset" :disable="loading || saving" @click="resetChanges" />
          <q-btn color="primary" label="Save" :loading="saving" :disable="loading || !employeeId" @click="saveChanges" />
        </q-card-actions>
      </q-card>
    </div>
  </q-page>
</template>



<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import {
  getPhaseActivityRows,
  getPhaseCompletionTimestamp,
  getSameDayDeadline,
  getSameDaySlaStatus,
  isCompletedActivityStatus,
  isVdiActivationActivityRow,
  getOnboardingDaySchedule,
  getPhaseTimerLabel
} from 'src/utils/onboardingSchedule'


const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const loading = ref(false)
const saving = ref(false)
const emailSending = ref(false)
const employeeId = computed(() => {
  const query = route.query || {}
  return String(
    query.employeeId ||
    query.userId ||
    query.id ||
    route.params.employeeId ||
    route.params.userId ||
    route.params.id ||
    ''
  )
})
const isViewMode = computed(() => route.query.mode === 'view')
const overallStatus = ref('Pending')
const remarks = ref('')
const employee = reactive({ name: '', employeeCode: '', email: '', teamLeadEmail: '', accountManagerEmail: '', client: '', project: '', teamLead: '', accountManager: '', joiningDate: '' })
const employeeFields = computed(() => [
  { label: 'Employee', value: employee.name },
  { label: 'Employee ID', value: employee.employeeCode },
  { label: 'Client', value: employee.client },
  { label: 'Project', value: employee.project },
  { label: 'Team Lead', value: employee.teamLead },
  { label: 'Account Manager', value: employee.accountManager },
  { label: 'Joining Date', value: timestampToDate(employee.joiningDate) }
])
const onboardingStatusOptions = ['Pending', 'InProgress', 'Completed', 'Cancelled']
const trackingStatusOptions = ['InProgress','Pending', 'Completed']
const ragColors = { Green: 'positive', Amber: 'warning', Red: 'negative' }
const trackingData = reactive([])
const week0Rows = ref([])
const week0PhaseCounts = ref({})
const phaseCompletionDates = ref({})
const savedState = ref(null)
const currentTimestamp = ref(Date.now())
const holidayDatesByYear = ref({})
const holidayCalendarError = ref('')
const holidayCalendarLoading = ref(false)
const trackingOrder = ['Background Verification', 'VCF Tracking', 'Client Credentials']
const slaDeadlineHour = 20

onMounted(() => {
  const timer = window.setInterval(() => {
    currentTimestamp.value = Date.now()
  }, 60000)

  onBeforeUnmount(() => {
    window.clearInterval(timer)
  })
})

function isCompletedStatus(value) {
  return ['completed', 'complete'].includes(String(value || '').trim().toLowerCase())
}

const orderedTrackingData = computed(() => {
  const byTitle = new Map(trackingData.map((item) => [item.title, item]))
  return trackingOrder.map((title) => byTitle.get(title)).filter(Boolean)
})

watch(
  trackingData,
  () => {
    const vcfItem = trackingData.find((item) => item.title === 'VCF Tracking')
    const clientItem = trackingData.find((item) => item.title === 'Client Credentials')

    if (!vcfItem || !clientItem) return

    const vcfCompleted = isCompletedStatus(vcfItem.status)
    const clientCompleted = isCompletedStatus(clientItem.status)

    if (vcfCompleted || clientCompleted) {
      vcfItem.status = 'Completed'
      clientItem.status = 'Completed'

      const syncedDate = vcfItem.completedDate || clientItem.completedDate || new Date().toISOString().slice(0, 10)
      vcfItem.completedDate = syncedDate
      clientItem.completedDate = syncedDate
    }
  },
  { deep: true }
)




function getPhaseCountsForLabel(label) {
  if (label === 'Week0') {
    const total = Number(week0PhaseCounts.value?.Week0_total ?? week0PhaseCounts.value?.Week0 ?? getApplicableWeek0Rows().length)
    const completed = Number(week0PhaseCounts.value?.Week0_completed ?? getCompletedCount(getApplicableWeek0Rows()))
    return {
      total: Number.isFinite(total) ? total : 0,
      completed: Number.isFinite(completed) ? completed : 0,
      pending: Math.max((Number.isFinite(total) ? total : 0) - (Number.isFinite(completed) ? completed : 0), 0)
    }
  }

  if (label === 'VDI Activation') {
    const rows = getVdiActivationRows()
    const total = rows.length
    const completed = getCompletedCount(rows)
    return {
      total,
      completed,
      pending: Math.max(total - completed, 0)
    }
  }

  if (['Day1', 'Day2', 'Day3', 'Day4', 'Day5'].includes(label)) {
    const dayNumber = Number(String(label).replace('Day', ''))
    const dayRows = getDayRows(dayNumber)
    const total = dayRows.length
    const completed = getCompletedCount(dayRows)
    return {
      total: Number.isFinite(total) ? total : 0,
      completed: Number.isFinite(completed) ? completed : 0,
      pending: Math.max((Number.isFinite(total) ? total : 0) - (Number.isFinite(completed) ? completed : 0), 0)
    }
  }

  return { total: 0, completed: 0, pending: 0 }
}

function getPhasePendingCount(label) {
  return getPhaseCountsForLabel(label).pending
}

function getDayTargetInfo(dayNumber) {
  const completionTime = getVdiActivationCompletionTimestamp()
  if (!completionTime) return null
  if (holidayCalendarError.value) return { targetLabel: 'Holiday calendar unavailable' }
  if (holidayCalendarLoading.value) return { targetLabel: 'Loading target date...' }

  const schedule = getDaySchedule(completionTime)
  if (!schedule) return null

  const targetDate = schedule[dayNumber - 1]
  if (!targetDate) return null
  const deadline = new Date(targetDate)
  deadline.setHours(slaDeadlineHour, 0, 0, 0)

  const phaseCounts = getPhaseCountsForLabel(`Day${dayNumber}`)
  const phaseCompleted = phaseCounts.total > 0 && phaseCounts.completed >= phaseCounts.total
  const completedAt = phaseCompleted
    ? phaseCompletionDates.value[`Day${dayNumber}`] || getDayCompletionTimestamp(dayNumber)
    : null
  const timeRemainingLabel = phaseCompleted && !completedAt
    ? null
    : getPhaseTimerLabel(deadline, currentTimestamp.value, completedAt, holidayDatesByYear.value)
  const isOverdue = timeRemainingLabel?.startsWith('Overdue') || false

  return {
    deadline,
    targetLabel: `Target: ${formatTargetDate(deadline)}`,
    timeRemainingLabel,
    isOverdue,
    timeRemainingColor: isOverdue ? 'text-negative' : 'text-positive'
  }
}

const employeePhases = computed(() => {
  const phaseStatusByLabel = {
    BGV: getPhaseDisplayStatus('Background Verification'),
    VCF: getPhaseDisplayStatus('VCF Tracking'),
    Credentials: getPhaseDisplayStatus('Client Credentials'),
    Week0: getWeek0PhaseStatus(),
    'VDI Activation': getVdiActivationPhaseStatus(),
    Day1: getDayPhaseStatus(1),
    Day2: getDayPhaseStatus(2),
    Day3: getDayPhaseStatus(3),
    Day4: getDayPhaseStatus(4),
    Day5: getDayPhaseStatus(5)
  }

  return Object.entries(phaseStatusByLabel).map(([label, status]) => ({
    label,
    value: status.value,
    color: status.color,
    pendingCount: getPhasePendingCount(label),
    ...(label === 'VDI Activation'
      ? getVdiActivationTargetInfo()
      : label === 'Week0'
        ? getWeek0TargetInfo()
      : label.startsWith('Day')
        ? getDayTargetInfo(Number(label.slice(3))) || {}
        : {})
  }))
})

const clickableTrackerPhases = new Set(['Week0', 'VDI Activation', 'Day1', 'Day2', 'Day3', 'Day4', 'Day5'])

function snapshotState(data) {
  return {
    employee: {
      name: data.employee || '',
      employeeCode: data.employeeCode || '',
      email: data.email || '',
      teamLeadEmail: data.teamLeadEmail || '',
      accountManagerEmail: data.accountManagerEmail || '',
      client: data.client || '',
      project: data.project || '',
      teamLead: data.teamLead || '',
      accountManager: data.accountManager || '',
      joiningDate: data.joiningDate || ''
    },
    tracking: data.tracking.map((item) => ({ ...item })),
    overallStatus: data.status || 'Pending',
    remarks: data.remarks || ''
  }
}

function applyState(state) {
  Object.assign(employee, state.employee)
  trackingData.splice(0, trackingData.length, ...state.tracking.map((item) => ({ ...item })))
  overallStatus.value = state.overallStatus
  remarks.value = state.remarks
}

function showRequestedDate(item) {
  return item.title === 'Background Verification' || item.title === 'VCF Tracking'
}

function showWaitingDays(item) {
  return showRequestedDate(item)
}


function waitingDays(item) {
  if (!showWaitingDays(item) || !item.requestedDate) return 0
  const endDate = item.completedDate ? new Date(`${item.completedDate}T00:00:00`) : new Date()
  const startDate = new Date(`${item.requestedDate}T00:00:00`)
  return Math.max(0, Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)))
}

function getInitiatedDateAgeDays(item) {
  if (!item || !item.requestedDate) return 0

  const requestedDate = new Date(`${item.requestedDate}T00:00:00`)
  if (Number.isNaN(requestedDate.getTime())) return 0

  const currentDate = new Date()
  const msPerDay = 1000 * 60 * 60 * 24
  const diffDays = Math.ceil((currentDate - requestedDate) / msPerDay)
  return Math.max(0, diffDays)
}

function getDisplayRag(item) {
  if (item.title === 'Client Credentials' || item.title === 'Background Verification' || item.title === 'VCF Tracking') {
    const days = getInitiatedDateAgeDays(item)
    if (days <= 21) return 'Green'
    if (days <= 30) return 'Amber'
    return 'Red'
  }

  return item.rag || 'Green'
}

function getPhaseDisplayStatus(title) {
  const phase = trackingData.find((item) => item.title === title)
  if (!phase) {
    return { value: 'Not Applicable', color: 'grey-6' }
  }

  if (phase.status === 'Completed') {
    return { value: 'Completed', color: 'positive' }
  }

  return { value: 'In-progress', color: 'warning' }
}

function getApplicableWeek0Rows() {
  return getApplicableProjectRows(week0Rows.value).filter((row) => (
    !isVdiActivationActivityRow(row)
  ))
}

function getApplicableProjectRows(rows) {
  const employeeProject = String(employee.project || '').trim().toLowerCase()

  return rows.filter((row) => {
    const rowProject = String(row?.project || '').trim().toLowerCase()
    if (
      !employeeProject ||
      !rowProject ||
      ['applicable for all', 'applicable for all projects'].includes(rowProject)
    ) {
      return true
    }

    return rowProject === employeeProject
  })
}

function getVdiActivationRows() {
  return getApplicableProjectRows(week0Rows.value).filter((row) => (
    isVdiActivationActivityRow(row)
  ))
}

function getVdiActivationCompletionTimestamp() {
  const vdiActivities = getVdiActivationRows()
  if (!vdiActivities.length || !vdiActivities.every((row) => isCompletedActivityStatus(row?.status))) {
    return null
  }

  const completionTimes = vdiActivities
    .map((row) => {
      const completionTimestamp = row?.completedAt || row?.updatedAt || row?.createdAt
      if (!completionTimestamp) return null

      const timestamp = new Date(completionTimestamp)
      return Number.isNaN(timestamp.getTime()) ? null : timestamp
    })
    .filter((timestamp) => timestamp instanceof Date)

  if (completionTimes.length !== vdiActivities.length) return null
  return completionTimes.reduce((latest, current) => (
    current.getTime() > latest.getTime() ? current : latest
  ))
}

function getVdiActivationPhaseStatus() {
  const phaseCounts = getPhaseCountsForLabel('VDI Activation')
  if (phaseCounts.total === 0) {
    return { value: 'To be started', color: 'grey-6' }
  }

  if (phaseCounts.completed === phaseCounts.total) {
    return { value: 'Completed', color: 'positive' }
  }

  if (getVdiActivationTargetInfo().isOverdue) {
    return { value: 'Overdue', color: 'negative' }
  }

  return { value: 'In-progress', color: 'warning' }
}

function getVdiActivationTargetInfo() {
  return getCredentialSlaInfo(getVdiActivationRows())
}

function getWeek0TargetInfo() {
  const rows = getApplicableWeek0Rows()
  return rows.length ? getCredentialSlaInfo(rows) : {}
}

function getCredentialSlaInfo(rows) {
  const credentials = getTrackingItem('Client Credentials')
  if (!credentials?.completedDate) return {}

  const deadline = getSameDayDeadline(credentials.completedDate)
  if (!deadline) return {}

  const completed = rows.length > 0 && rows.every((row) => isCompletedActivityStatus(row?.status))
  const completedAt = completed
    ? getPhaseCompletionTimestamp(rows)
    : null
  const sla = getSameDaySlaStatus(deadline, currentTimestamp.value, completedAt, completed)
  if (!sla) return {}

  return {
    deadline,
    isOverdue: sla.isOverdue,
    targetLabel: `SLA deadline: ${formatTargetDate(deadline)}`,
    timeRemainingLabel: sla.label,
    timeRemainingColor: sla.isOverdue ? 'text-negative' : 'text-positive'
  }
}

function isDayPhaseLocked(label) {
  return /^Day[1-5]$/.test(label) && !getVdiActivationCompletionTimestamp()
}

function getDaySchedule(completionTime) {
  return getOnboardingDaySchedule(completionTime, holidayDatesByYear.value)
}

function formatTargetDate(deadline) {
  return new Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  }).format(deadline)
}

async function loadHolidayCalendars(completionTimes) {
  const dates = (Array.isArray(completionTimes) ? completionTimes : [completionTimes])
    .filter(Boolean)
    .map((completionTime) => {
      const value = String(completionTime)
      return new Date(/^\d{4}-\d{2}-\d{2}$/.test(value) ? `${value}T00:00:00` : value)
    })
    .filter((date) => !Number.isNaN(date.getTime()))
  const years = [...new Set(dates.flatMap((date) => [
    date.getFullYear(),
    date.getFullYear() + 1
  ]))]

  if (!years.length) {
    holidayDatesByYear.value = {}
    holidayCalendarError.value = ''
    return
  }

  holidayCalendarLoading.value = true
  holidayCalendarError.value = ''
  try {
    const calendars = await Promise.all(
      years.map((year) => api.get('/v1/holidays', { params: { year } }))
    )
    holidayDatesByYear.value = Object.fromEntries(
      calendars.map((response, index) => {
        if (!Array.isArray(response.data)) {
          throw new Error(`Holiday response for ${years[index]} is not a list.`)
        }
        const applicableHolidays = response.data.filter((holiday) => (
          String(holiday.type || '').trim().replace(/\s+/g, ' ').toLowerCase() !== 'restricted holiday'
        ))
        const holidayDates = new Set(applicableHolidays.map((holiday) => {
          if (!/^\d{4}-\d{2}-\d{2}$/.test(holiday.date || '')) {
            throw new Error(`Holiday response for ${years[index]} contains an invalid date.`)
          }
          return holiday.date
        }))
        return [years[index], holidayDates]
      })
    )
  } catch (error) {
    holidayCalendarError.value = 'Holiday calendar unavailable'
    console.error('Unable to load the yearly holiday calendar:', error)
    $q.notify({
      type: 'negative',
      message: 'Unable to load holidays. Onboarding targets cannot be calculated.'
    })
  } finally {
    holidayCalendarLoading.value = false
  }
}

function getDayRows(dayNumber) {
  return getPhaseActivityRows(getApplicableWeek0Rows(), dayNumber)
}

function getCompletedCount(rowsList) {
  return (Array.isArray(rowsList) ? rowsList : []).filter((row) => isCompletedActivityStatus(row?.status)).length
}

function getDayCompletionTimestamp(dayNumber) {
  return getPhaseCompletionTimestamp(getDayRows(dayNumber))
}

function getDayPhaseStatus(dayNumber) {
  const phaseCounts = getPhaseCountsForLabel(`Day${dayNumber}`)
  const totalCount = phaseCounts.total || getDayRows(dayNumber).length
  const completedCount = phaseCounts.completed || getCompletedCount(getDayRows(dayNumber))

  if (totalCount === 0) {
    return { value: 'To be started', color: 'grey-6' }
  }

  if (completedCount === totalCount) {
    return { value: 'Completed', color: 'positive' }
  }

  const completionTime = getVdiActivationCompletionTimestamp()

  if (!completionTime) {
    return { value: 'To be started', color: 'grey-6' }
  }

  if (holidayCalendarError.value) {
    return { value: 'Calendar unavailable', color: 'negative' }
  }
  if (holidayCalendarLoading.value) {
    return { value: 'To be started', color: 'grey-6' }
  }

  const targetInfo = getDayTargetInfo(dayNumber)
  if (!targetInfo?.deadline) {
    return { value: 'To be started', color: 'grey-6' }
  }

  const phaseStartDate = new Date(targetInfo.deadline)
  phaseStartDate.setHours(0, 0, 0, 0)
  const phaseStart = phaseStartDate.getTime()
  if (currentTimestamp.value < phaseStart) {
    return { value: 'To be started', color: 'grey-6' }
  }

  if (currentTimestamp.value > targetInfo.deadline.getTime()) {
    return { value: 'Awaited', color: 'negative' }
  }

  return { value: 'In-progress', color: 'warning' }
}

function getWeek0PhaseStatus() {
  const phaseCounts = getPhaseCountsForLabel('Week0')
  const totalCount = phaseCounts.total || getApplicableWeek0Rows().length
  const completedCount = phaseCounts.completed || getCompletedCount(getApplicableWeek0Rows())

  if (totalCount === 0) {
    return { value: 'To be started', color: 'grey-6' }
  }

  if (completedCount === totalCount) {
    return { value: 'Completed', color: 'positive' }
  }

  if (getWeek0TargetInfo().isOverdue) {
    return { value: 'Overdue', color: 'negative' }
  }

  return { value: 'In-progress', color: 'warning' }
}




function hasCompletionDate(item) {
  return Boolean(item.completedDate)
}

function getTrackingItem(title) {
  return trackingData.find((item) => item.title === title)
}

function syncCredentialAndVcfCompletedDate(changedTitle, value) {
  const normalizedValue = value === null || value === undefined ? '' : String(value)
  const vcfItem = getTrackingItem('VCF Tracking')
  const clientItem = getTrackingItem('Client Credentials')

  if (!vcfItem || !clientItem) return

  if (changedTitle !== 'VCF Tracking' && changedTitle !== 'Client Credentials') {
    return
  }

  if (!normalizedValue) {
    vcfItem.completedDate = ''
    clientItem.completedDate = ''
  } else {
    vcfItem.completedDate = normalizedValue
    clientItem.completedDate = normalizedValue
  }

  vcfItem.status = 'Pending'
  clientItem.status = 'Pending'
}

function resetCredentialPhaseStatus(item) {
  if (item.title !== 'VCF Tracking' && item.title !== 'Client Credentials') {
    return
  }

  item.status = 'Pending'

  const counterpart = item.title === 'VCF Tracking'
    ? getTrackingItem('Client Credentials')
    : getTrackingItem('VCF Tracking')

  if (counterpart) {
    counterpart.status = 'Pending'
  }
}

function openDateSelector(event) {
  if (event?.target && typeof event.target.showPicker === 'function') {
    event.target.showPicker()
  }
}

function normalizeDateValue(value) {
  return value === null || value === undefined ? '' : String(value)
}

function validateDateAgainstRequested(item, value) {
  const normalizedValue = normalizeDateValue(value)
  if (!normalizedValue || !item.requestedDate) {
    return normalizedValue
  }

  return normalizedValue < item.requestedDate ? item.requestedDate : normalizedValue
}

function handleRequestedDateChange(item, value) {
  const normalizedValue = normalizeDateValue(value)
  item.requestedDate = normalizedValue

  if (item.title === 'VCF Tracking' || item.title === 'Client Credentials') {
    resetCredentialPhaseStatus(item)
    syncCredentialAndVcfCompletedDate(item.title, item.completedDate || '')
  } else {
    item.status = 'Pending'
  }

  if (item.completedDate && item.completedDate < item.requestedDate) {
    item.completedDate = item.requestedDate
  }
}

function handleCompletedDateChange(item, value) {
  const normalizedValue = validateDateAgainstRequested(item, value)
  item.completedDate = normalizedValue

  if (item.title === 'VCF Tracking' || item.title === 'Client Credentials') {
    resetCredentialPhaseStatus(item)
    syncCredentialAndVcfCompletedDate(item.title, normalizedValue)
  } else {
    item.status = 'Pending'
  }
}

function trackingStatusOptionsFor(item) {
  return hasCompletionDate(item) ? trackingStatusOptions : ['Pending']
}

async function handleTrackingStatusChange(item, value) {
  const isCredentialPhase = item.title === 'VCF Tracking' || item.title === 'Client Credentials'

  if (!isCredentialPhase && value === 'Completed' && !hasCompletionDate(item)) {
    item.status = 'Pending'
    $q.notify({
      type: 'warning',
      message: `${item.label2} is required before marking status as Completed.`
    })
    return
  }

  if (!isViewMode.value && !saving.value) {
    await saveChanges()
  }
}

async function handleOverallStatusChange(value) {
  if (value === 'Completed' && !isViewMode.value && !saving.value) {
    await saveChanges()
  }
}

async function sendBgvCompletionEmail() {
  if (!employeeId.value || emailSending.value) return

  const shouldSend = await new Promise((resolve) => {
    $q.dialog({
      title: 'Send Email',
      message: 'Send BGV completion email to the user now?',
      persistent: true,
      ok: {
        label: 'Send',
        color: 'primary'
      },
      cancel: {
        label: 'Cancel',
        flat: true
      }
    })
      .onOk(() => resolve(true))
      .onCancel(() => resolve(false))
      .onDismiss(() => resolve(false))
  })

  if (!shouldSend) return

  emailSending.value = true
  try {
    const { data } = await api.post(`/v1/users/onboarding/${employeeId.value}/bgv-completion-email`)
    $q.notify({ type: 'positive', message: data?.message || 'BGV completion email queued successfully' })
  } catch (error) {
    console.error('Error sending BGV completion email:', error)
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to send BGV completion email.' })
  } finally {
    emailSending.value = false
  }
}

function isClientCredentialsCompleted() {
  const clientCredentialItem = trackingData.find((item) => item.title === 'Client Credentials')
  const vcfItem = trackingData.find((item) => item.title === 'VCF Tracking')

  return [
    String(clientCredentialItem?.status || '').trim().toLowerCase(),
    String(vcfItem?.status || '').trim().toLowerCase()
  ].includes('completed')
}

async function sendClientCredentialEmail() {
  if (!employeeId.value || emailSending.value) return

  const shouldSend = await new Promise((resolve) => {
    $q.dialog({
      title: 'Send Email',
      message: 'Send client credential received email to the user now?',
      persistent: true,
      ok: {
        label: 'Send',
        color: 'primary'
      },
      cancel: {
        label: 'Cancel',
        flat: true
      }
    })
      .onOk(() => resolve(true))
      .onCancel(() => resolve(false))
      .onDismiss(() => resolve(false))
  })

  if (!shouldSend) return

  emailSending.value = true
  try {
    const { data } = await api.post(`/v1/users/onboarding/${employeeId.value}/client-credential-email`)
    $q.notify({ type: 'positive', message: data?.message || 'Client credential received email queued successfully' })
  } catch (error) {
    console.error('Error sending client credential received email:', error)
    console.error('Full Error:', error)
    console.error('Status:', error.response?.status)
    console.error('Response Data:', error.response?.data)
    console.error('Request URL:', error.config?.url)
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to send client credential received email.' })
  } finally {
    emailSending.value = false
  }
}

function timestampToDate(timestamp) {
  if (timestamp === null || timestamp === undefined || timestamp === '') {
    return ''
  }

  const numericTimestamp = Number(timestamp)
  const normalizedTimestamp = Number.isFinite(numericTimestamp)
    ? (String(Math.trunc(numericTimestamp)).length <= 10 ? numericTimestamp * 1000 : numericTimestamp)
    : timestamp

  const date = new Date(normalizedTimestamp)
  if (Number.isNaN(date.getTime())) {
    return String(timestamp)
  }

  return `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')}/${date.getFullYear()}`
}

async function fetchEmployeeOnboarding() {
  if (!employeeId.value) {
    trackingData.splice(0, trackingData.length)
    phaseCompletionDates.value = {}
    holidayDatesByYear.value = {}
    holidayCalendarError.value = ''
    Object.assign(employee, {
      name: '',
      employeeCode: '',
      email: '',
      teamLeadEmail: '',
      accountManagerEmail: '',
      client: '',
      project: '',
      teamLead: '',
      accountManager: '',
      joiningDate: ''
    })
    return
  }
  loading.value = true
  try {
    const [{ data }, week0Response] = await Promise.all([
      api.get(`/v1/users/onboarding/${employeeId.value}`),
      api.get('/v1/week0/tracker', {
        params: { employeeId: employeeId.value, employee_id: employeeId.value }
      }).catch(() => ({ data: { rows: [] } })),
    ])
    const state = snapshotState(data)
    applyState(state)
    week0Rows.value = Array.isArray(week0Response?.data?.rows) ? week0Response.data.rows : []
    week0PhaseCounts.value = week0Response?.data?.counts || {}
    phaseCompletionDates.value = week0Response?.data?.phaseCompletionDates || {}
    await loadHolidayCalendars([
      getTrackingItem('Client Credentials')?.completedDate,
      getVdiActivationCompletionTimestamp()
    ])
    savedState.value = state
  } catch (error) {
    console.error('Error fetching employee onboarding:', error)
    $q.notify({ type: 'negative', message: 'Unable to load employee onboarding details.' })
  } finally {
    loading.value = false
  }
}

async function saveChanges() {
  if (!employeeId.value) return

  const vcfItem = getTrackingItem('VCF Tracking')
  const clientItem = getTrackingItem('Client Credentials')
  if (vcfItem && clientItem) {
    const syncedDate = vcfItem.completedDate || clientItem.completedDate || ''
    vcfItem.completedDate = syncedDate
    clientItem.completedDate = syncedDate
  }

  const missingCompletionDateItem = trackingData.find(
    (item) => item.status === 'Completed' && !hasCompletionDate(item)
  )
  if (missingCompletionDateItem) {
    $q.notify({
      type: 'negative',
      message: `${missingCompletionDateItem.label2} is required before marking status as Completed.`
    })
    return
  }

  saving.value = true
  try {
    const { data } = await api.patch(`/v1/users/onboarding/${employeeId.value}`, {
      status: overallStatus.value,
      remarks: remarks.value,
      tracking: trackingData.map((item) => ({
        title: item.title,
        requestedDate: showRequestedDate(item) ? item.requestedDate : null,
        completedDate: item.completedDate,
        status: item.status || 'Pending'
      }))
    })
    const state = snapshotState(data)
    applyState(state)
    savedState.value = state
    await loadHolidayCalendars([
      getTrackingItem('Client Credentials')?.completedDate,
      getVdiActivationCompletionTimestamp()
    ])
    $q.notify({ type: 'positive', message: 'Onboarding details saved successfully.' })
  } catch (error) {
    console.error('Error saving employee onboarding:', error)
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to save onboarding details.' })
  } finally {
    saving.value = false
  }
}

function resetChanges() {
  if (savedState.value) applyState(savedState.value)
}

function openTrackerPhase(phaseLabel) {
  const normalized = String(phaseLabel || '').trim().toLowerCase()
  const pathMap = {
    week0: '/week-0',
    'vdi activation': '/vdi-activation',
    day1: '/day-1',
    day2: '/day-2',
    day3: '/day-3',
    day4: '/day-4',
    day5: '/day-5'
  }

  const selectedEmployeeCode = String(employee.employeeCode || employeeId.value || '').trim()
  const selectedEmployeeId = String(employeeId.value || selectedEmployeeCode || '').trim()
  router.push({
    path: pathMap[normalized] || '/week-0',
    query: {
      employeeId: selectedEmployeeCode,
      employeeCode: selectedEmployeeCode,
      userId: selectedEmployeeId,
      day: phaseLabel,
      mode: route.query.mode || 'edit'
    }
  })
}

watch(employeeId, fetchEmployeeOnboarding)
watch(
  () => [
    route.path,
    route.query.employeeId,
    route.query.userId,
    route.query.employeeCode,
    route.query.refresh,
    route.query.mode
  ],
  () => {
    if (route.path === '/employee-onboarding' || route.path.endsWith('/employee-onboarding')) {
      fetchEmployeeOnboarding()
    }
  },
  { immediate: true }
)
onMounted(fetchEmployeeOnboarding)
</script>

<style scoped>
.page-content {
  max-width: 1440px;
  margin: 8px auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.phase-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.phase-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.info-field {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  min-height: 54px;
}

.phase-label {
  min-height: 42px;
}

.rag-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.field-label {
  line-height: 20px;
  min-height: 20px;
}
.field-label .q-btn {
min-height: 20px;
line-height: 20px;
vertical-align: top;
}

.badge-container {
margin-top: 1px;
}

.phase-pending-count {
  display: block;
  line-height: 1.4;
  margin-top: 4px;
}

.tracker-text-btn {
min-height: unset !important;
padding: 0 !important;
}

.phase-legend {
display: flex;
gap: 12px;
}

.legend-badge {
padding: 6px 12px !important;
}
.clickable-label {
font-size: 12px;
font-weight: 700;
line-height: 1.5;
}
.non-clickable-label {
font-size: 12px;
font-weight: 700;
line-height: 1.5;
}


</style>
