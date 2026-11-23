<template>
  <q-page class="q-pa-md status-report-page">
    <div class="text-h4 text-weight-bold q-mb-md">Status Update Analytics</div>
    <div class="text-subtitle1 text-grey-6 q-mb-lg">Daily Status Update Reports & Analysis</div>

    <!-- Date Range Filter -->
    <q-card class="q-mb-md bg-white chart-card no-shadow">
      <q-card-section class="q-pa-md">
        <div class="row items-center q-col-gutter-md">
          <div class="col-auto" v-if="dateRange.preset === 'custom'">
            <div class="text-subtitle2 text-weight-medium">Date Range:</div>
          </div>
          <div class="col-auto">
            <q-btn-group unelevated class="chart-card">
              <q-btn
                label="Present Week"
                :color="dateRange.preset === 'presentWeek' ? 'primary' : 'grey-7'"
                flat
                dense
                @click="setDateRange('presentWeek')"
              >
                <q-tooltip>View current week (Monday to Friday)</q-tooltip>
              </q-btn>
              <q-btn
                label="Last 1 Month"
                :color="dateRange.preset === '1month' ? 'primary' : 'grey-7'"
                flat
                dense
                @click="setDateRange('1month')"
              >
                <q-tooltip>View data from the last 30 days</q-tooltip>
              </q-btn>
              <q-btn
                label="Customize Range"
                :color="dateRange.preset === 'custom' ? 'primary' : 'grey-7'"
                flat
                dense
                @click="setDateRange('custom')"
              >
                <q-tooltip>Select custom date range</q-tooltip>
              </q-btn>
            </q-btn-group>
          </div>
          <div class="col-auto" v-if="dateRange.preset === 'custom'">
            <q-input
              v-model="dateRange.from"
              label="From"
              outlined
              dense
              style="min-width: 180px"
              clearable
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="dateRange.from" mask="YYYY-MM-DD">
                      <div class="row items-center justify-end q-gutter-sm">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>
          <div class="col-auto" v-if="dateRange.preset === 'custom'">
            <q-input
              v-model="dateRange.to"
              label="To"
              outlined
              dense
              style="min-width: 180px"
              clearable
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="dateRange.to" mask="YYYY-MM-DD">
                      <div class="row items-center justify-end q-gutter-sm">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>
          <div class="col-auto" v-if="dateRange.preset === 'custom'">
            <q-btn
              @click="applyDateFilter"
              label="Apply"
              color="primary"
              :disable="!dateRange.from || !dateRange.to"
              :loading="filterLoading"
            />
          </div>
          <div class="col-auto">
            <q-btn
              @click="resetDateRange"
              icon="refresh"
              flat
              dense
              :disable="dateRange.preset === 'presentWeek'"
            >
              <q-tooltip>Reset to Present Week</q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Sheet Upload Section -->
    <q-card class="q-mb-md hidden bg-white chart-card no-shadow">
      <q-card-section class="q-pa-md">
        <div class="text-h6 q-mb-md">Upload Status Sheet</div>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <q-file
              v-model="uploadedFile"
              label="Select Excel File"
              accept=".xlsx,.xls"
              outlined
              dense
              @update:model-value="handleFileUpload"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
          </div>
          <div class="col-12 col-md-4">
            <q-select
              v-model="selectedTeam"
              :options="teamOptions"
              label="Team Type"
              outlined
              dense
              emit-value
              map-options
              :disable="!uploadedFile"
            >
              <template v-slot:prepend>
                <q-icon name="groups" />
              </template>
              <template v-slot:after>
                <q-icon
                  v-if="autoDetectedTeam"
                  name="auto_awesome"
                  color="positive"
                  size="sm"
                >
                  <q-tooltip>Auto-detected from filename</q-tooltip>
                </q-icon>
              </template>
            </q-select>
          </div>
          <div class="col-12 col-md-4">
            <q-btn
              color="primary"
              label="Process Sheet"
              :disable="!uploadedFile || !selectedTeam"
              @click="processSheet"
              :loading="processing"
            />
          </div>
        </div>
        <div v-if="uploadedFile" class="q-mt-sm text-caption text-grey-6">
          Selected file: {{ uploadedFile.name }}
        </div>
      </q-card-section>
    </q-card>

    <!-- Team Lead Table -->
    <div class="row q-col-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card class="bg-white text-dark chart-card no-shadow">
          <q-card-section class="q-pa-md">
            <div class="row items-center justify-between">
              <div>
                <div class="text-h6">Team Completion Status</div>
                <div class="text-caption text-grey-6">{{ weekInfo.week_start }} to {{ weekInfo.current_date }}</div>
              </div>
              <div class="row items-center q-gutter-md">
                <div class="text-caption text-grey-6">
                  Deadline: {{ new Date(weekInfo.deadline).toLocaleString() }}
                </div>
                <q-btn
                  @click="exportToExcel"
                  label="Export"
                  color="primary"
                  icon-right="download"
                  dense
                  unelevated
                />
              </div>
            </div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-table
              :rows="teamData"
              :columns="teamColumns"
              row-key="team_lead"
              flat
              bordered
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:header-cell="props">
                <q-th :props="props" style="font-size: 20px; font-weight: bold;">
                  <template v-if="props.col.name === 'team_lead'">
                    <q-btn
                      flat
                      dense
                      :icon="parentExpanded ? 'expand_less' : 'expand_more'"
                      @click="toggleParentExpanded"
                      class="q-mr-xs"
                      size="lg"
                    />
                    Team Lead
                  </template>
                  <template v-else>
                    {{ props.col.label }}
                  </template>
                </q-th>
              </template>
              <template v-slot:body="props">
                <q-tr :props="props" v-show="parentExpanded">
                  <q-td key="team_lead" :props="props" style="font-size: 16px; font-weight: 500;">
                    <q-btn
                      flat
                      dense
                      :icon="props.expand ? 'expand_less' : 'expand_more'"
                      @click="props.expand = !props.expand"
                      class="q-mr-sm"
                      size="lg"
                    />
                    <router-link
                      v-if="props.row.team_lead_id"
                      class="member-status-link"
                      :to="statusDetailsRoute('lead', props.row.team_lead_id, props.row.team_lead)"
                    >{{ props.row.team_lead }}</router-link>
                    <span v-else>{{ props.row.team_lead }}</span>
                  </q-td>
                  <q-td key="total_team_members" :props="props" style="font-size: 16px; font-weight: 500;">
                    {{ props.row.total_team_members }}
                  </q-td>
                  <q-td key="completed_count" :props="props" style="font-size: 16px; font-weight: 500;">
                    {{ props.row.completed_count || 0 }}
                  </q-td>
                  <q-td key="pending_count" :props="props" style="font-size: 16px; font-weight: 500;">
                    {{ props.row.pending_count || 0 }}
                  </q-td>
                  <q-td key="is_complete" :props="props" style="font-size: 16px; font-weight: 500;">
                    <q-badge :color="props.row.is_complete ? 'positive' : 'warning'">
                      {{ props.row.is_complete ? 'Completed' : 'Pending' }}
                    </q-badge>
                  </q-td>
                </q-tr>
                <q-tr v-show="props.expand && parentExpanded" :props="props">
                  <q-td colspan="100%" class="q-pa-md bg-grey-1">
                    <div class="text-subtitle2 q-mb-sm" style="font-size: 17px; font-weight: 600;">Pending Members ({{ props.row.pending_count }}):</div>
                    <q-list class="q-mb-md">
                      <q-item v-for="member in props.row.pending_member_details" :key="member.id || member.name" class="q-pa-sm">
                        <q-item-section avatar>
                          <q-icon name="person" color="negative" size="md" />
                        </q-item-section>
                        <q-item-section class="items-start">
                          <router-link
                            v-if="member.id"
                            class="member-status-link"
                            :to="statusDetailsRoute('employee', member.id, member.name)"
                          >{{ member.name }}</router-link>
                          <q-item-label v-else style="font-size: 16px;">{{ member.name }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item v-if="props.row.pending_member_details.length === 0" class="q-pa-sm">
                        <q-item-section>
                          <q-item-label class="text-grey-6" style="font-size: 16px;">No pending members</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>

                    <div class="text-subtitle2 q-mb-sm" style="font-size: 17px; font-weight: 600;">Completed Members ({{ props.row.completed_count }}):</div>
                    <q-list>
                      <q-item v-for="member in props.row.completed_member_details" :key="member.id || member.name" class="q-pa-sm">
                        <q-item-section avatar>
                          <q-icon name="person" color="positive" size="md" />
                        </q-item-section>
                        <q-item-section class="items-start">
                          <router-link
                            v-if="member.id"
                            class="member-status-link"
                            :to="statusDetailsRoute('employee', member.id, member.name)"
                          >{{ member.name }}</router-link>
                          <q-item-label v-else style="font-size: 16px;">{{ member.name }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item v-if="props.row.completed_member_details.length === 0" class="q-pa-sm">
                        <q-item-section>
                          <q-item-label class="text-grey-6" style="font-size: 16px;">No completed members</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="row q-col-gutter-md q-mb-lg hidden">
      <!-- Daily Fill Rate Chart -->
      <div class="col-12 col-md-6">
        <q-card class="bg-white text-dark chart-card no-shadow">
          <q-card-section class="q-pa-md">
            <div class="text-h6">Daily Fill Rate</div>
            <div class="text-caption text-grey-6">Status update compliance rate</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div ref="fillRateChart" style="height: 300px;"></div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-btn flat color="primary" label="View Details" @click="openFillRateDialog" />
          </q-card-section>
        </q-card>
      </div>

      <!-- Leave Analysis Chart -->
      <div class="col-12 col-md-6">
        <q-card class="bg-white text-dark chart-card no-shadow">
          <q-card-section class="q-pa-md">
            <div class="text-h6">Leave Analysis</div>
            <div class="text-caption text-grey-6">Weekly leave patterns (12 weeks)</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div ref="leaveChart" style="height: 300px;"></div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-btn flat color="primary" label="View Details" @click="openLeaveDialog" />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Full Width Chart -->
    <div class="row q-col-gutter-md q-mb-lg hidden">
      <div class="col-12">
        <q-card class="bg-white text-dark chart-card no-shadow">
          <q-card-section class="q-pa-md">
            <div class="text-h6">Weekly Status Breakdown</div>
            <div class="text-caption text-grey-6">Daily status update compliance for current week</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div ref="productivityChart" style="height: 350px;"></div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-btn flat color="primary" label="View Details" @click="openProductivityDialog" />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Fill Rate Dialog -->
    <q-dialog v-model="fillRateDialog" maximized>
      <q-card class="analytics-dialog">
        <q-card-section class="q-pa-md bg-primary text-white">
          <div class="row items-center">
            <div class="text-h6">Daily Fill Rate Details</div>
            <q-space />
            <q-btn flat round dense icon="close" v-close-popup />
          </div>
        </q-card-section>
        <q-card-section class="q-pa-md">
          <div class="row q-col-gutter-lg">
            <div class="col-12 col-md-6">
              <div ref="fillRateChartDialog" style="height: 400px;"></div>
            </div>
            <div class="col-12 col-md-6">
              <div class="text-h6 q-mb-md">Fill Rate Breakdown</div>
              <q-list separator>
                <q-item v-for="item in fillRateData" :key="item.name">
                  <q-item-section avatar>
                    <q-avatar :style="{ backgroundColor: item.color }" text-color="white">
                      {{ item.value }}%
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ item.name }}</q-item-label>
                    <q-item-label caption>{{ item.count }} employees</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-weight-bold">{{ item.share }}</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Leave Dialog -->
    <q-dialog v-model="leaveDialog" maximized>
      <q-card class="analytics-dialog">
        <q-card-section class="q-pa-md bg-primary text-white">
          <div class="row items-center">
            <div class="text-h6">Leave Analysis Details</div>
            <q-space />
            <q-btn flat round dense icon="close" v-close-popup />
          </div>
        </q-card-section>
        <q-card-section class="q-pa-md">
          <div class="row q-col-gutter-lg">
            <div class="col-12 col-md-6">
              <div ref="leaveChartDialog" style="height: 400px;"></div>
            </div>
            <div class="col-12 col-md-6">
              <div class="text-h6 q-mb-md">Leave Summary</div>
              <q-list separator>
                <q-item v-for="item in leaveData" :key="item.week">
                  <q-item-section>
                    <q-item-label>{{ item.week }}</q-item-label>
                    <q-item-label caption>{{ item.details }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-weight-bold">{{ item.total }} days</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Productivity Dialog -->
    <q-dialog v-model="productivityDialog" maximized>
      <q-card class="analytics-dialog">
        <q-card-section class="q-pa-md bg-primary text-white">
          <div class="row items-center">
            <div class="text-h6">Weekly Status Breakdown Details</div>
            <q-space />
            <q-btn flat round dense icon="close" v-close-popup />
          </div>
        </q-card-section>
        <q-card-section class="q-pa-md">
          <div class="row q-col-gutter-lg">
            <div class="col-12">
              <div ref="productivityChartDialog" style="height: 400px;"></div>
            </div>
          </div>
          <q-card-section class="q-pt-md">
            <div class="text-h6 q-mb-md">Weekly Status Metrics</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-3">
                <q-card class="bg-primary text-white">
                  <q-card-section>
                    <div class="text-subtitle2">Total Entries</div>
                    <div class="text-h4 text-weight-bold">{{ productivityMetrics.totalEntries }}</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-md-3">
                <q-card class="bg-positive text-white">
                  <q-card-section>
                    <div class="text-subtitle2">Fill Rate</div>
                    <div class="text-h4 text-weight-bold">{{ productivityMetrics.fillRate }}%</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-md-3">
                <q-card class="bg-negative text-white">
                  <q-card-section>
                    <div class="text-subtitle2">Unfilled</div>
                    <div class="text-h4 text-weight-bold">{{ productivityMetrics.unfilled }}</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-md-3">
                <q-card class="bg-warning text-white">
                  <q-card-section>
                    <div class="text-subtitle2">Leave Days</div>
                    <div class="text-h4 text-weight-bold">{{ productivityMetrics.leave }}</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { api } from 'src/boot/axios'
import XLSX from 'xlsx-js-style'

// Date Range
const dateRange = ref({
  from: '',
  to: '',
  preset: 'presentWeek'
})
const statusDetailsRoute = (type, id, name) => ({
  path: '/status-report/details',
  query: { type, id, name }
})

// Sheet upload state
const uploadedFile = ref(null)
const selectedTeam = ref(null)
const autoDetectedTeam = ref(false)
const processing = ref(false)
const filterLoading = ref(false)

// Team options with their processor modules
const teamOptions = [
  { label: 'Platform Team', value: 'app.engine.sheets.platform_team_status', patterns: ['platform', 'plateform'] },
  { label: 'Product Team', value: 'app.engine.sheets.phoenix_status', patterns: ['product', 'phoenix'] },
  { label: 'PMI Team', value: 'app.engine.sheets.pmi_status_team', patterns: ['pmi'] },
  { label: 'PTR Team', value: 'app.engine.sheets.ptr_team_status', patterns: ['ptr'] },
  { label: 'Dexia Team', value: 'app.engine.sheets.dexia_status', patterns: ['dexia'] },
  { label: 'Data Team', value: 'app.engine.sheets.bud_db_status', patterns: ['data', 'buddb'] },
  { label: 'Other', value: 'app.engine.sheets.generic', patterns: [] }
]

// Dialog states
const fillRateDialog = ref(false)
const leaveDialog = ref(false)
const productivityDialog = ref(false)

// Chart refs
const fillRateChart = ref(null)
const leaveChart = ref(null)
const productivityChart = ref(null)
const fillRateChartDialog = ref(null)
const leaveChartDialog = ref(null)
const productivityChartDialog = ref(null)

// Chart instances
let fillRateChartInstance = null
let leaveChartInstance = null
let productivityChartInstance = null
let fillRateChartDialogInstance = null
let leaveChartDialogInstance = null
let productivityChartDialogInstance = null

// Sample data
const fillRateData = ref([
  { name: '100% Filled', value: 45, count: 12, share: '45%', color: '#10B981' },
  { name: '80-99% Filled', value: 30, count: 8, share: '30%', color: '#4A90E2' },
  { name: '50-79% Filled', value: 15, count: 4, share: '15%', color: '#F59E0B' },
  { name: 'Below 50%', value: 10, count: 3, share: '10%', color: '#EF4444' }
])

const leaveData = ref([
  { week: 'Week 1', total: 5, details: '3 sick leave, 2 casual leave' },
  { week: 'Week 2', total: 3, details: '2 sick leave, 1 casual leave' },
  { week: 'Week 3', total: 7, details: '4 sick leave, 3 casual leave' },
  { week: 'Week 4', total: 4, details: '2 sick leave, 2 casual leave' },
  { week: 'Week 5', total: 6, details: '3 sick leave, 3 casual leave' },
  { week: 'Week 6', total: 8, details: '5 sick leave, 3 casual leave' },
  { week: 'Week 7', total: 5, details: '2 sick leave, 3 casual leave' },
  { week: 'Week 8', total: 4, details: '3 sick leave, 1 casual leave' },
  { week: 'Week 9', total: 6, details: '4 sick leave, 2 casual leave' },
  { week: 'Week 10', total: 7, details: '3 sick leave, 4 casual leave' },
  { week: 'Week 11', total: 5, details: '2 sick leave, 3 casual leave' },
  { week: 'Week 12', total: 4, details: '2 sick leave, 2 casual leave' }
])

const productivityMetrics = ref({
  totalEntries: 0,
  fillRate: 0,
  unfilled: 0,
  leave: 0
})

const weeklyStatusData = ref({
  sheetDate: null,
  dailyBreakdown: [],
  summary: {
    total: 0,
    fillRate: 0,
    unfilled: 0,
    leave: 0
  }
})

// Team data
const teamColumns = [
  { name: 'team_lead', label: 'Team Lead', field: 'team_lead', align: 'left', sortable: true },
  { name: 'total_team_members', label: 'Team Size', field: 'total_team_members', align: 'center', sortable: true },
  { name: 'completed_count', label: 'Completed', field: 'completed_count', align: 'center', sortable: true },
  { name: 'pending_count', label: 'Pending', field: 'pending_count', align: 'center', sortable: true },
  { name: 'is_complete', label: 'Status', field: 'is_complete', align: 'center', sortable: true }
]

const teamData = ref([])
const parentExpanded = ref(true)
const weekInfo = ref({
  week_start: '',
  current_date: '',
  deadline: ''
})

// Fetch team completion status from API
const fetchTeamStatus = async () => {
  try {
    const params = {}
    if (dateRange.value.from && dateRange.value.to) {
      params.start = dateRange.value.from
      params.end = dateRange.value.to
    }
    const response = await api.get('/v1/daily-reports/team-completion', { params })
    console.log('Team completion response:', response.data)
    if (response.data) {
      const teamStatus = response.data.team_status || []
      console.log('Team status before assignment:', teamStatus)
      console.log('First item:', teamStatus[0])
      teamData.value = teamStatus
      console.log('Team data after assignment:', teamData.value)
      console.log('Team data length:', teamData.value.length)
      weekInfo.value = {
        week_start: response.data.week_start,
        current_date: response.data.current_date,
        deadline: response.data.deadline
      }
    }
  } catch (error) {
    console.error('Error fetching team completion status:', error)
  }
}

// Fetch weekly status breakdown from API
const fetchWeeklyStatusBreakdown = async () => {
  try {
    const response = await api.get('/v1/sheets/weekly-status-breakdown')
    console.log('Weekly status data:', response.data)
    if (response.data) {
      weeklyStatusData.value = {
        sheetDate: response.data.sheet_date,
        dailyBreakdown: response.data.daily_breakdown,
        summary: response.data.summary
      }
      productivityMetrics.value = {
        totalEntries: response.data.summary.total,
        fillRate: response.data.summary.fill_rate,
        unfilled: response.data.summary.unfilled,
        leave: response.data.summary.leave
      }
      console.log('Updated weeklyStatusData:', weeklyStatusData.value)
    }
  } catch (error) {
    console.error('Error fetching weekly status breakdown:', error)
  }
}

// Watch for data changes and update chart
watch(() => weeklyStatusData.value.dailyBreakdown, (newData) => {
  if (newData && newData.length > 0 && productivityChartInstance) {
    console.log('Data changed, updating chart:', newData)
    productivityChartInstance.dispose()
    productivityChartInstance = null
    setTimeout(() => {
      initProductivityChart()
    }, 100)
  }
}, { deep: true })

// Reset date range to default
const resetDateRange = async () => {
  await setDateRange('presentWeek')
}

// Toggle parent expanded state
const toggleParentExpanded = () => {
  parentExpanded.value = !parentExpanded.value
  console.log('Parent expanded toggled:', parentExpanded.value)
}

// Export team completion data to Excel
const exportToExcel = () => {
  try {
    const exportData = []

    // Add header row
    exportData.push(['Team Lead', 'Team Size', 'Completed', 'Pending', 'Status'])

    // Add data for each team lead
    teamData.value.forEach(team => {
      // Add team lead row with counts
      exportData.push([
        team.team_lead,
        team.total_team_members,
        team.completed_count || 0,
        team.pending_count || 0,
        team.is_complete ? 'Completed' : 'Pending'
      ])

      // Add pending members (without "Pending:" prefix)
      if (team.pending_members && team.pending_members.length > 0) {
        team.pending_members.forEach(member => {
          exportData.push(['', '', '', member])
        })
      }

      // Add completed members (without "Completed:" prefix)
      if (team.completed_members && team.completed_members.length > 0) {
        team.completed_members.forEach(member => {
          exportData.push(['', '', member, ''])
        })
      }

      // Add empty row for separation
      exportData.push([])
    })

    // Create worksheet
    const ws = XLSX.utils.aoa_to_sheet(exportData)

    // Apply conditional formatting using cell styles
    const range = XLSX.utils.decode_range(ws['!ref'])

    // Loop through data rows (skip header row)
    for (let row = range.s.r + 1; row <= range.e.r; row++) {
      // Skip empty rows
      const cellAddress = XLSX.utils.encode_cell({ r: row, c: 0 })
      if (!ws[cellAddress] || !ws[cellAddress].v) continue

      // Check if this is a team lead row (has team lead name in column A)
      const isTeamLeadRow = ws[cellAddress].v

      if (isTeamLeadRow) {
        // Status column (column E, index 4) for team lead row
        const statusCell = XLSX.utils.encode_cell({ r: row, c: 4 })
        if (ws[statusCell]) {
          if (ws[statusCell].v === 'Completed') {
            ws[statusCell].s = {
              fill: { patternType: "solid", fgColor: { rgb: "C6EFCE" } },
              font: { color: { rgb: "006100" }, bold: true }
            }
          } else if (ws[statusCell].v === 'Pending') {
            ws[statusCell].s = {
              fill: { patternType: "solid", fgColor: { rgb: "FFC7CE" } },
              font: { color: { rgb: "9C0006" }, bold: true }
            }
          }
        }
      } else {
        // Member row - apply color based on which column has the name
        // Completed column (column C, index 2)
        const completedCell = XLSX.utils.encode_cell({ r: row, c: 2 })
        if (ws[completedCell] && ws[completedCell].v) {
          ws[completedCell].s = {
            fill: { patternType: "solid", fgColor: { rgb: "C6EFCE" } },
            font: { color: { rgb: "006100" } }
          }
        }

        // Pending column (column D, index 3)
        const pendingCell = XLSX.utils.encode_cell({ r: row, c: 3 })
        if (ws[pendingCell] && ws[pendingCell].v) {
          ws[pendingCell].s = {
            fill: { patternType: "solid", fgColor: { rgb: "FFC7CE" } },
            font: { color: { rgb: "9C0006" } }
          }
        }
      }
    }

    // Style header row
    for (let col = range.s.c; col <= range.e.c; col++) {
      const headerCell = XLSX.utils.encode_cell({ r: range.s.r, c: col })
      if (ws[headerCell]) {
        ws[headerCell].s = {
          fill: { patternType: "solid", fgColor: { rgb: "D3D3D3" } },
          font: { bold: true }
        }
      }
    }

    // Create workbook
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Team Completion Status')

    // Generate filename with date range
    const filename = `Team_Completion_Status_${weekInfo.value.week_start}_to_${weekInfo.value.current_date}.xlsx`

    // Download file
    XLSX.writeFile(wb, filename)

    console.log('Excel file exported successfully')
  } catch (error) {
    console.error('Error exporting to Excel:', error)
  }
}

// Initialize date range
const initDateRange = () => {
  const today = new Date()
  const dayOfWeek = today.getDay()
  const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
  const monday = new Date(today.setDate(diff))
  // Use today's date as end date, but if it's Saturday (6) or Sunday (0), use Friday instead
  let toDate = new Date()
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    toDate = new Date(monday)
    toDate.setDate(monday.getDate() + 4) // Friday
  }

  dateRange.value.from = monday.toISOString().split('T')[0]
  dateRange.value.to = toDate.toISOString().split('T')[0]
}

const setDateRange = async (preset) => {
  const today = new Date()
  let fromDate = new Date()

  switch(preset) {
    case 'presentWeek': {
      const dayOfWeek = today.getDay()
      const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
      fromDate = new Date(today.setDate(diff))
      // Use today's date as end date, but if it's Saturday (6) or Sunday (0), use Friday instead
      let toDate = new Date()
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        toDate = new Date(fromDate)
        toDate.setDate(fromDate.getDate() + 4) // Friday
      }
      dateRange.value.from = fromDate.toISOString().split('T')[0]
      dateRange.value.to = toDate.toISOString().split('T')[0]
      console.log(dateRange.value)
      break
    }
    case '1month': {
      fromDate.setMonth(today.getMonth() - 1)
      dateRange.value.from = fromDate.toISOString().split('T')[0]
      dateRange.value.to = today.toISOString().split('T')[0]
      break
    }
    case 'custom':
      dateRange.value.preset = preset
      return
  }

  dateRange.value.preset = preset

  // Automatically apply the filter after setting the date range
  await applyDateFilter()
}

const applyDateFilter = async () => {
  filterLoading.value = true
  try {
    console.log('Applying date filter:', dateRange.value)
    // Fetch team status with date range
    await fetchTeamStatus()
    // Fetch weekly status breakdown with date range
    await fetchWeeklyStatusBreakdown()
  } catch (error) {
    console.error('Error applying date filter:', error)
  } finally {
    filterLoading.value = false
  }
}

// Sheet upload functions
const handleFileUpload = (file) => {
  if (!file) {
    selectedTeam.value = null
    autoDetectedTeam.value = false
    return
  }

  // Auto-detect team from filename using patterns
  const fileName = file.name.toLowerCase()
  const detectedTeam = teamOptions.find(option =>
    option.patterns.some(pattern => fileName.includes(pattern.toLowerCase()))
  )

  if (detectedTeam) {
    selectedTeam.value = detectedTeam.value
    autoDetectedTeam.value = true
  } else {
    selectedTeam.value = null
    autoDetectedTeam.value = false
  }
}

const processSheet = async () => {
  if (!uploadedFile.value || !selectedTeam.value) {
    return
  }

  processing.value = true

  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('processor_module', selectedTeam.value)

    // Call the API endpoint using the boot api instance
    const response = await api.post('/v1/sheets/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // Handle successful processing
    console.log('Sheet processed successfully:', response.data)

    // Refresh data after successful sheet processing
    await fetchTeamStatus()
    await fetchWeeklyStatusBreakdown()

  } catch (error) {
    console.error('Error processing sheet:', error)
    if (error.response) {
      console.error('Server responded with error:', error.response.data)
    }
  } finally {
    processing.value = false
  }
}

// Dialog functions
const openFillRateDialog = () => {
  fillRateDialog.value = true
  setTimeout(() => {
    initFillRateChartDialog()
  }, 100)
}

const openLeaveDialog = () => {
  leaveDialog.value = true
  setTimeout(() => {
    initLeaveChartDialog()
  }, 100)
}

const openProductivityDialog = () => {
  productivityDialog.value = true
  setTimeout(() => {
    initProductivityChartDialog()
  }, 100)
}

// Chart initialization functions
const initFillRateChart = () => {
  fillRateChartInstance = echarts.init(fillRateChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' },
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      bottom: '0%',
      left: 'center',
      textStyle: { color: '#000' }
    },
    series: [
      {
        name: 'Fill Rate',
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['50%', '60%'],
        startAngle: 180,
        endAngle: 360,
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#000',
            formatter: '{b}\n{c}%'
          }
        },
        labelLine: {
          show: false
        },
        data: fillRateData.value.map(item => ({
          value: item.value,
          name: item.name,
          itemStyle: { color: item.color }
        }))
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '45%',
        style: {
          text: '85%',
          textAlign: 'center',
          fill: '#000',
          fontSize: 28,
          fontWeight: 'bold'
        }
      },
      {
        type: 'text',
        left: 'center',
        top: '55%',
        style: {
          text: 'Avg Fill Rate',
          textAlign: 'center',
          fill: '#666',
          fontSize: 14
        }
      }
    ]
  }
  fillRateChartInstance.setOption(option)
}

const initLeaveChart = () => {
  leaveChartInstance = echarts.init(leaveChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' }
    },
    legend: {
      data: ['Sick Leave', 'Casual Leave'],
      textStyle: { color: '#000' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: leaveData.value.map(d => d.week),
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: 'Sick Leave',
        type: 'bar',
        stack: 'total',
        data: [3, 2, 4, 2, 3, 5, 2, 3, 4, 3, 2, 2],
        itemStyle: { color: '#EF4444' }
      },
      {
        name: 'Casual Leave',
        type: 'bar',
        stack: 'total',
        data: [2, 1, 3, 2, 3, 3, 3, 1, 2, 4, 3, 2],
        itemStyle: { color: '#F59E0B' }
      }
    ]
  }
  leaveChartInstance.setOption(option)
}

const initProductivityChart = () => {
  if (!productivityChart.value) {
    console.log('Chart element not available')
    return
  }

  // Dispose existing instance if any
  if (productivityChartInstance) {
    productivityChartInstance.dispose()
    productivityChartInstance = null
  }

  productivityChartInstance = echarts.init(productivityChart.value)

  // Use real weekly data if available, otherwise use empty structure
  const dailyData = weeklyStatusData.value.dailyBreakdown.length > 0
    ? weeklyStatusData.value.dailyBreakdown
    : [
        { day: 'Mon', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Tue', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Wed', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Thu', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Fri', filled: 0, unfilled: 0, leave: 0, total: 0 }
      ]

  console.log('Initializing chart with data:', dailyData)

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' }
    },
    legend: {
      data: ['Filled', 'Unfilled', 'Leave'],
      textStyle: { color: '#000' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dailyData.map(d => d.day),
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: 'Filled',
        type: 'bar',
        stack: 'total',
        data: dailyData.map(d => d.filled),
        itemStyle: { color: '#10B981' }
      },
      {
        name: 'Unfilled',
        type: 'bar',
        stack: 'total',
        data: dailyData.map(d => d.unfilled),
        itemStyle: { color: '#EF4444' }
      },
      {
        name: 'Leave',
        type: 'bar',
        stack: 'total',
        data: dailyData.map(d => d.leave),
        itemStyle: { color: '#F59E0B' }
      }
    ]
  }

  productivityChartInstance.setOption(option)
  console.log('Chart initialized successfully')
}

// Dialog chart initialization
const initFillRateChartDialog = () => {
  if (fillRateChartDialogInstance) {
    fillRateChartDialogInstance.dispose()
  }
  fillRateChartDialogInstance = echarts.init(fillRateChartDialog.value)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' },
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      bottom: '0%',
      left: 'center',
      textStyle: { color: '#000' }
    },
    series: [
      {
        name: 'Fill Rate',
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['50%', '60%'],
        startAngle: 180,
        endAngle: 360,
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#000',
            formatter: '{b}\n{c}%'
          }
        },
        labelLine: {
          show: false
        },
        data: fillRateData.value.map(item => ({
          value: item.value,
          name: item.name,
          itemStyle: { color: item.color }
        }))
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '45%',
        style: {
          text: '85%',
          textAlign: 'center',
          fill: '#000',
          fontSize: 28,
          fontWeight: 'bold'
        }
      },
      {
        type: 'text',
        left: 'center',
        top: '55%',
        style: {
          text: 'Avg Fill Rate',
          textAlign: 'center',
          fill: '#666',
          fontSize: 14
        }
      }
    ]
  }
  fillRateChartDialogInstance.setOption(option)
}

const initLeaveChartDialog = () => {
  if (leaveChartDialogInstance) {
    leaveChartDialogInstance.dispose()
  }
  leaveChartDialogInstance = echarts.init(leaveChartDialog.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' }
    },
    legend: {
      data: ['Sick Leave', 'Casual Leave'],
      textStyle: { color: '#000' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: leaveData.value.map(d => d.week),
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: 'Sick Leave',
        type: 'bar',
        stack: 'total',
        data: [3, 2, 4, 2, 3, 5, 2, 3, 4, 3, 2, 2],
        itemStyle: { color: '#EF4444' }
      },
      {
        name: 'Casual Leave',
        type: 'bar',
        stack: 'total',
        data: [2, 1, 3, 2, 3, 3, 3, 1, 2, 4, 3, 2],
        itemStyle: { color: '#F59E0B' }
      }
    ]
  }
  leaveChartDialogInstance.setOption(option)
}

const initProductivityChartDialog = () => {
  if (productivityChartDialogInstance) {
    productivityChartDialogInstance.dispose()
  }
  productivityChartDialogInstance = echarts.init(productivityChartDialog.value)

  // Use real weekly data if available, otherwise use empty structure
  const dailyData = weeklyStatusData.value.dailyBreakdown.length > 0
    ? weeklyStatusData.value.dailyBreakdown
    : [
        { day: 'Mon', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Tue', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Wed', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Thu', filled: 0, unfilled: 0, leave: 0, total: 0 },
        { day: 'Fri', filled: 0, unfilled: 0, leave: 0, total: 0 }
      ]

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' }
    },
    legend: {
      data: ['Filled', 'Unfilled', 'Leave'],
      textStyle: { color: '#000' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dailyData.map(d => d.day),
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: 'Filled',
        type: 'bar',
        stack: 'total',
        data: dailyData.map(d => d.filled),
        itemStyle: { color: '#10B981' }
      },
      {
        name: 'Unfilled',
        type: 'bar',
        stack: 'total',
        data: dailyData.map(d => d.unfilled),
        itemStyle: { color: '#EF4444' }
      },
      {
        name: 'Leave',
        type: 'bar',
        stack: 'total',
        data: dailyData.map(d => d.leave),
        itemStyle: { color: '#F59E0B' }
      }
    ]
  }
  productivityChartDialogInstance.setOption(option)
}

onMounted(() => {
  initDateRange()
  fetchTeamStatus()
  fetchWeeklyStatusBreakdown()
  initFillRateChart()
  initLeaveChart()
  initProductivityChart()
})

onUnmounted(() => {
  if (fillRateChartInstance) fillRateChartInstance.dispose()
  if (leaveChartInstance) leaveChartInstance.dispose()
  if (productivityChartInstance) productivityChartInstance.dispose()
  if (fillRateChartDialogInstance) fillRateChartDialogInstance.dispose()
  if (leaveChartDialogInstance) leaveChartDialogInstance.dispose()
  if (productivityChartDialogInstance) productivityChartDialogInstance.dispose()
})

// Handle window resize
window.addEventListener('resize', () => {
  if (fillRateChartInstance) fillRateChartInstance.resize()
  if (leaveChartInstance) leaveChartInstance.resize()
  if (productivityChartInstance) productivityChartInstance.resize()
  if (fillRateChartDialogInstance) fillRateChartDialogInstance.resize()
  if (leaveChartDialogInstance) leaveChartDialogInstance.resize()
  if (productivityChartDialogInstance) productivityChartDialogInstance.resize()
})
</script>

<style scoped>
.member-status-link {
  display: inline-flex;
  width: fit-content;
  max-width: 100%;
  align-self: flex-start;
  font-size: 16px;
  line-height: 1.4;
  color: var(--q-primary);
  text-decoration: none;
  cursor: pointer;
}

.member-status-link:hover {
  text-decoration: underline;
}

.status-report-page {
  background: #f5f5f5;
}

.chart-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.analytics-dialog {
  border-radius: 12px;
}

.q-card {
  border-radius: 8px;
}
</style>
