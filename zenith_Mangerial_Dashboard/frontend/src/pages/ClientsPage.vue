<template>
  <q-page class="clients-page">
    <main class="clients-container" aria-labelledby="clients-title">
      <section class="page-header">
        <div class="header-copy">
          <div class="title-icon" aria-hidden="true"><q-icon name="business" /></div>
          <div>
            <h1 id="clients-title">Clients</h1>
            <p>Manage your clients and their contact information.</p>
          </div>
        </div>
        <q-btn unelevated no-caps icon="add" label="Add Client" class="add-client-btn" @click="openAddDialog" />
      </section>

      <section class="stats-grid" aria-label="Client statistics">
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

      <q-card flat bordered class="clients-panel">
        <q-card-section class="filters-section">
          <div class="filters-row">
            <q-input v-model="search" outlined dense class="search-input" placeholder="Search clients by name..."
              aria-label="Search clients">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <q-select v-model="statusFilter" outlined dense emit-value map-options class="filter-select"
              :options="statusOptions" label="All Status" aria-label="Filter by status" />
            <q-space />
            <q-btn flat no-caps icon="download" label="Export" class="export-btn" @click="exportClients" />
          </div>
        </q-card-section>

        <q-card-section class="table-section q-pa-none">
          <q-table :rows="filteredClients" :columns="columns" row-key="id" flat :loading="loading" class="clients-table">
            <template #loading>
              <q-inner-loading showing color="primary"><q-spinner-dots size="36px" /></q-inner-loading>
            </template>
            <template #body="props">
              <q-tr :props="props" class="client-row">
                <q-td key="name" :props="props" class="name-cell">{{ props.row.name }}</q-td>
                <q-td key="contact" :props="props" class="contact-cell">
                  <div v-for="(person, idx) in props.row.contact_persons" :key="idx" class="contact-item">
                    <div>{{ person.name }}</div>
                    <div class="contact-detail">{{ person.email || person.phone || '' }}</div>
                  </div>
                </q-td>
                <q-td key="address" :props="props" class="address-cell">{{ props.row.address || '—' }}</q-td>
                <q-td key="status" :props="props"><q-badge class="status-chip" :class="statusClass(props.row.status)"
                    :label="props.row.status" /></q-td>
                <q-td key="created" :props="props" class="created-cell">{{ formatDate(props.row.created_at) }}</q-td>
                <q-td key="actions" :props="props" class="actions-cell">
                  <q-btn flat round dense icon="edit" aria-label="Edit client"
                    @click="openEditDialog(props.row)"><q-tooltip>Edit client</q-tooltip></q-btn>
                  <q-btn flat round dense icon="delete_outline" color="negative" aria-label="Delete client"
                    @click="openDeleteDialog(props.row)"><q-tooltip>Delete client</q-tooltip></q-btn>
                </q-td>
              </q-tr>
            </template>
            <template #no-data>
              <div class="empty-state full-width">
                <div class="empty-icon"><q-icon name="business_off" /></div>
                <h2>No Clients Found</h2>
                <p>
                  {{ clients.length ? 'Try adjusting your search or filters.' : 'Click Add Client to add your first client.' }}
                </p>
                <q-btn v-if="!clients.length" unelevated no-caps icon="add" label="Add Client" class="add-client-btn"
                  @click="openAddDialog" />
              </div>
            </template>
          </q-table>
        </q-card-section>
        <q-separator />
        <!-- <q-card-section class="pagination-section">
          <span>Showing {{ filteredClients.length ? `1–${filteredClients.length}` : 0 }} of {{ filteredClients.length }}
            clients</span>
          <div class="pagination-controls"><span>Rows per page:</span><q-btn flat dense no-caps label="100"
              icon-right="expand_more" /><q-btn flat round dense icon="chevron_left" disable /><q-btn flat round dense
              icon="chevron_right" disable /></div>
        </q-card-section> -->
      </q-card>
    </main>

    <q-dialog v-model="showClientDialog" persistent>
      <q-card class="client-dialog">
        <q-card-section class="dialog-heading">
          <div>
            <div class="dialog-title">{{ editingClient ? 'Edit Client' : 'Add Client' }}</div>
            <div class="dialog-subtitle">
              {{ editingClient ? 'Update this client’s details.' : 'Add a new client to your workspace.' }}
            </div>
          </div><q-btn flat round dense icon="close" aria-label="Close dialog" @click="closeClientDialog" />
        </q-card-section>
        <q-separator />
        <q-card-section class="client-dialog-body">
          <q-form id="client-form" ref="clientFormRef" class="client-form" autocomplete="off" @submit="saveClient">
            <div class="form-grid">
              <q-input v-model="clientForm.name" outlined dense label="Client Name *" :rules="[requiredRule]" />
              <q-input v-model="clientForm.address" outlined dense label="Address" />
              <q-select v-model="clientForm.status" outlined dense emit-value map-options label="Status *"
                :options="dialogStatusOptions" :rules="[requiredRule]" />
              <q-input v-model="clientForm.description" outlined dense type="textarea" label="Description"
                class="full-width" />
              <div class="full-width contact-section">
                <div class="section-label">Contact Persons</div>
                <div v-for="(contact, idx) in clientForm.contact_persons" :key="idx" class="contact-row">
                  <q-input v-model="contact.name" outlined dense label="Name *" :rules="[requiredRule]"
                    class="contact-field" />
                  <q-input v-model="contact.email" outlined dense label="Email" class="contact-field" />
                  <q-input v-model="contact.phone" outlined dense label="Phone" class="contact-field" />
                  <q-input v-model="contact.role" outlined dense label="Role" class="contact-field" />
                  <div class="contact-delete-row">
                    <q-btn flat no-caps icon="delete" color="negative" label="Remove Contact" @click="removeContact(idx)" />
                  </div>
                </div>
                <q-btn flat no-caps icon="add" label="Add Contact" class="add-contact-btn" @click="addContact" />
              </div>
            </div>
          </q-form>
        </q-card-section>
        <q-separator />
        <q-card-actions class="dialog-actions"><q-btn flat no-caps label="Cancel" @click="closeClientDialog" /><q-btn
            unelevated no-caps :loading="saving" :label="editingClient ? 'Save changes' : 'Add Client'"
            class="add-client-btn" @click="saveClient" /></q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showDeleteDialog" persistent><q-card class="delete-dialog"><q-card-section
          class="dialog-heading">
          <div class="delete-icon"><q-icon name="delete_outline" /></div>
          <div>
            <div class="dialog-title">Delete Client</div>
            <div class="dialog-subtitle">This action cannot be undone.</div>
          </div>
        </q-card-section><q-card-section class="q-pt-none">Are you sure you want to delete <strong>{{
          clientToDelete?.name
            }}</strong>?</q-card-section><q-card-actions align="right"><q-btn flat no-caps label="Cancel"
            @click="showDeleteDialog = false" /><q-btn unelevated no-caps color="negative" :loading="deleting"
            label="Delete" @click="deleteClient" /></q-card-actions></q-card></q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar, exportFile } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const search = ref('')
const statusFilter = ref('all')
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const clients = ref([])
const showClientDialog = ref(false)
const showDeleteDialog = ref(false)
const editingClient = ref(null)
const clientToDelete = ref(null)
const clientFormRef = ref(null)
const emptyClientForm = () => ({ name: '', address: '', status: 'active', description: '', contact_persons: [] })
const clientForm = ref(emptyClientForm())

const columns = [
  { name: 'name', label: 'Client Name', align: 'left', field: 'name' },
  { name: 'contact', label: 'Contact Persons', align: 'left', field: 'contact_persons' },
  { name: 'address', label: 'Address', align: 'left', field: 'address' },
  { name: 'status', label: 'Status', align: 'left', field: 'status' },
  { name: 'created', label: 'Created On', align: 'left', field: 'created_at' },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions' }
]
const statusOptions = [{ label: 'All Status', value: 'all' }, { label: 'Active', value: 'active' }, { label: 'Inactive', value: 'inactive' }, { label: 'Pending', value: 'pending' }]
const dialogStatusOptions = statusOptions.slice(1)
const filteredClients = computed(() => clients.value.filter(client => {
  const term = search.value.trim().toLowerCase()
  return (!term || client.name.toLowerCase().includes(term)) && (statusFilter.value === 'all' || client.status === statusFilter.value)
}))
const stats = computed(() => [
  { label: 'Total Clients', value: clients.value.length, hint: 'All clients', icon: 'business', tone: 'indigo' },
  { label: 'Active Clients', value: clients.value.filter(c => c.status === 'active').length, hint: 'Currently active', icon: 'verified_user', tone: 'green' },
  { label: 'Inactive Clients', value: clients.value.filter(c => c.status === 'inactive').length, hint: 'Not active', icon: 'block', tone: 'red' },
  { label: 'Pending Clients', value: clients.value.filter(c => c.status === 'pending').length, hint: 'Awaiting setup', icon: 'schedule', tone: 'orange' }
])

const requiredRule = value => !!value || 'This field is required'
const statusClass = status => {
  const classes = { active: 'active-chip', inactive: 'inactive-chip', pending: 'pending-chip' }
  return classes[status] || 'inactive-chip'
}
const formatDate = date => date ? new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(date)) : '—'

async function fetchClients() { loading.value = true; try { const { data } = await api.get('/v1/clients?page=1&page_size=100'); clients.value = data.items.map(client => ({ id: client.id, name: client.name, contact_persons: client.contact_persons || [], address: client.address, status: client.status, description: client.description, created_at: client.created_at })) } catch (error) { console.error('Error fetching clients:', error); $q.notify({ type: 'negative', message: 'Unable to load clients. Please try again.' }) } finally { loading.value = false } }
function openAddDialog() { editingClient.value = null; clientForm.value = emptyClientForm(); showClientDialog.value = true }
function openEditDialog(client) { editingClient.value = client; clientForm.value = { ...emptyClientForm(), name: client.name, address: client.address, status: client.status, description: client.description, contact_persons: client.contact_persons ? [...client.contact_persons] : [] }; showClientDialog.value = true }
function closeClientDialog() { showClientDialog.value = false; editingClient.value = null }
function addContact() { clientForm.value.contact_persons.push({ name: '', email: '', phone: '', role: '' }) }
function removeContact(idx) { clientForm.value.contact_persons.splice(idx, 1) }
async function saveClient() { const valid = await clientFormRef.value.validate(); if (!valid) return; const isEditing = !!editingClient.value; saving.value = true; try { if (isEditing) { await api.patch(`/v1/clients/${editingClient.value.id}`, clientForm.value) } else { await api.post('/v1/clients', clientForm.value) } await fetchClients(); closeClientDialog(); $q.notify({ type: 'positive', message: isEditing ? 'Client updated successfully.' : 'Client added successfully.' }) } catch (error) { console.error('Error saving client:', error); $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to save the client.' }) } finally { saving.value = false } }
function openDeleteDialog(client) { clientToDelete.value = client; showDeleteDialog.value = true }
async function deleteClient() { deleting.value = true; try { await api.delete(`/v1/clients/${clientToDelete.value.id}`); await fetchClients(); showDeleteDialog.value = false; $q.notify({ type: 'positive', message: 'Client deleted successfully.' }) } catch (error) { console.error('Error deleting client:', error); $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to delete the client.' }) } finally { deleting.value = false } }
function exportClients() { const header = 'Name,Contact Persons,Address,Status,Created On'; const rows = filteredClients.value.map(client => [client.name, client.contact_persons.map(c => c.name).join('; '), client.address || '', client.status, formatDate(client.created_at)].map(value => `"${String(value).replaceAll('"', '""')}"`).join(',')); exportFile('clients.csv', [header, ...rows].join('\n'), 'text/csv'); }
onMounted(fetchClients)
</script>

<style scoped>
.clients-page {
  min-height: 100%;
  background: #f8fafc;
  color: #1e293b;
}

.clients-container {
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

.add-client-btn {
  min-height: 42px;
  padding: 0 17px;
  border-radius: 10px;
  color: white;
  background: #4f46e5;
  box-shadow: 0 7px 18px rgba(79, 70, 229, .24);
  font-weight: 650;
}

.add-client-btn:hover {
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
.clients-panel {
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

.stat-icon.red {
  color: #ef4444;
  background: #fef2f2;
}

.stat-icon.orange {
  color: #f97316;
  background: #fff3e7;
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

.clients-panel {
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

.clients-table :deep(th) {
  height: 54px;
  color: #334155;
  font-weight: 700;
  font-size: 13px;
}

.clients-table :deep(thead tr) {
  background: #fbfcfe;
}

.clients-table :deep(td) {
  height: 84px;
  border-color: #edf0f5;
}

.client-row {
  transition: background .18s ease;
}

.client-row:hover {
  background: #f8faff;
}

.name-cell {
  color: #172033;
  font-size: 14px;
  font-weight: 700;
}

.contact-cell {
  color: #64748b;
  font-size: 13px;
}

.contact-item {
  margin-bottom: 4px;
}

.contact-detail {
  color: #94a3b8;
  font-size: 12px;
}

.address-cell,
.created-cell {
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

.pending-chip {
  color: #f97316;
  border-color: #fed7aa;
  background: #fff7ed;
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

.client-dialog {
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

.client-dialog-body {
  min-height: 0;
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 20px 28px;
}

.client-form {
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

.client-dialog :deep(.q-field__control) {
  min-height: 46px;
  height: 46px;
  border-radius: 9px;
}

.client-dialog :deep(.q-field--dense .q-field__label) {
  top: 13px;
}

.client-dialog :deep(.q-field--float .q-field__label) {
  top: 7px;
}

.client-dialog :deep(.q-field__native),
.client-dialog :deep(.q-field__input) {
  min-height: 46px;
}

.contact-section {
  margin-top: 8px;
}

.section-label {
  color: #334155;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.contact-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  align-items: top;
  margin-bottom: 10px;
}
.contact-delete-row {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.contact-field {
  margin: 0;
}

.add-contact-btn {
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
  .client-dialog {
    width: min(720px, calc(100vw - 32px));
  }

  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .clients-container {
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

  .add-client-btn {
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

  .clients-table :deep(thead) {
    display: none;
  }

  .clients-table :deep(tbody tr) {
    display: grid;
    grid-template-columns: 1fr auto;
    padding: 15px;
    border-bottom: 1px solid #edf0f5;
  }

  .clients-table :deep(tbody td) {
    display: none;
    height: auto;
    padding: 0;
    border: 0;
  }

  .clients-table :deep(tbody td:first-child),
  .clients-table :deep(tbody td:last-child) {
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

  .client-dialog {
    width: calc(100vw - 20px);
    max-height: calc(100dvh - 20px);
  }

  .dialog-heading,
  .client-dialog-body,
  .dialog-actions {
    padding-right: 18px;
    padding-left: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .contact-row {
    grid-template-columns: 1fr auto;
  }

  .dialog-actions {
    min-height: 66px;
  }
}
</style>
