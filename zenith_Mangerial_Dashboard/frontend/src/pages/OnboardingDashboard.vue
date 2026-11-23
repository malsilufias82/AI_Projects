
<template>
  <q-page class="bg-grey-2 q-pa-lg">
    <div class="dashboard-content q-gutter-y-lg">
      <q-tabs
        align="left"
        active-color="primary"
        indicator-color="primary"
        class="page-tabs bg-white text-grey-8"
        no-caps
      >
        <q-route-tab name="home" label="Home" to="/" />
        <q-route-tab name="onboarding-metrics" label="Onboarding Metrics" to="onboarding-metrics" />
        <q-route-tab name="employee-onboarding" label="Employee Onboarding" to="employee-onboarding" />
        <q-route-tab name="Week0" label="Week0" to="Week-0" />
      </q-tabs>

      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">Onboarding Dashboard</h1>
        <p class="text-grey-7 q-mt-sm q-mb-none">
          Monitor onboarding progress, pending activities, and SLA compliance.
        </p>
      </div>

      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Search Criteria</div>
          <div class="row q-col-gutter-md">
            <q-input v-model="searchEmployeeID" class="col-12 col-md-4 col-lg-3" outlined dense label="Search EmployeeID" />
            <q-input v-model="searchEmployee" class="col-12 col-md-4 col-lg-3" outlined dense label="Search Employee" />
            <q-select v-model="selectedProject" class="col-12 col-md-4 col-lg-3" outlined dense label="Select Project" :options="projectOptions" emit-value map-options clearable />
            <q-select v-model="selectedClient" class="col-12 col-md-4 col-lg-3" outlined dense label="Select Client" :options="clientOptions" emit-value map-options clearable />
            <q-select v-model="selectedTeamLead" class="col-12 col-md-4 col-lg-3" outlined dense label="Select Team Lead" :options="teamLeadOptionsSelect" emit-value map-options clearable />
            <q-select v-model="selectedPrimarySkill" class="col-12 col-md-4 col-lg-3" outlined dense label="Select Primary Skill" :options="primarySkillOptionsSelect" emit-value map-options clearable />
          </div>
          <div class="q-mt-md q-gutter-sm">
            <q-btn color="primary" label="Search" @click="searchEmployees" />
            <q-btn outline label="Reset" @click="resetFilters" />
          </div>
        </q-card-section>
      </q-card>

      <div class="row q-col-gutter-md">
        <div v-for="metric in metrics" :key="metric.title" class="col-12 col-sm-6 col-lg">
          <q-card flat bordered class="full-height">
            <q-card-section>
              <div :class="`metric-dot bg-${metric.color}`" />
              <div class="text-h4 text-weight-bold q-mt-sm">{{ metric.value }}</div>
              <div class="text-body2 text-grey-7 q-mt-sm">{{ metric.title }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      
      <q-card flat bordered>
        <q-card-section class="q-pb-sm row items-center justify-between">
          <div class="text-h6">Onboarding List</div>
          <q-btn flat round dense icon="filter_list" aria-label="Filter onboarding employees">
            <q-tooltip>Filter onboarding employees</q-tooltip>
            <q-menu anchor="bottom right" self="top right" :offset="[0, 8]">
              <div class="filter-menu q-pa-md">
                <div class="text-subtitle1 text-weight-medium q-mb-sm">Filter employees</div>
                <div v-for="filter in filterDefinitions" :key="filter.key" class="q-mb-sm">
                  <q-select
                    v-model="selectedFilters[filter.key]"
                    :label="filter.label"
                    :options="availableFilterOptions[filter.key]"
                    multiple
                    outlined
                    dense
                    use-input
                    input-debounce="0"
                    clearable
                    use-chips
                    @filter="(value, update) => updateFilterOptions(filter, value, update)"
                  />
                </div>
                <q-separator class="q-my-sm" />
                <q-btn flat dense color="primary" label="Clear filters" @click="clearAdditionalFilters" />
              </div>
            </q-menu>
          </q-btn>
        </q-card-section>
        <q-separator />
        <q-table flat :rows="filteredRows" :columns="columns" row-key="employee" :pagination="{ rowsPerPage: 10 }">
          <template #body-cell-actions="props">
            <q-td :props="props" class="q-gutter-xs">
              <q-btn
                flat
                dense
                label="View"
                :to="{ path: '/employee-onboarding', query: { employeeId: props.row.id || props.row.userId || props.row.employeeId || '', mode: 'view' } }"
              />
              <q-btn
                flat
                dense
                color="primary"
                label="Edit"
                :to="{ path: '/employee-onboarding', query: { employeeId: props.row.id || props.row.userId || props.row.employeeId || '', mode: 'edit' } }"
              />
            </q-td>
          </template>
        </q-table>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const searchEmployeeID = ref('')
const searchEmployee = ref('')
const selectedProject = ref(null)
const selectedClient = ref(null)
const selectedTeamLead = ref(null)
const selectedPrimarySkill = ref(null)
const searchedEmployeeID = ref('')
const searchedEmployee = ref('')
const searchedProject = ref(null)
const searchedClient = ref(null)
const searchedTeamLead = ref(null)
const searchedPrimarySkill = ref(null)
const projects = ref([])
const clients = ref([])
const rows = ref([])


const columns = [
{ name: 'employeeCode', label: 'Employee ID', field: 'employeeCode', align: 'left' },
 { name: 'employee', label: 'Employee', field: 'employee', align: 'left' },
  { name: 'client', label: 'Client', field: 'client', align: 'left' },
  { name: 'project', label: 'Project', field: 'project', align: 'left' },
  { name: 'teamLead', label: 'Team Lead', field: 'teamLead', align: 'left' },
  { name: 'primarySkill', label: 'Primary Skill', field: 'primarySkill', align: 'left' },
  { name: 'accountManager', label: 'Account Manager', field: 'accountManager', align: 'left' },
  { name: 'credential', label: 'Credential Status', field: 'credential', align: 'left' },
  { name: 'bgv', label: 'BGV Status', field: 'bgv', align: 'left' },
  { name: 'vcf', label: 'VCF Status', field: 'vcf', align: 'left' },
  { name: 'status', label: 'Overall Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'left' }
]

function timestampToDate(timestamp) {
  const date = new Date(timestamp);
  return `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
}

const splitMultiValueField = (value) => String(value ?? '')
  .split(',')
  .map((item) => item.trim())
  .filter(Boolean)

const uniqueRowValues = (field) => {
  const values = rows.value.flatMap((row) => splitMultiValueField(row[field]))
  return [...new Set(values.filter(Boolean))]
}

const withBlankOption = (values) => [{ label: 'All', value: null }, ...values.map((value) => ({ label: value, value }))]
const projectOptions = computed(() => withBlankOption(projects.value))
const clientOptions = computed(() => withBlankOption(clients.value))
const teamLeadOptions = computed(() => uniqueRowValues('teamLead'))
const teamLeadOptionsSelect = computed(() => withBlankOption(teamLeadOptions.value))
const primarySkillOptions = computed(() => uniqueRowValues('primarySkill'))
const primarySkillOptionsSelect = computed(() => withBlankOption(primarySkillOptions.value))
const filterDefinitions = computed(() => [
  { key: 'client', label: 'Client', field: 'client', options: clients.value },
  { key: 'project', label: 'Project', field: 'project', options: projects.value },
  { key: 'teamLead', label: 'Team Lead', field: 'teamLead', options: teamLeadOptions.value },
  { key: 'primarySkill', label: 'Primary Skill', field: 'primarySkill', options: primarySkillOptions.value },
  { key: 'accountManager', label: 'Account Manager', field: 'accountManager', options: uniqueRowValues('accountManager') },
  { key: 'status', label: 'Overall Status', field: 'status', options: uniqueRowValues('status') },
  { key: 'credential', label: 'Credential Status', field: 'credential', options: uniqueRowValues('credential') },
  { key: 'bgv', label: 'BGV Status', field: 'bgv', options: uniqueRowValues('bgv') },
  { key: 'vcf', label: 'VCF Status', field: 'vcf', options: uniqueRowValues('vcf') },
  { key: 'rag', label: 'RAG Status', field: 'rag', options: uniqueRowValues('rag') }
])
const filterKeys = ['client', 'project', 'teamLead', 'primarySkill', 'accountManager', 'status', 'credential', 'bgv', 'vcf', 'rag']
const selectedFilters = reactive(Object.fromEntries(
  filterKeys.map((key) => [key, []])
))
const availableFilterOptions = reactive(Object.fromEntries(
  filterKeys.map((key) => [key, []])
))

const filteredRows = computed(() => rows.value.filter((row) => {
  const employeeIdMatches = !searchedEmployeeID.value || String(row.employeeCode || '').toLowerCase().includes(searchedEmployeeID.value.toLowerCase())
  const employeeMatches = !searchedEmployee.value || (row.employee || '').toLowerCase().includes(searchedEmployee.value.toLowerCase())
  const teamLeadMatches = !searchedTeamLead.value || String(row.teamLead || '').toLowerCase() === String(searchedTeamLead.value).toLowerCase()
  const rowPrimarySkills = splitMultiValueField(row.primarySkill)
  const primarySkillMatches = !searchedPrimarySkill.value || rowPrimarySkills.some((skill) => skill.toLowerCase() === String(searchedPrimarySkill.value).toLowerCase())
  const searchMatches = employeeIdMatches && employeeMatches && teamLeadMatches && primarySkillMatches &&
    (!searchedProject.value || row.project === searchedProject.value) &&
    (!searchedClient.value || row.client === searchedClient.value)

  return searchMatches && filterDefinitions.value.every((filter) => {
    const selectedOptions = selectedFilters[filter.key]
    return selectedOptions.length === 0 || selectedOptions.includes(row[filter.field])
  })
}))

function updateFilterOptions(filter, value, update) {
  update(() => {
    const searchValue = value.trim().toLowerCase()
    availableFilterOptions[filter.key] = searchValue
      ? filter.options.filter((option) => option.toLowerCase().includes(searchValue))
      : []
  })
}

async function fetchOnboardingEmployees() {
  try {
    rows.value = []
    const { data } = await api.get('/v1/users/onboarding', {
      params: {
        refresh: Date.now()
      }
    })
    rows.value = (Array.isArray(data) ? data : []).map((row) => {
      const primarySkill = row.primarySkill ?? row.primaryskill ?? row.primary_skill ?? ''
      return {
        ...row,
        primarySkill,
        primaryskill: primarySkill,
        joiningDate: row.joiningDate ? timestampToDate(row.joiningDate) : ''
      }
    })
    projects.value = [...new Set(data.map((row) => row.project).filter(Boolean))]
    clients.value = [...new Set(data.map((row) => row.client).filter(Boolean))]
  } catch (error) {
    console.error('Error fetching onboarding employees:', error)
    $q.notify({ type: 'negative', message: 'Unable to load onboarding employees.' })
  }
}

function syncSearchCriteria() {
  searchedEmployeeID.value = searchEmployeeID.value.trim()
  searchedEmployee.value = searchEmployee.value.trim()
  searchedProject.value = selectedProject.value ?? null
  searchedClient.value = selectedClient.value ?? null
  searchedTeamLead.value = selectedTeamLead.value ?? null
  searchedPrimarySkill.value = selectedPrimarySkill.value ?? null
}

function searchEmployees() {
  syncSearchCriteria()
}

function clearAdditionalFilters() {
  filterDefinitions.value.forEach((filter) => {
    selectedFilters[filter.key] = []
    availableFilterOptions[filter.key] = []
  })
}

watch(
  [searchEmployeeID, searchEmployee, selectedProject, selectedClient, selectedTeamLead, selectedPrimarySkill],
  () => {
    syncSearchCriteria()
  },
  { flush: 'sync' }
)

onMounted(() => {
  fetchOnboardingEmployees()
  window.addEventListener('focus', fetchOnboardingEmployees)
})

function resetFilters() {
  searchEmployeeID.value = ''
  searchEmployee.value = ''
  selectedProject.value = null
  selectedClient.value = null
  selectedTeamLead.value = null
  selectedPrimarySkill.value = null
  clearAdditionalFilters()
  syncSearchCriteria()
}
</script>

<style scoped>
.dashboard-content {
  max-width: 1440px;
  margin: 0 auto;
}

.metric-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.filter-menu {
  width: 280px;
  max-height: 70vh;
  overflow-y: auto;
}

.filter-menu :deep(.q-chip) {
  max-width: 100%;
}

.page-tabs {
  border-bottom: 1px solid #e5e7eb;
}
</style>
