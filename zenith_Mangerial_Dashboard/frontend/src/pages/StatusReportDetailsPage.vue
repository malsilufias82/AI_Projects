<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">{{ pageTitle }}</div>
        <div class="text-subtitle2 text-grey-7">Read-only daily status reports</div>
      </div>
      <q-btn flat no-caps icon="arrow_back" label="Back to Status Report" @click="router.push('/status-report')" />
    </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section class="row items-center justify-between q-gutter-sm">
        <div class="row items-center q-gutter-sm">
          <q-btn round flat dense icon="chevron_left" aria-label="Previous week" @click="changeWeek(-1)" />
          <div class="text-subtitle1 text-weight-medium">{{ weekLabel }}</div>
          <q-btn round flat dense icon="chevron_right" aria-label="Next week" @click="changeWeek(1)" />
          <q-btn flat dense no-caps label="Current Week" @click="showCurrentWeek" />
          <q-btn round flat dense icon="event" aria-label="Choose week">
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <q-date
                v-model="calendarDate"
                mask="YYYY-MM-DD"
                @update:model-value="setWeekFromDate"
              >
                <div class="row items-center justify-end q-pa-sm">
                  <q-btn v-close-popup flat label="Close" color="primary" />
                </div>
              </q-date>
            </q-popup-proxy>
          </q-btn>
        </div>
        <q-btn
          color="primary"
          unelevated
          no-caps
          icon="download"
          label="Export to Excel"
          :disable="!reports.length"
          @click="exportToExcel"
        />
      </q-card-section>
    </q-card>

    <q-card flat bordered>
      <q-table
        :rows="employeeRows"
        :columns="tableColumns"
        row-key="user_id"
        flat
        bordered
        :loading="loading"
        :pagination="{ rowsPerPage: 0 }"
        :rows-per-page-options="[0]"
        class="status-details-table"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td key="employee_name" :props="props" class="employee-cell align-top-cell">
              <div class="text-weight-medium">{{ props.row.employee_name }}</div>
              <div class="text-caption text-grey-7">{{ props.row.email }}</div>
            </q-td>
            <q-td key="team_lead" :props="props" class="team-lead-cell align-top-cell">
              {{ props.row.team_lead || entityName || '—' }}
            </q-td>
            <q-td v-for="day in weekDates" :key="day.date" :props="props" class="daily-status-cell align-top-cell">
              <q-input
                :model-value="statusText(props.row.reportsByDate[day.date])"
                type="textarea"
                readonly
                outlined
                dense
                autogrow
                class="readonly-status-field"
                input-style="min-width: 220px; max-height: 240px; overflow-y: auto; white-space: pre-wrap;"
              />
            </q-td>
          </q-tr>
        </template>
        <template #no-data>
          <div class="full-width q-pa-xl text-center text-grey-7">
            No daily status reports found for this week.
          </div>
        </template>
      </q-table>
    </q-card>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRoute, useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import XLSX from 'xlsx-js-style'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()

const reports = ref([])
const loading = ref(false)
const weekStart = ref(getMonday(new Date()))
const calendarDate = ref(formatDate(weekStart.value))
const entityType = computed(() => route.query.type === 'lead' ? 'lead' : 'employee')
const entityId = computed(() => typeof route.query.id === 'string' ? route.query.id : '')
const entityName = computed(() => typeof route.query.name === 'string' ? route.query.name : '')
const pageTitle = computed(() => entityType.value === 'lead'
  ? `${entityName.value || 'Team Lead'} — Team Status`
  : `${entityName.value || 'Employee'} — Daily Status`)
const weekLabel = computed(() => {
  const end = new Date(weekStart.value)
  end.setDate(end.getDate() + 4)
  return `${formatDate(weekStart.value)} – ${formatDate(end)}`
})
const weekDates = computed(() => Array.from({ length: 5 }, (_, index) => {
  const date = new Date(weekStart.value)
  date.setDate(date.getDate() + index)
  return {
    date: formatDate(date),
    label: `${date.toLocaleDateString('en-US', { weekday: 'short' })}\n${formatDate(date)}`
  }
}))
const tableColumns = computed(() => [
  { name: 'employee_name', label: 'Employee', field: 'employee_name', align: 'left' },
  { name: 'team_lead', label: 'Lead Name', field: 'team_lead', align: 'left' },
  ...weekDates.value.map(day => ({
    name: day.date,
    label: day.label,
    field: row => row.reportsByDate[day.date],
    align: 'left'
  }))
])
const employeeRows = computed(() => {
  const rowsByUser = new Map()
  for (const report of reports.value) {
    if (!rowsByUser.has(report.user_id)) {
      rowsByUser.set(report.user_id, {
        user_id: report.user_id,
        employee_name: report.employee_name,
        email: report.email,
        team_lead: report.team_lead,
        reportsByDate: {}
      })
    }
    rowsByUser.get(report.user_id).reportsByDate[report.date] = report
  }
  return Array.from(rowsByUser.values())
})

function getMonday (date) {
  const monday = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const day = monday.getDay()
  monday.setDate(monday.getDate() + (day === 0 ? -6 : 1 - day))
  return monday
}

function formatDate (date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function statusText (report) {
  if (!report) return ''
  if (report.leaveType && report.leaveType !== 'Working') {
    return `Leave: ${report.leaveType}`
  }
  return [
    `Completed:\n${report.completed || (report.completedNoUpdates ? 'No updates' : '')}`,
    `In Progress:\n${report.inProgress || (report.inProgressNoUpdates ? 'No updates' : '')}`,
    `Blockers:\n${report.blockers || (report.blockersNoUpdates ? 'No updates' : '')}`,
    `Next Plan:\n${report.nextPlan || (report.nextPlanNoUpdates ? 'No updates' : '')}`,
    `Notes:\n${report.notes || (report.notesNoUpdates ? 'No updates' : '')}`
  ].join('\n\n')
}

async function fetchReports () {
  if (!entityId.value) {
    reports.value = []
    return
  }

  const start = formatDate(weekStart.value)
  const endDate = new Date(weekStart.value)
  endDate.setDate(endDate.getDate() + 6)
  const params = {
    start,
    end: formatDate(endDate),
    [entityType.value === 'lead' ? 'team_lead_id' : 'user_id']: entityId.value
  }

  loading.value = true
  try {
    const { data } = await api.get('/v1/daily-reports/status-details', { params })
    reports.value = data
  } catch (error) {
    console.error('Error fetching status details:', error)
    $q.notify({ type: 'negative', message: 'Unable to load daily status reports.' })
  } finally {
    loading.value = false
  }
}

function changeWeek (offset) {
  const next = new Date(weekStart.value)
  next.setDate(next.getDate() + offset * 7)
  weekStart.value = next
  calendarDate.value = formatDate(next)
  fetchReports()
}

function setWeekFromDate (value) {
  if (!value) return
  weekStart.value = getMonday(new Date(`${value}T00:00:00`))
  calendarDate.value = formatDate(weekStart.value)
  fetchReports()
}

function showCurrentWeek () {
  weekStart.value = getMonday(new Date())
  calendarDate.value = formatDate(weekStart.value)
  fetchReports()
}

function exportToExcel () {
  const exportRows = employeeRows.value.map(row => {
    const exportRow = {
      Employee: row.employee_name,
      'Lead Name': row.team_lead || entityName.value || ''
    }
    for (const day of weekDates.value) {
      exportRow[day.date] = statusText(row.reportsByDate[day.date])
    }
    return exportRow
  })
  const worksheet = XLSX.utils.json_to_sheet(exportRows)
  worksheet['!cols'] = [{ wch: 28 }, { wch: 28 }, ...weekDates.value.map(() => ({ wch: 55 }))]
  const range = XLSX.utils.decode_range(worksheet['!ref'])
  for (let row = range.s.r; row <= range.e.r; row += 1) {
    for (let column = range.s.c; column <= range.e.c; column += 1) {
      const cell = worksheet[XLSX.utils.encode_cell({ r: row, c: column })]
      if (cell) {
        cell.s = {
          alignment: {
            vertical: 'top',
            wrapText: column >= 2
          }
        }
      }
    }
  }
  worksheet['!rows'] = [
    { hpt: 24 },
    ...employeeRows.value.map(row => ({
      hpt: Math.max(90, ...weekDates.value.map(day => {
        const status = statusText(row.reportsByDate[day.date])
        const wrappedLines = status.split('\n').reduce((total, line) => total + Math.max(1, Math.ceil(line.length / 55)), 0)
        return wrappedLines * 15
      }))
    }))
  ]
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Daily Status')
  XLSX.writeFile(workbook, `Daily_Status_${formatDate(weekStart.value)}.xlsx`, { cellStyles: true })
}

watch(
  () => [route.query.type, route.query.id],
  fetchReports
)

onMounted(fetchReports)
</script>

<style scoped>
.status-details-table :deep(.q-table__middle) {
  overflow-x: auto;
}

.status-details-table :deep(th) {
  white-space: pre-line;
  min-width: 220px;
}

.status-details-table :deep(th:first-child),
.status-details-table :deep(th:nth-child(2)) {
  min-width: 180px;
}

.readonly-status-field {
  min-width: 220px;
}

.team-lead-cell,
.employee-cell {
  min-width: 180px;
  white-space: nowrap;
}

.align-top-cell {
  vertical-align: top;
}

.align-top-cell :deep(.q-td__div),
.align-top-cell :deep(.q-field__control) {
  align-items: flex-start;
}

.daily-status-cell :deep(.q-field__control) {
  align-items: flex-start;
}
</style>
