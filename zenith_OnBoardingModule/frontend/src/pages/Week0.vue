<template>
  <q-page class="bg-grey-2 q-pa-lg">
    <div class="page-content q-gutter-y-lg">
      <div class="page-header">
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">{{ pageTitle }}</h1>
          <p class="text-grey-7 q-mt-sm q-mb-none">
            Track onboarding items with activity details, relevant links, technology/project scope, comments, and status.
          </p>
          <div class="q-mt-sm flex items-center q-gutter-sm">
            <q-badge v-if="showSaveBadge" :color="saveIndicatorColor" rounded>
              {{ saveIndicatorLabel }}
            </q-badge>
            <q-toggle
              v-model="showAllTasks"
              color="primary"
              left-label
              :label="showAllTasks ? 'All tasks' : 'Relevant page tasks'"
            />
          </div>
        </div>
        <div class="row q-gutter-sm">
          <q-btn outline icon="arrow_back" label="Back" :to="backTo" />
          <q-btn color="primary" icon="add" label="Add Activity" @click="addActivity" />
        </div>
      </div>

      <q-banner v-if="dayActivitiesLocked" class="bg-blue-1 text-primary" rounded>
        Day 1–5 activities are locked until all VDI Activation activities are completed.
      </q-banner>

      <q-card flat bordered>
        <q-card-section>
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-12 col-sm-4">
              <q-card flat bordered class="count-card">
                <q-card-section class="q-py-sm q-px-md">
                  <div class="text-caption text-grey-7">Total activities</div>
                  <div class="text-h6 q-mt-xs">{{ totalActivityCount }}</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-12 col-sm-4">
              <q-card flat bordered class="count-card count-card-success">
                <q-card-section class="q-py-sm q-px-md">
                  <div class="text-caption text-grey-7">Completed</div>
                  <div class="text-h6 q-mt-xs">{{ completedActivityCount }}</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-12 col-sm-4">
              <q-card flat bordered class="count-card count-card-warning">
                <q-card-section class="q-py-sm q-px-md">
                  <div class="text-caption text-grey-7">Pending</div>
                  <div class="text-h6 q-mt-xs">{{ pendingActivityCount }}</div>
                </q-card-section>
              </q-card>
            </div>
          </div>
          <div class="text-subtitle2 q-mb-sm">Filter by column</div>
          <div class="row q-col-gutter-sm q-mb-md">
            <div
              v-for="filter in textFilters"
              :key="filter.name"
              class="col-12 col-sm-6 col-md-3"
            >
              <q-input
                v-model="columnFilters[filter.name]"
                dense
                outlined
                clearable
                :label="`Filter ${filter.label}`"
                @keydown.stop
              />
            </div>
            <div class="col-12 col-sm-6 col-md-3">
              <q-select
                v-model="columnFilters.status"
                dense
                outlined
                clearable
                options-dense
                :options="statusFilterOptions"
                emit-value
                map-options
                label="Filter Status"
              />
            </div>
          </div>
          <q-table
            flat
            bordered
            :rows="filteredRows"
            :columns="columns"
            row-key="id"
            :pagination="{ rowsPerPage: 0 }"
            :row-class="getRowClass"
            hide-bottom
          >
            <template #body-cell-activity="props">
              <q-td :props="props">
                <q-input
                  v-model="props.row.activity"
                  type="textarea"
                  autogrow
                  dense
                  outlined
                  :disable="isCompletedStatus(props.row.status) || showAllTasks || dayActivitiesLocked"
                  debounce="400"
                  placeholder="Enter activity"
                  @update:model-value="scheduleAutoSave"
                />
              </q-td>
            </template>

            <template #body-cell-action="props">
              <q-td :props="props">
                <q-input
                  v-model="props.row.action"
                  type="textarea"
                  autogrow
                  dense
                  outlined
                  :disable="isCompletedStatus(props.row.status) || showAllTasks || dayActivitiesLocked"
                  debounce="400"
                  placeholder="Enter action"
                  @update:model-value="scheduleAutoSave"
                />
              </q-td>
            </template>

            <template #body-cell-technology="props">
              <q-td :props="props">
                <q-input
                  v-model="props.row.technology"
                  dense
                  outlined
                  :disable="isCompletedStatus(props.row.status) || showAllTasks || dayActivitiesLocked"
                  placeholder="Technology"
                  debounce="400"
                  @update:model-value="scheduleAutoSave"
                />
              </q-td>
            </template>

            <template #body-cell-project="props">
              <q-td :props="props">
                <q-input
                  v-model="props.row.project"
                  dense
                  outlined
                  :disable="isCompletedStatus(props.row.status) || showAllTasks || dayActivitiesLocked"
                  placeholder="Project"
                  debounce="400"
                  @update:model-value="scheduleAutoSave"
                />
              </q-td>
            </template>

            <template #body-cell-comment="props">
              <q-td :props="props">
                <q-input
                  v-model="props.row.comment"
                  type="textarea"
                  autogrow
                  dense
                  outlined
                  :disable="isCompletedStatus(props.row.status) || showAllTasks || dayActivitiesLocked"
                  debounce="400"
                  placeholder="Enter comment"
                  @update:model-value="scheduleAutoSave"
                />
              </q-td>
            </template>

            <template #body-cell-status="props">
              <q-td :props="props">
                <q-select
                  v-model="props.row.status"
                  dense
                  outlined
                  :disable="showAllTasks || isCompletedStatus(props.row.status) || dayActivitiesLocked"
                  :options="statusOptions"
                  label="Status"
                  emit-value
                  map-options
                  @update:model-value="scheduleAutoSave"
                />
                <q-btn
                  v-if="isCompletedStatus(props.row.status) && !showAllTasks && !dayActivitiesLocked"
                  flat
                  dense
                  size="sm"
                  color="primary"
                  class="q-mt-xs row-edit-link"
                  label="Edit response"
                  @click.stop="reopenCompletedActivity(props.row)"
                />
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute } from 'vue-router'
import { Notify, useQuasar } from 'quasar'
import { api } from 'boot/axios'
import { isVdiActivationActivityRow } from 'src/utils/onboardingSchedule'

defineOptions({
  name: 'WeekZeroPage'
})

const defaultColumns = [
  { name: 'day', label: 'Day', field: 'day', align: 'left', classes: 'wrap-cell', headerClasses: 'wrap-cell' },
  { name: 'activity', label: 'Activity', field: 'activity', align: 'left', classes: 'wrap-cell', headerClasses: 'wrap-cell' },
  { name: 'action', label: 'Actions', field: 'action', align: 'left', classes: 'wrap-cell', headerClasses: 'wrap-cell' },
  { name: 'technology', label: 'Technology', field: 'technology', align: 'left' },
  { name: 'project', label: 'Project', field: 'project', align: 'left' },
  { name: 'comment', label: 'Comment', field: 'comment', align: 'left', classes: 'wrap-cell', headerClasses: 'wrap-cell' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' }
]

const columns = ref([...defaultColumns])
const statusOptions = [
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Pending', value: 'Pending' },
  { label: 'Not Applicable', value: 'Not Applicable' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Blocked', value: 'Blocked' }
]
const statusFilterOptions = statusOptions
const textFilters = [
  { name: 'day', label: 'Day' },
  { name: 'activity', label: 'Activity' },
  { name: 'action', label: 'Actions' },
  { name: 'technology', label: 'Technology' },
  { name: 'project', label: 'Project' },
  { name: 'comment', label: 'Comment' }
]

const rows = ref([])
const showAllTasks = ref(false)
const columnFilters = ref({
  day: '',
  activity: '',
  action: '',
  technology: '',
  project: '',
  comment: '',
  status: null
})
let autoSaveTimer = null
let autoSaveInFlight = false
let saveBadgeTimer = null
const saveIndicator = ref('Saved')
const showSaveBadge = ref(true)
const route = useRoute()
const $q = useQuasar()

const displayRows = computed(() => {
  if (showAllTasks.value) return rows.value
  return rows.value.filter((row) => matchesCurrentPage(row))
})
const isDayPhase = computed(() => /^Day[1-5]$/i.test(phaseDayLabel.value))
const vdiActivationCompleted = computed(() => {
  const activationRows = rows.value.filter((row) => isVdiActivationActivityRow(row))
  return activationRows.length > 0 &&
    activationRows.every((row) => isCompletedStatus(row?.status))
})
const dayActivitiesLocked = computed(() => isDayPhase.value && !vdiActivationCompleted.value)
const filteredRows = computed(() => displayRows.value.filter((row) => {
  for (const { name } of textFilters) {
    const query = String(columnFilters.value[name] || '').trim().toLowerCase()
    if (query && !String(row?.[name] || '').toLowerCase().includes(query)) {
      return false
    }
  }

  const statusFilter = columnFilters.value.status
  return !statusFilter || normalizeStatus(row?.status) === statusFilter
}))

const saveIndicatorLabel = computed(() => {
  if (String(route.query.mode || '').toLowerCase() === 'view') return 'View mode'
  return saveIndicator.value
})

const saveIndicatorColor = computed(() => {
  if (String(route.query.mode || '').toLowerCase() === 'view') return 'grey-6'
  if (saveIndicator.value === 'Saving...') return 'warning'
  if (saveIndicator.value === 'Unsaved changes') return 'negative'
  return 'positive'
})

const phaseDayLabel = computed(() => {
  const qDay = String(route.query.day || '').trim()
  if (qDay) return qDay

  const path = String(route.path || '').toLowerCase()
  if (path.endsWith('/vdi-activation')) return 'VDI Activation'
  if (path.endsWith('/day-1')) return 'Day1'
  if (path.endsWith('/day-2')) return 'Day2'
  if (path.endsWith('/day-3')) return 'Day3'
  if (path.endsWith('/day-4')) return 'Day4'
  if (path.endsWith('/day-5')) return 'Day5'
  return 'Week0'
})

const pageTitle = computed(() => `${phaseDayLabel.value} Activity Tracker`)
const totalActivityCount = computed(() => displayRows.value.length)
const completedActivityCount = computed(() => displayRows.value.filter((row) => isCompletedStatus(row?.status)).length)
const pendingActivityCount = computed(() => displayRows.value.filter((row) => !isCompletedStatus(row?.status)).length)

const backTo = computed(() => ({
  path: '/employee-onboarding',
  query: {
    employeeId: route.query.employeeId || route.query.employeeCode || route.query.userId || '',
    employeeCode: route.query.employeeCode || route.query.employeeId || route.query.userId || '',
    userId: route.query.userId || route.query.employeeId || route.query.employeeCode || '',
    mode: route.query.mode || 'edit',
    refresh: Date.now()
  }
}))

function normalizeStatus(status) {
  const normalized = String(status || '').trim().toLowerCase()
  if (['completed', 'complete'].includes(normalized)) return 'Completed'
  if (['not applicable', 'not_applicable', 'n/a'].includes(normalized)) return 'Not Applicable'
  if (['in progress', 'in-progress', 'in_progress', 'inprogress'].includes(normalized)) return 'In Progress'
  if (normalized === 'blocked') return 'Blocked'
  return 'Pending'
}

function isCompletedStatus(status) {
  return ['Completed', 'Not Applicable'].includes(normalizeStatus(status))
}

function matchesCurrentPage(row) {
  const currentDay = String(phaseDayLabel.value || '').trim().toLowerCase()
  const dayValue = row?.day
  const normalizedTarget = String(dayValue || '').trim().toLowerCase().replace(/\s+/g, '').replace(/-/g, '')

  if (!currentDay) return true
  if (!normalizedTarget) return false

  if (currentDay === 'week0') {
    if (isVdiActivationActivityRow(row)) return false
    return ['week0', 'day0', 'week0a', 'day0a'].includes(normalizedTarget)
  }

  const currentPageKey = currentDay.replace(/\s+/g, '').replace(/-/g, '')
  if (currentPageKey === 'vdiactivation') {
    return isVdiActivationActivityRow(row)
  }
  return normalizedTarget === currentPageKey || normalizedTarget === `day${currentPageKey.replace('day', '')}`
}

function getRowClass(row) {
  return isCompletedStatus(row?.status) ? 'completed-row' : ''
}

function reopenCompletedActivity(row) {
  if (!row) return
  row.status = 'Pending'
  scheduleAutoSave()
}

function setSaveIndicator(nextValue) {
  saveIndicator.value = nextValue

  if (saveBadgeTimer) {
    clearTimeout(saveBadgeTimer)
    saveBadgeTimer = null
  }

  if (String(route.query.mode || '').toLowerCase() === 'view') {
    showSaveBadge.value = true
    return
  }

  if (nextValue === 'Saved') {
    showSaveBadge.value = true
    saveBadgeTimer = setTimeout(() => {
      showSaveBadge.value = false
      saveBadgeTimer = null
    }, 10000)
    return
  }

  showSaveBadge.value = true
}

function addActivity() {
  const adminMessage = `Activities can be displayed by admin, please mail the relevant activity with following information to the admin;\nActivity:\nAction:\nTechnology:\nProject:`

  $q.dialog({
    title: 'Add Activity',
    message: adminMessage,
    html: false,
    persistent: true,
    ok: {
      label: 'OK',
      color: 'primary'
    }
  })
}

function normalizeRows(rawRows) {
  return (Array.isArray(rawRows) ? rawRows : []).map((row, index) => ({
    id: Number(row?.id) || index + 1,
    day: String(row?.day || ''),
    activity: String(row?.activity || ''),
    action: String(row?.action || row?.relevantLink || ''),
    relevantLink: String(row?.relevantLink || row?.action || ''),
    technology: String(row?.technology || 'Applicable for all'),
    project: String(row?.project || 'Applicable for all projects'),
    comment: String(row?.comment ?? row?.blocker ?? ''),
    status: normalizeStatus(row?.status),
    completedAt: row?.completedAt || null,
    updatedAt: row?.updatedAt || null,
    createdAt: row?.createdAt || null
  }))
}

function scheduleAutoSave() {
  setSaveIndicator('Unsaved changes')
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
  autoSaveTimer = setTimeout(() => {
    autoSaveTimer = null
    saveWeek0Tracker()
  }, 500)
}

async function flushPendingAutoSave() {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
    autoSaveTimer = null
  }

  if (!rows.value.length || autoSaveInFlight) {
    return
  }

  await saveWeek0Tracker()
}

function serializeRow(row) {
  return {
    id: Number(row?.id) || 0,
    day: String(row?.day || phaseDayLabel.value || ''),
    activity: String(row?.activity || ''),
    action: String(row?.action || row?.relevantLink || ''),
    relevantLink: String(row?.action || row?.relevantLink || ''),
    technology: String(row?.technology || 'Applicable for all'),
    project: String(row?.project || 'Applicable for all projects'),
    projects: String(row?.project || 'Applicable for all projects'),
    comment: String(row?.comment ?? row?.blocker ?? ''),
    status: normalizeStatus(row?.status)
  }
}

async function saveWeek0Tracker() {
  if (autoSaveInFlight || rows.value.length === 0 || dayActivitiesLocked.value) return
  autoSaveInFlight = true
  setSaveIndicator('Saving...')
  try {
    const payloadRows = rows.value.map((row) => serializeRow(row))
    const resolvedEmployeeId = String(
      route.query.employeeCode || route.query.employeeId || route.query.userId || route.query.id || ''
    ).trim()
    const { data } = await api.put('/v1/week0/tracker', {
      columns: columns.value,
      rows: payloadRows,
      employeeId: resolvedEmployeeId,
      employee_id: resolvedEmployeeId
    })
    columns.value = Array.isArray(data?.columns) && data.columns.length > 0 ? data.columns : [...defaultColumns]
    rows.value = normalizeRows(data?.rows)
    setSaveIndicator('Saved')
  } catch (error) {
    console.error('Failed to auto-save Week0 tracker:', error)
    setSaveIndicator('Unsaved changes')
    Notify.create({
      type: 'warning',
      message: 'Unable to save Week0 tracker changes.'
    })
  } finally {
    autoSaveInFlight = false
  }
}

async function fetchWeek0Tracker() {
  try {
    const resolvedEmployeeId = String(
      route.query.employeeCode || route.query.employeeId || route.query.employee_id || route.query.userId || route.query.id || ''
    ).trim()
    rows.value = []
    setSaveIndicator('Saved')
    const { data } = await api.get('/v1/week0/tracker', {
      params: {
        employeeId: resolvedEmployeeId,
        employee_id: resolvedEmployeeId,
      }
    })
    columns.value = Array.isArray(data?.columns) && data.columns.length > 0 ? data.columns : [...defaultColumns]
    rows.value = normalizeRows(data?.rows)
    setSaveIndicator('Saved')
  } catch (error) {
    console.error('Failed to load Week0 tracker:', error)
    columns.value = [...defaultColumns]
    rows.value = []
    setSaveIndicator('Unsaved changes')
    Notify.create({
      type: 'warning',
      message: 'Unable to load Week0 tracker from server.'
    })
  }
}

onMounted(() => {
  fetchWeek0Tracker()
})

onBeforeRouteLeave(async () => {
  await flushPendingAutoSave()
})

watch(() => route.fullPath, () => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
    autoSaveTimer = null
  }
  rows.value = []
  fetchWeek0Tracker()
})
</script>

<style scoped>
:deep(.completed-row) {
  background: rgba(76, 175, 80, 0.12);
}

:deep(.completed-row td) {
  color: #2e7d32;
}

.row-edit-link {
  min-height: 20px;
  padding: 0;
  font-size: 11px;
  text-transform: none;
}

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

:deep(.wrap-cell) {
  white-space: normal;
  word-break: break-word;
}

.count-card {
  height: 100%;
}

.count-card-success {
  border-color: rgba(76, 175, 80, 0.4);
}

.count-card-warning {
  border-color: rgba(255, 193, 7, 0.4);
}

</style>
