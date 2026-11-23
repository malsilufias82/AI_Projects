<template>
  <q-page class="projects-page">
    <main class="projects-container" aria-labelledby="projects-title">
      <section class="page-header">
        <div class="header-copy">
          <div class="title-icon" aria-hidden="true"><q-icon name="work" /></div>
          <div>
            <h1 id="projects-title">Projects</h1>
            <p>Manage your projects and their points of contact.</p>
          </div>
        </div>
        <q-btn
          unelevated
          no-caps
          icon="add"
          label="Add Project"
          class="add-project-btn"
          @click="openAddDialog"
        />
      </section>

      <section class="stats-grid" aria-label="Project statistics">
        <q-card v-for="stat in stats" :key="stat.label" flat bordered class="stat-card">
          <q-card-section class="stat-content">
            <div class="stat-icon" :class="stat.tone"><q-icon :name="stat.icon" /></div>
            <div>
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-hint">{{ stat.hint }}</div>
            </div>
          </q-card-section>
        </q-card>
      </section>

      <q-card flat bordered class="projects-panel">
        <q-card-section class="filters-section">
          <div class="filters-row">
            <q-input v-model="search" outlined dense class="search-input" placeholder="Search projects by name..." aria-label="Search projects">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <q-select v-model="statusFilter" outlined dense emit-value map-options class="filter-select" :options="statusOptions" label="All Status" aria-label="Filter by status" />
            <q-select v-model="clientFilter" outlined dense emit-value map-options class="filter-select" :options="clientOptions" label="All Clients" aria-label="Filter by client" />
            <q-space />
            <q-btn flat no-caps icon="download" label="Export" class="export-btn" @click="exportProjects" />
          </div>
        </q-card-section>

        <q-card-section class="table-section q-pa-none">
          <q-table
            :rows="filteredProjects"
            :columns="columns"
            row-key="id"
            flat
            :loading="loading"
            class="projects-table"
          >
            <template #loading>
              <q-inner-loading showing color="primary"><q-spinner-dots size="36px" /></q-inner-loading>
            </template>
            <template #body="props">
              <q-tr :props="props" class="project-row">
                <q-td key="name" :props="props" class="name-cell">{{ props.row.name }}</q-td>
                <q-td key="client" :props="props" class="client-cell">{{ getClientName(props.row.client_id) }}</q-td>
                <q-td key="pocs" :props="props" class="pocs-cell">
                  <div v-for="(poc, idx) in props.row.pocs" :key="idx" class="poc-item">
                    <div>{{ poc.name }}</div>
                    <div class="poc-detail">{{ poc.email || poc.phone || '' }}</div>
                  </div>
                </q-td>
                <q-td key="status" :props="props"><q-badge class="status-chip" :class="statusClass(props.row.status)" :label="props.row.status" /></q-td>
                <q-td key="dates" :props="props" class="dates-cell">{{ formatDateRange(props.row.start_date, props.row.end_date) }}</q-td>
                <q-td key="actions" :props="props" class="actions-cell">
                  <q-btn flat round dense icon="edit" aria-label="Edit project" @click="openEditDialog(props.row)"><q-tooltip>Edit project</q-tooltip></q-btn>
                  <q-btn flat round dense icon="delete_outline" color="negative" aria-label="Delete project" @click="openDeleteDialog(props.row)"><q-tooltip>Delete project</q-tooltip></q-btn>
                </q-td>
              </q-tr>
            </template>
            <template #no-data>
              <div class="empty-state full-width">
                <div class="empty-icon"><q-icon name="work_off" /></div>
                <h2>No Projects Found</h2>
                <p>{{ projects.length ? 'Try adjusting your search or filters.' : 'Click Add Project to add your first project.' }}</p>
                <q-btn v-if="!projects.length" unelevated no-caps icon="add" label="Add Project" class="add-project-btn" @click="openAddDialog" />
              </div>
            </template>
          </q-table>
        </q-card-section>
        <q-separator />
        <!-- <q-card-section class="pagination-section">
          <span>Showing {{ filteredProjects.length ? `1–${filteredProjects.length}` : 0 }} of {{ filteredProjects.length }} projects</span>
          <div class="pagination-controls"><span>Rows per page:</span><q-btn flat dense no-caps label="100" icon-right="expand_more" /><q-btn flat round dense icon="chevron_left" disable /><q-btn flat round dense icon="chevron_right" disable /></div>
        </q-card-section> -->
      </q-card>
    </main>

    <q-dialog v-model="showProjectDialog" persistent>
      <q-card class="project-dialog">
        <q-card-section class="dialog-heading"><div><div class="dialog-title">{{ editingProject ? 'Edit Project' : 'Add Project' }}</div><div class="dialog-subtitle">{{ editingProject ? 'Update this project’s details.' : 'Add a new project to your workspace.' }}</div></div><q-btn flat round dense icon="close" aria-label="Close dialog" @click="closeProjectDialog" /></q-card-section>
        <q-separator />
        <q-card-section class="project-dialog-body">
          <q-form id="project-form" ref="projectFormRef" class="project-form" autocomplete="off" @submit="saveProject">
            <div class="form-grid">
              <q-input v-model="projectForm.name" outlined dense label="Project Name *" :rules="[requiredRule]" />
              <q-select v-model="projectForm.client_id" outlined dense emit-value map-options label="Client *" :options="clientSelectOptions" :rules="[requiredRule]" />
              <q-select v-model="projectForm.status" outlined dense emit-value map-options label="Status *" :options="dialogStatusOptions" :rules="[requiredRule]" />
              <q-select v-model="projectForm.team_lead" outlined dense emit-value map-options label="Team Lead" :options="userSelectOptions" />
              <!-- <q-input v-model="projectForm.pillar" outlined dense label="Pillar" /> -->
              <q-input v-model="projectForm.start_date" outlined dense label="Start Date" readonly :rules="[startDateRule]">
                <template #append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover transition-show="scale" transition-hide="scale"><q-date v-model="projectForm.start_date" mask="YYYY-MM-DD" /></q-popup-proxy></q-icon></template>
              </q-input>
              <q-input v-model="projectForm.end_date" outlined dense label="End Date" readonly :rules="[endDateRule]">
                <template #append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover transition-show="scale" transition-hide="scale"><q-date v-model="projectForm.end_date" mask="YYYY-MM-DD" /></q-popup-proxy></q-icon></template>
              </q-input>
              <q-input v-model="projectForm.description" outlined dense type="textarea" label="Description" class="full-width" />
              <div class="full-width pocs-section">
                <div class="section-label">Points of Contact</div>
                <div v-for="(poc, idx) in projectForm.pocs" :key="idx" class="poc-row">
                  <q-input v-model="poc.name" outlined dense label="Name *" :rules="[requiredRule]" class="poc-field" />
                  <q-input v-model="poc.email" outlined dense label="Email" class="poc-field" />
                  <q-input v-model="poc.phone" outlined dense label="Phone" class="poc-field" />
                  <q-input v-model="poc.role" outlined dense label="Role" class="poc-field" />
                  <div class="poc-delete-row">
                    <q-btn flat no-caps icon="delete" color="negative" label="Remove POC" @click="removePOC(idx)" />
                  </div>
                </div>
                <q-btn flat no-caps icon="add" label="Add POC" class="add-poc-btn" @click="addPOC" />
              </div>
            </div>
          </q-form>
        </q-card-section>
        <q-separator />
        <q-card-actions class="dialog-actions"><q-btn flat no-caps label="Cancel" @click="closeProjectDialog" /><q-btn unelevated no-caps :loading="saving" :label="editingProject ? 'Save changes' : 'Add Project'" class="add-project-btn" @click="saveProject" /></q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showDeleteDialog" persistent><q-card class="delete-dialog"><q-card-section class="dialog-heading"><div class="delete-icon"><q-icon name="delete_outline" /></div><div><div class="dialog-title">Delete Project</div><div class="dialog-subtitle">This action cannot be undone.</div></div></q-card-section><q-card-section class="q-pt-none">Are you sure you want to delete <strong>{{ projectToDelete?.name }}</strong>?</q-card-section><q-card-actions align="right"><q-btn flat no-caps label="Cancel" @click="showDeleteDialog = false" /><q-btn unelevated no-caps color="negative" :loading="deleting" label="Delete" @click="deleteProject" /></q-card-actions></q-card></q-dialog>
  </q-page>
</template>
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useQuasar, exportFile } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const search = ref('')
const statusFilter = ref('all')
const clientFilter = ref('all')
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const projects = ref([])
const clients = ref([])
const users = ref([])
const showProjectDialog = ref(false)
const showDeleteDialog = ref(false)
const editingProject = ref(null)
const projectToDelete = ref(null)
const projectFormRef = ref(null)
const emptyProjectForm = () => ({ name: '', client_id: '', pocs: [], description: '', status: 'active', start_date: '', end_date: '', team_lead: '', pillar: '' })
const projectForm = ref(emptyProjectForm())

const columns = [
  { name: 'name', label: 'Project Name', align: 'left', field: 'name' },
  { name: 'client', label: 'Client', align: 'left', field: 'client_id' },
  { name: 'pocs', label: 'POCs', align: 'left', field: 'pocs' },
  { name: 'status', label: 'Status', align: 'left', field: 'status' },
  { name: 'dates', label: 'Date Range', align: 'left', field: 'start_date' },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions' }
]
const statusOptions = [{ label: 'All Status', value: 'all' }, { label: 'Active', value: 'active' }, { label: 'Inactive', value: 'inactive' }, { label: 'On Hold', value: 'on_hold' }, { label: 'Completed', value: 'completed' }]
const dialogStatusOptions = statusOptions.slice(1)
const clientOptions = computed(() => [{ label: 'All Clients', value: 'all' }, ...clients.value.map(c => ({ label: c.name, value: c.id }))])
const clientSelectOptions = computed(() => clients.value.map(c => ({ label: c.name, value: c.id })))
const userSelectOptions = computed(() => users.value.map(u => ({ label: `${u.name} (${u.email})`, value: u.id, name: u.name, email: u.email })))
const filteredProjects = computed(() => projects.value.filter(project => {
  const term = search.value.trim().toLowerCase()
  return (!term || project.name.toLowerCase().includes(term)) && (statusFilter.value === 'all' || project.status === statusFilter.value) && (clientFilter.value === 'all' || project.client_id === clientFilter.value)
}))
const stats = computed(() => [
  { label: 'Total Projects', value: projects.value.length, hint: 'All projects', icon: 'work', tone: 'indigo' },
  { label: 'Active Projects', value: projects.value.filter(p => p.status === 'active').length, hint: 'Currently active', icon: 'play_circle', tone: 'green' },
  { label: 'On Hold', value: projects.value.filter(p => p.status === 'on_hold').length, hint: 'Paused projects', icon: 'pause_circle', tone: 'orange' },
  { label: 'Completed', value: projects.value.filter(p => p.status === 'completed').length, hint: 'Finished projects', icon: 'check_circle', tone: 'blue' }
])

const requiredRule = value => !!value || 'This field is required'
const startDateRule = value => !value || !projectForm.value.end_date || value < projectForm.value.end_date || 'Start date must be before end date'
const endDateRule = value => !value || !projectForm.value.start_date || value > projectForm.value.start_date || 'End date must be after start date'

watch(() => projectForm.value.start_date, () => projectFormRef.value?.validate())
const statusClass = status => {
  const classes = { active: 'active-chip', inactive: 'inactive-chip', on_hold: 'on-hold-chip', completed: 'completed-chip' }
  return classes[status] || 'inactive-chip'
}
const formatDate = date => date ? new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(date)) : '—'
const formatDateRange = (start, end) => {
  if (!start && !end) return '—'
  const s = formatDate(start)
  const e = formatDate(end)
  return start && end ? `${s} – ${e}` : s || e
}
const getClientName = clientId => {
  const client = clients.value.find(c => c.id === clientId)
  return client ? client.name : 'Unknown'
}

async function fetchProjects() { loading.value = true; try { const { data } = await api.get('/v1/projects?page=1&page_size=100'); projects.value = data.items.map(project => ({ id: project.id, name: project.name, client_id: project.client_id, pocs: project.pocs || [], description: project.description, status: project.status, start_date: project.start_date, end_date: project.end_date, team_lead: project.team_lead, pillar: project.pillar })) } catch (error) { console.error('Error fetching projects:', error); $q.notify({ type: 'negative', message: 'Unable to load projects. Please try again.' }) } finally { loading.value = false } }
async function fetchClients() { try { const { data } = await api.get('/v1/clients?page=1&page_size=100'); clients.value = data.items.map(client => ({ id: client.id, name: client.name })) } catch (error) { console.error('Error fetching clients:', error) } }
async function fetchUsers() { try { const { data } = await api.get('/v1/users?page=1&page_size=100'); users.value = data.items.map(user => ({ id: user.id, name: `${user.first_name} ${user.last_name}`.trim() || user.email, email: user.email })) } catch (error) { console.error('Error fetching users:', error) } }
function openAddDialog() { editingProject.value = null; projectForm.value = emptyProjectForm(); showProjectDialog.value = true }
function openEditDialog(project) { editingProject.value = project; projectForm.value = { ...emptyProjectForm(), name: project.name, client_id: project.client_id, status: project.status, description: project.description, start_date: project.start_date, end_date: project.end_date, team_lead: project.team_lead, pillar: project.pillar, pocs: project.pocs ? [...project.pocs] : [] }; showProjectDialog.value = true }
function closeProjectDialog() { showProjectDialog.value = false; editingProject.value = null }
function addPOC() { projectForm.value.pocs.push({ name: '', email: '', phone: '', role: '' }) }
function removePOC(idx) { projectForm.value.pocs.splice(idx, 1) }
async function saveProject() { const valid = await projectFormRef.value.validate(); if (!valid) return; const isEditing = !!editingProject.value; saving.value = true; try { if (isEditing) { await api.patch(`/v1/projects/${editingProject.value.id}`, projectForm.value) } else { await api.post('/v1/projects', projectForm.value) } await fetchProjects(); closeProjectDialog(); $q.notify({ type: 'positive', message: isEditing ? 'Project updated successfully.' : 'Project added successfully.' }) } catch (error) { console.error('Error saving project:', error); $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to save the project.' }) } finally { saving.value = false } }
function openDeleteDialog(project) { projectToDelete.value = project; showDeleteDialog.value = true }
async function deleteProject() { deleting.value = true; try { await api.delete(`/v1/projects/${projectToDelete.value.id}`); await fetchProjects(); showDeleteDialog.value = false; $q.notify({ type: 'positive', message: 'Project deleted successfully.' }) } catch (error) { console.error('Error deleting project:', error); $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to delete the project.' }) } finally { deleting.value = false } }
function exportProjects() { const header = 'Name,Client,POCs,Status,Start Date,End Date'; const rows = filteredProjects.value.map(project => [project.name, getClientName(project.client_id), project.pocs.map(p => p.name).join('; '), project.status, formatDate(project.start_date), formatDate(project.end_date)].map(value => `"${String(value).replaceAll('"', '""')}"`).join(',')); exportFile('projects.csv', [header, ...rows].join('\n'), 'text/csv'); }
onMounted(() => { fetchProjects(); fetchClients(); fetchUsers() })
</script>

<style scoped>
.projects-page {
  min-height: 100%;
  background: #f8fafc;
  color: #1e293b;
}

.projects-container {
  max-width: 1680px;
  margin: 0 auto;
  padding: 28px 32px 40px;
}

.page-header,
.header-copy,
.stat-content,
.filters-row,
.pagination-section,
.pagination-controls,
.dialog-heading {
  display: flex;
  align-items: center;
}

.page-header {
  justify-content: space-between;
  margin-bottom: 28px;
}

.header-copy {
  gap: 16px;
}

.title-icon {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 14px;
  color: #4f46e5;
  background: #eef2ff;
  font-size: 26px;
}

.header-copy h1 {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
  font-weight: 750;
  letter-spacing: -.6px;
}

.header-copy p {
  margin: 5px 0 0;
  color: #64748b;
  font-size: 14px;
}

.add-project-btn {
  min-height: 42px;
  padding: 0 17px;
  border-radius: 10px;
  color: white;
  background: #4f46e5;
  box-shadow: 0 7px 18px rgba(79, 70, 229, .24);
  font-weight: 650;
}

.add-project-btn:hover {
  background: #4338ca;
  transform: translateY(-1px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 22px;
}

.stat-card,
.projects-panel {
  border: 1px solid #e6eaf0;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 3px 14px rgba(15, 23, 42, .035);
}

.stat-content {
  gap: 17px;
  padding: 25px;
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  font-size: 28px;
}

.stat-icon.indigo {
  color: #4f46e5;
  background: #eef2ff;
}

.stat-icon.green {
  color: #16a34a;
  background: #e9f9ee;
}

.stat-icon.orange {
  color: #f97316;
  background: #fff3e7;
}

.stat-icon.blue {
  color: #2563eb;
  background: #ebf3ff;
}

.stat-label {
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
}

.stat-value {
  margin-top: 3px;
  font-size: 25px;
  font-weight: 750;
}

.stat-hint {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 13px;
}

.projects-panel {
  overflow: hidden;
}

.filters-section {
  padding: 26px 20px 24px;
}

.filters-row {
  gap: 16px;
}

.search-input {
  width: 395px;
}

.filter-select {
  width: 190px;
}

.export-btn {
  min-height: 42px;
  border: 1px solid #dfe5ed;
  border-radius: 9px;
  color: #334155;
  font-weight: 600;
}

.projects-table :deep(th) {
  height: 54px;
  color: #334155;
  font-weight: 700;
  font-size: 13px;
}

.projects-table :deep(thead tr) {
  background: #fbfcfe;
}

.projects-table :deep(td) {
  height: 84px;
  border-color: #edf0f5;
}

.project-row {
  transition: background .18s ease;
}

.project-row:hover {
  background: #f8faff;
}

.name-cell {
  color: #172033;
  font-size: 14px;
  font-weight: 700;
}

.client-cell {
  color: #64748b;
  font-size: 13px;
}

.pocs-cell {
  color: #64748b;
  font-size: 13px;
}

.poc-item {
  margin-bottom: 4px;
}

.poc-detail {
  color: #94a3b8;
  font-size: 12px;
}

.dates-cell {
  color: #64748b;
  font-size: 13px;
}

.status-chip {
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid;
  border-radius: 7px;
  font-weight: 650;
  font-size: 12px;
}

.active-chip {
  color: #16a34a;
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.inactive-chip {
  color: #64748b;
  border-color: #d7dde5;
  background: #f8fafc;
}

.on-hold-chip {
  color: #f97316;
  border-color: #fed7aa;
  background: #fff7ed;
}

.completed-chip {
  color: #2563eb;
  border-color: #bfdbfe;
  background: #f5f9ff;
}

.actions-cell {
  white-space: nowrap;
}

.pagination-section {
  justify-content: space-between;
  min-height: 68px;
  padding: 0 18px;
  color: #475569;
  font-size: 14px;
}

.pagination-controls {
  gap: 8px;
}

.empty-state {
  padding: 70px 20px;
  text-align: center;
}

.empty-icon {
  display: grid;
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  place-items: center;
  color: #818cf8;
  background: #eef2ff;
  border-radius: 50%;
  font-size: 32px;
}

.empty-state h2 {
  margin: 0;
  font-size: 18px;
}

.empty-state p {
  margin: 7px 0 20px;
  color: #64748b;
}

.project-dialog {
  display: flex;
  width: min(900px, calc(100vw - 48px));
  max-height: calc(100dvh - 48px);
  flex-direction: column;
  overflow: hidden;
  border-radius: 18px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, .22);
}

.dialog-heading {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 28px;
  background: #fff;
}

.project-dialog-body {
  min-height: 0;
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 20px 28px;
}

.project-form {
  padding: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}

.full-width {
  grid-column: 1 / -1;
}

.project-dialog :deep(.q-field__control) {
  min-height: 46px;
  height: 46px;
  border-radius: 9px;
}

.project-dialog :deep(.q-field--dense .q-field__label) {
  top: 13px;
}

.project-dialog :deep(.q-field--float .q-field__label) {
  top: 7px;
}

.project-dialog :deep(.q-field__native),
.project-dialog :deep(.q-field__input) {
  min-height: 46px;
}

.pocs-section {
  margin-top: 8px;
}

.section-label {
  color: #334155;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.poc-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  align-items: top;
  margin-bottom: 10px;
}
.poc-delete-row {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.poc-field {
  margin: 0;
}

.add-poc-btn {
  margin-top: 8px;
  color: #4f46e5;
}

.dialog-title {
  color: #1e293b;
  font-size: 19px;
  font-weight: 750;
}

.dialog-subtitle {
  margin-top: 3px;
  color: #64748b;
  font-size: 13px;
}

.dialog-actions {
  z-index: 1;
  flex: 0 0 auto;
  justify-content: flex-end;
  gap: 10px;
  min-height: 72px;
  margin: 0;
  padding: 14px 28px;
  background: #fff;
}

.delete-dialog {
  width: min(440px, calc(100vw - 32px));
  border-radius: 16px;
}

.delete-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  color: #ef4444;
  background: #fef2f2;
  border-radius: 12px;
  font-size: 23px;
}

@media (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filters-row {
    flex-wrap: wrap;
  }

  .filters-row .q-space {
    display: none;
  }

  .export-btn {
    margin-left: auto;
  }
}

@media (max-width: 900px) {
  .project-dialog {
    width: min(720px, calc(100vw - 32px));
  }

  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .projects-container {
    padding: 20px 16px 100px;
  }

  .page-header {
    align-items: flex-start;
    gap: 12px;
  }

  .header-copy {
    gap: 11px;
  }

  .title-icon {
    width: 42px;
    height: 42px;
  }

  .header-copy h1 {
    font-size: 24px;
  }

  .header-copy p {
    max-width: 200px;
  }

  .add-project-btn {
    padding: 0 12px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-content {
    padding: 17px;
  }

  .filters-section {
    padding: 16px;
  }

  .filters-row {
    display: grid;
    grid-template-columns: 1fr;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }

  .export-btn {
    margin-left: 0;
  }

  .projects-table :deep(thead) {
    display: none;
  }

  .projects-table :deep(tbody tr) {
    display: grid;
    grid-template-columns: 1fr auto;
    padding: 15px;
    border-bottom: 1px solid #edf0f5;
  }

  .projects-table :deep(tbody td) {
    display: none;
    height: auto;
    padding: 0;
    border: 0;
  }

  .projects-table :deep(tbody td:first-child),
  .projects-table :deep(tbody td:last-child) {
    display: table-cell;
  }

  .pagination-section {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
    padding: 15px 16px;
  }

  .pagination-controls {
    display: none;
  }

  .project-dialog {
    width: calc(100vw - 20px);
    max-height: calc(100dvh - 20px);
  }

  .dialog-heading,
  .project-dialog-body,
  .dialog-actions {
    padding-right: 18px;
    padding-left: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .poc-row {
    grid-template-columns: 1fr auto;
  }

  .dialog-actions {
    min-height: 66px;
  }
}
</style>
