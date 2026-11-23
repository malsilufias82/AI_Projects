<template>
  <q-page class="bg-grey-2 q-pa-lg">
    <div class="dashboard-content q-gutter-y-lg">
      <div class="row items-center justify-between q-col-gutter-md">
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">TL Group Dashboard</h1>
          <p class="text-grey-7 q-mt-sm q-mb-none">
            View team sizes and employee onboarding progress by team lead.
          </p>
        </div>
        <q-btn
          outline
          color="primary"
          icon="refresh"
          label="Refresh"
          :loading="loading"
          @click="fetchDashboardData"
        />
      </div>

      <q-card flat bordered>
        <q-card-section class="q-pb-sm">
          <div class="text-h6">Teams</div>
          <div class="text-caption text-grey-7">
            Pending totals show the number of team members waiting for each onboarding stage.
          </div>
        </q-card-section>
        <q-separator />

        <q-inner-loading :showing="loading" color="primary" />
        <q-banner v-if="!loading && teams.length === 0" class="bg-white text-grey-7">
          No team leads or onboarding team members are available.
        </q-banner>

        <q-list v-else separator>
          <q-expansion-item
            v-for="team in teams"
            :key="team.teamLeadId || team.teamLead"
            expand-separator
            header-class="team-header"
            @show="fetchTeamPhaseStatuses(team)"
          >
            <template #header>
              <q-item-section avatar>
                <q-avatar color="primary" text-color="white">
                  {{ team.teamLead.slice(0, 1).toUpperCase() }}
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-medium">{{ team.teamLead }}</q-item-label>
                <q-item-label caption>{{ team.memberCount }} team members</q-item-label>
              </q-item-section>
              <q-item-section side class="gt-sm">
                <div class="row q-gutter-md">
                  <div v-for="stage in stageColumns" :key="stage.key" class="text-center">
                    <div class="text-caption text-grey-7">{{ stage.label }}</div>
                    <div class="text-weight-bold">Pending: {{ team.stageCounts[stage.key] }}</div>
                  </div>
                </div>
              </q-item-section>
            </template>

            <q-card flat class="bg-grey-1">
              <q-card-section class="lt-md">
                <div class="row q-col-gutter-md">
                  <div
                    v-for="stage in stageColumns"
                    :key="stage.key"
                    class="col-6 col-sm-3"
                  >
                    <div class="text-caption text-grey-7">{{ stage.label }}</div>
                    <div class="text-weight-bold">Pending: {{ team.stageCounts[stage.key] }}</div>
                  </div>
                </div>
              </q-card-section>
              <q-table
                flat
                :rows="team.members"
                :columns="memberColumns"
                row-key="id"
                :pagination="{ rowsPerPage: 10 }"
                no-data-label="No onboarding records found for this team."
              >
                <template #body-cell-employee="props">
                  <q-td :props="props">
                    <q-btn
                      flat
                      dense
                      no-caps
                      color="primary"
                      class="q-px-none"
                      :label="props.row.employee"
                      :to="employeeOnboardingRoute(props.row)"
                    />
                  </q-td>
                </template>
                <template #body-cell="props">
                  <q-td :props="props">
                    <q-badge
                      v-if="stageColumns.some((stage) => stage.key === props.col.name)"
                      :color="statusColor(props.value)"
                      :label="props.value || 'To be started'"
                    />
                    <span v-else>{{ props.value }}</span>
                  </q-td>
                </template>
              </q-table>
            </q-card>
          </q-expansion-item>
        </q-list>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const loading = ref(false)
const teamLeads = ref([])
const employees = ref([])
const loadedPhaseTeams = ref(new Set())
const loadingPhaseTeams = ref(new Set())

const stageColumns = [
  { key: 'bgv', label: 'BGV' },
  { key: 'vcf', label: 'VCF' },
  { key: 'credential', label: 'Credentials' },
  { key: 'week0', label: 'Week0', countKey: 'status' },
  { key: 'day1', label: 'Day1', countKey: 'status' },
  { key: 'day2', label: 'Day2', countKey: 'status' },
  { key: 'day3', label: 'Day3', countKey: 'status' },
  { key: 'day4', label: 'Day4', countKey: 'status' },
  { key: 'day5', label: 'Day5', countKey: 'status' }
]

const memberColumns = [
  { name: 'employee', label: 'Team Member', field: 'employee', align: 'left', sortable: true },
  { name: 'employeeCode', label: 'Employee ID', field: 'employeeCode', align: 'left', sortable: true },
  ...stageColumns.map(({ key, label }) => ({ name: key, label, field: key, align: 'left' }))
]

const normalizeName = (value) => String(value || '').trim().toLowerCase()

const teams = computed(() => teamLeads.value.map((lead) => {
  const members = employees.value.filter(
    (employee) => (lead.team_lead_id && employee.teamLeadId === String(lead.team_lead_id)) ||
      normalizeName(employee.teamLead) === normalizeName(lead.team_lead)
  )

  const stageCounts = Object.fromEntries(stageColumns.map(({ key, countKey }) => [
    key,
    members.filter((member) => !isCompleted(member[countKey || key])).length
  ]))

  return {
    teamLead: lead.team_lead || 'Unknown team lead',
    teamLeadId: lead.team_lead_id,
    memberCount: Number(lead.total_team_members) || members.length,
    members,
    stageCounts
  }
}))

function isCompleted(status) {
  return ['complete', 'completed'].includes(String(status || '').trim().toLowerCase())
}

function statusColor(status) {
  const normalized = String(status || '').trim().toLowerCase().replace(/[\s_-]+/g, '')
  if (['complete', 'completed'].includes(normalized)) return 'positive'
  if (['inprogress', 'awaited'].includes(normalized)) return 'warning'
  if (['cancelled', 'canceled'].includes(normalized)) return 'negative'
  return 'grey-6'
}

function employeeOnboardingRoute(employee) {
  return {
    path: '/employee-onboarding',
    query: {
      employeeId: employee.id || employee.userId || employee.employeeId,
      mode: 'view'
    }
  }
}

function getPhaseStatus(counts, phase) {
  const total = Number(counts?.[`${phase}_total`] ?? counts?.[phase] ?? 0)
  const completed = Number(counts?.[`${phase}_completed`] ?? 0)

  if (!total) return 'To be started'
  if (completed >= total) return 'Completed'
  if (completed > 0) return 'In-progress'
  return 'Pending'
}

async function fetchTeamPhaseStatuses(team) {
  const teamKey = team.teamLeadId || team.teamLead
  if (loadedPhaseTeams.value.has(teamKey) || loadingPhaseTeams.value.has(teamKey)) return

  loadingPhaseTeams.value = new Set([...loadingPhaseTeams.value, teamKey])
  const results = await Promise.allSettled(team.members.map(async (member) => {
    const employeeId = member.employeeCode || member.id
    const { data } = await api.get('/v1/week0/tracker', { params: { employeeId } })
    return { member, counts: data?.counts || {} }
  }))

  const hasFailures = results.some((result) => result.status === 'rejected')
  for (const result of results) {
    if (result.status === 'rejected') continue

    const { member, counts } = result.value
    for (const stage of stageColumns.filter(({ key }) => key === 'week0' || /^day[1-5]$/.test(key))) {
      const phase = stage.key === 'week0' ? 'Week0' : stage.key.replace(/^day/, 'Day')
      member[stage.key] = getPhaseStatus(counts, phase)
    }
  }

  loadingPhaseTeams.value = new Set([...loadingPhaseTeams.value].filter((key) => key !== teamKey))
  if (!hasFailures) {
    loadedPhaseTeams.value = new Set([...loadedPhaseTeams.value, teamKey])
  }

  if (hasFailures) {
    $q.notify({
      type: 'negative',
      message: 'Unable to load onboarding phase statuses for some team members.'
    })
  }
}

async function fetchDashboardData() {
  loading.value = true
  try {
    const [teamResponse, employeeResponse] = await Promise.all([
      api.get('/v1/daily-reports/team-completion'),
      api.get('/v1/users/onboarding')
    ])
    teamLeads.value = Array.isArray(teamResponse.data?.team_status)
      ? teamResponse.data.team_status
      : []
    employees.value = Array.isArray(employeeResponse.data) ? employeeResponse.data : []
    loadedPhaseTeams.value = new Set()
    loadingPhaseTeams.value = new Set()
  } catch (error) {
    console.error('Error fetching TL group dashboard data:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Unable to load TL group dashboard.'
    })
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboardData)
</script>

<style scoped>
.dashboard-content {
  max-width: 1440px;
  margin: 0 auto;
}

.team-header {
  min-height: 76px;
}
</style>
