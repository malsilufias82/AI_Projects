<template>
  <q-page class="members-page">
    <main class="members-container" aria-labelledby="members-title">
      <section class="page-header">
        <div class="header-copy">
          <div class="title-icon" aria-hidden="true"><q-icon name="group" /></div>
          <div>
            <h1 id="members-title">Members</h1>
            <p>Manage your team members and their access permissions.</p>
          </div>
        </div>
        <q-btn
          unelevated
          no-caps
          icon="person_add"
          label="Add Member"
          class="add-member-btn"
          @click="openAddDialog"
        />
      </section>

      <section class="stats-grid" aria-label="Member statistics">
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

      <q-card flat bordered class="members-panel">
        <q-card-section class="filters-section">
          <div class="filters-row">
            <q-input v-model="search" outlined dense class="search-input" placeholder="Search members by name or email..." aria-label="Search members">
              <template #prepend><q-icon name="search" /></template>
            </q-input>
            <q-select v-model="roleFilter" outlined dense emit-value map-options class="filter-select" :options="roleOptions" label="All Roles" aria-label="Filter by role" />
            <q-select v-model="statusFilter" outlined dense emit-value map-options class="filter-select" :options="statusOptions" label="All Status" aria-label="Filter by status" />
            <q-space />
            <q-btn flat no-caps icon="download" label="Export" class="export-btn" @click="exportMembers" />
          </div>
        </q-card-section>

        <q-card-section class="table-section q-pa-none">
          <q-table
            :rows="filteredMembers"
            :columns="columns"
            row-key="id"
            flat
            :loading="loading"
            class="members-table"
          >
            <template #loading>
              <q-inner-loading showing color="primary"><q-spinner-dots size="36px" /></q-inner-loading>
            </template>
            <template #body="props">
              <q-tr :props="props" class="member-row">
                <q-td key="member" :props="props">
                  <div class="member-identity">
                    <q-avatar size="44px" class="member-avatar" color="indigo-1" text-color="primary">
                      <img v-if="props.row.avatar" :src="props.row.avatar" :alt="`${props.row.name} avatar`" @error="props.row.avatar = ''">
                      <span v-else>{{ initials(props.row.name) }}</span>
                    </q-avatar>
                    <div>
                      <div class="member-name">{{ props.row.name }}</div>
                      <div class="member-email">{{ props.row.email }}</div>
                    </div>
                  </div>
                </q-td>
                <q-td key="department" :props="props" class="department-cell">{{ props.row.department }}</q-td>
                <q-td key="role" :props="props"><q-badge class="role-chip" :class="props.row.role === 'admin' ? 'admin-chip' : 'user-chip'" :label="roleLabel(props.row.role)" /></q-td>
                <q-td key="status" :props="props"><q-badge class="status-chip" :class="props.row.status === 'Active' ? 'active-chip' : 'inactive-chip'" :label="props.row.status" /></q-td>
                <q-td key="joined" :props="props" class="joined-cell">{{ formatDate(props.row.createdAt) }}</q-td>
                <q-td key="actions" :props="props" class="actions-cell">
                  <q-btn flat round dense icon="edit" aria-label="Edit member" @click="openEditDialog(props.row)"><q-tooltip>Edit member</q-tooltip></q-btn>
                  <q-btn flat round dense icon="send" color="primary" :loading="activatingUser === props.row.id" aria-label="Send activation email" @click="handleActivate(props.row.id)"><q-tooltip>Send activation email</q-tooltip></q-btn>
                  <q-btn flat round dense icon="delete_outline" color="negative" aria-label="Delete member" @click="openDeleteDialog(props.row)"><q-tooltip>Delete member</q-tooltip></q-btn>
                </q-td>
              </q-tr>
            </template>
            <template #no-data>
              <div class="empty-state full-width">
                <div class="empty-icon"><q-icon name="group_off" /></div>
                <h2>No Members Found</h2>
                <p>{{ members.length ? 'Try adjusting your search or filters.' : 'Click Add Member to invite your first member.' }}</p>
                <q-btn v-if="!members.length" unelevated no-caps icon="person_add" label="Add Member" class="add-member-btn" @click="openAddDialog" />
              </div>
            </template>
          </q-table>
        </q-card-section>
        <q-separator />
        <!-- <q-card-section class="pagination-section">
          <span>Showing {{ filteredMembers.length ? `1–${filteredMembers.length}` : 0 }} of {{ filteredMembers.length }} members</span>
          <div class="pagination-controls"><span>Rows per page:</span><q-btn flat dense no-caps label="100" icon-right="expand_more" /><q-btn flat round dense icon="chevron_left" disable /><q-btn flat round dense icon="chevron_right" disable /></div>
        </q-card-section> -->
      </q-card>
    </main>

    <q-dialog v-model="showMemberDialog" persistent>
      <q-card class="member-dialog">
        <q-card-section class="dialog-heading"><div><div class="dialog-title">{{ editingMember ? 'Edit Member' : 'Add Member' }}</div><div class="dialog-subtitle">{{ editingMember ? 'Update this member’s account details.' : 'Invite a teammate to join your workspace.' }}</div></div><q-btn flat round dense icon="close" aria-label="Close dialog" @click="closeMemberDialog" /></q-card-section>
        <q-separator />
        <q-card-section class="member-dialog-body">
          <q-form id="member-form" ref="memberFormRef" class="member-form" autocomplete="off" @submit="saveMember">
            <div class="form-grid">
              <q-input v-model="memberForm.firstName" outlined dense label="First Name *" :rules="[requiredRule, fieldRules.firstName]" />
              <q-input v-model="memberForm.lastName" outlined dense label="Last Name *" :rules="[requiredRule, fieldRules.lastName]" />
              <q-input v-model="memberForm.employeeId" outlined dense label="Employee ID *" :rules="[requiredRule, fieldRules.employeeId]" />
              <q-input v-model="memberForm.client" outlined dense label="Client *" :rules="[requiredRule, fieldRules.client]" />
              <q-input v-model="memberForm.project" outlined dense label="Project *" :rules="[requiredRule, fieldRules.project]" />
              <q-input v-model="memberForm.vlinker" outlined dense label="VLinker *" :rules="[requiredRule, fieldRules.vlinker]" />
              <q-select
                v-model="memberForm.teamLead"
                outlined
                dense
                :use-input="memberForm.teamLead == null"
                input-debounce="0"
                clearable
                :options="filteredTeamLeads"
                @filter="filterTeamLeads"
                label="Team Lead"
                option-value="value"
                emit-value
                map-options
                option-dense
                options-dense
                menu-offset="110"
                label-always-floating
              >
                <template #no-option>
                  <q-item>
                    <q-item-section class="text-italic">No team lead found</q-item-section>
                  </q-item>
                </template>
              </q-select>
              <q-input v-model="memberForm.devQa" outlined dense label="Dev/QA *" :rules="[requiredRule, fieldRules.devQa]" />
              <q-select v-model="memberForm.status" outlined dense emit-value map-options label="Status *" :options="dialogStatusOptions" :rules="[requiredRule, fieldRules.status]" />
              <q-input v-model="memberForm.roleDescription" outlined dense label="Role Description *" :rules="[requiredRule, fieldRules.roleDescription]" />
              <q-input v-model="memberForm.workLocation" outlined dense label="Work Location *" :rules="[requiredRule, fieldRules.workLocation]" />
              <q-input v-model="memberForm.onboarding" outlined dense label="Onboarding *" :rules="[requiredRule, fieldRules.onboarding]" />
              <q-input v-model="memberForm.employmentType" outlined dense label="FTE/Contractor *" :rules="[requiredRule, fieldRules.employmentType]" />
              <q-input v-model="memberForm.city" outlined dense label="Current City *" :rules="[requiredRule, fieldRules.city]" />
              <q-input v-model="memberForm.phone" outlined dense label="Phone Number" />
              <q-input v-model="memberForm.department" outlined dense label="Department *" :rules="[requiredRule, fieldRules.department]" />
              <q-input v-model="memberForm.address" outlined dense label="Address" type="textarea" rows="2" />
              <q-input v-model="memberForm.country" outlined dense label="Country" />
              <q-input v-model="memberForm.email" outlined dense type="email" name="member-invite-email" autocomplete="off" data-lpignore="true" label="Email Address *" :rules="[requiredRule, emailRule]" />
              <q-input v-if="!editingMember" v-model="memberForm.password" outlined dense type="password" name="member-invite-password" autocomplete="new-password" data-lpignore="true" label="Temporary Password (optional)" :rules="[passwordRule]" />
            </div>
            <q-checkbox v-if="!editingMember" v-model="memberForm.sendAccountInfo" label="Send Account information with set password link" class="q-mt-sm" />
          </q-form>
        </q-card-section>
        <q-separator />
        <q-card-actions class="dialog-actions"><q-btn flat no-caps label="Cancel" @click="closeMemberDialog" /><q-btn unelevated no-caps :loading="saving" :label="editingMember ? 'Save changes' : 'Add Member'" class="add-member-btn" @click="saveMember" /></q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showDeleteDialog" persistent><q-card class="delete-dialog"><q-card-section class="dialog-heading"><div class="delete-icon"><q-icon name="delete_outline" /></div><div><div class="dialog-title">Delete Member</div><div class="dialog-subtitle">This action cannot be undone.</div></div></q-card-section><q-card-section class="q-pt-none">Are you sure you want to delete <strong>{{ memberToDelete?.name }}</strong>?</q-card-section><q-card-actions align="right"><q-btn flat no-caps label="Cancel" @click="showDeleteDialog = false" /><q-btn unelevated no-caps color="negative" :loading="deleting" label="Delete" @click="deleteMember" /></q-card-actions></q-card></q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar, exportFile } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const search = ref('')
const roleFilter = ref('all')
const statusFilter = ref('all')
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const activatingUser = ref(null)
const members = ref([])
const showMemberDialog = ref(false)
const showDeleteDialog = ref(false)
const editingMember = ref(null)
const memberToDelete = ref(null)
const memberFormRef = ref(null)
const teamLeadOptions = ref([])
const filteredTeamLeads = ref([])
function filterTeamLeads (val, update) {
  if (val === '') { update(() => { filteredTeamLeads.value = teamLeadOptions.value }); return }
  update(() => {
    const needle = val.toLowerCase()
    filteredTeamLeads.value = teamLeadOptions.value.filter(item => item.label.toLowerCase().includes(needle))
  })
}
const emptyMemberForm = () => ({ firstName: '', lastName: '', employeeId: '', client: '', project: '', vlinker: '', teamLead: null, devQa: '', roleDescription: '', workLocation: '', onboarding: '', employmentType: '', city: '', email: '', password: '', sendAccountInfo: true, role: 'user', status: 'Active', phone: '', department: '', address: '', country: '' })
const memberForm = ref(emptyMemberForm())

const columns = [
  { name: 'member', label: 'Member', align: 'left', field: 'name' }, { name: 'department', label: 'Department', align: 'left', field: 'department' }, { name: 'role', label: 'Role', align: 'left', field: 'role' }, { name: 'status', label: 'Status', align: 'left', field: 'status' }, { name: 'joined', label: 'Joined On', align: 'left', field: 'createdAt' }, { name: 'actions', label: 'Actions', align: 'right', field: 'actions' }
]
const roleOptions = [{ label: 'All Roles', value: 'all' }, { label: 'Admin', value: 'admin' }, { label: 'User', value: 'user' }]
const statusOptions = [{ label: 'All Status', value: 'all' }, { label: 'Active', value: 'Active' }, { label: 'Inactive', value: 'Inactive' }]
const dialogStatusOptions = statusOptions.slice(1)
const filteredMembers = computed(() => members.value.filter(member => {
  const term = search.value.trim().toLowerCase()
  return (!term || `${member.name} ${member.email}`.toLowerCase().includes(term)) && (roleFilter.value === 'all' || member.role === roleFilter.value) && (statusFilter.value === 'all' || member.status === statusFilter.value)
}))
const stats = computed(() => [
  { label: 'Total Members', value: members.value.length, hint: 'All team members', icon: 'groups', tone: 'indigo' },
  { label: 'Active Members', value: members.value.filter(m => m.status === 'Active').length, hint: 'Currently active', icon: 'verified_user', tone: 'green' },
  { label: 'Administrators', value: members.value.filter(m => m.role === 'admin').length, hint: 'Have admin access', icon: 'workspace_premium', tone: 'blue' },
  { label: 'Regular Users', value: members.value.filter(m => m.role === 'user').length, hint: 'Standard users', icon: 'person_outline', tone: 'orange' }
])

const requiredRule = value => !!value || 'This field is required'
const emailRule = value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Enter a valid email address'
const passwordRule = value => !value || value.length >= 8 || 'Password must contain at least 8 characters'
const createPatternRule = (pattern, message) => value => pattern.test(value) || message
const fieldRules = {
  firstName: createPatternRule(/^[A-Za-z ]+$/, 'First Name can contain only letters and spaces.'),
  lastName: createPatternRule(/^[A-Za-z ]+$/, 'Last Name can contain only letters and spaces.'),
  employeeId: createPatternRule(/^[A-Za-z0-9]+$/, 'Employee ID can contain only letters and numbers.'),
  client: createPatternRule(/^[A-Za-z ]+$/, 'Client name can contain only letters and spaces.'),
  project: createPatternRule(/^[A-Za-z ]+$/, 'Project  name can contain only letters and spaces.'),
   vlinker: createPatternRule(/^[A-Za-z ]+$/, 'Vlinker name can contain only letters and spaces.'),
   devQa: createPatternRule(/^[A-Za-z ]+$/, 'Dev/QA name can contain only letters and spaces.'),
   department: createPatternRule(/^[A-Za-z ]+$/, 'Department can contain only letters and spaces.'),
  status: createPatternRule(/^[A-Za-z ]+$/, 'Status name can contain only letters and spaces.'),
  roleDescription: createPatternRule(/^[A-Za-z ]+$/, 'Role Description can contain only letters and spaces.'),
  workLocation: createPatternRule(/^[A-Za-z ]+$/, 'Work Location can contain only letters and spaces.'),
  onboarding: createPatternRule(/^[A-Za-z0-9 .,/'"-]+$/, 'Onboarding can contain letters and numbers'),
  employmentType: createPatternRule(/^[A-Za-z ]+$/, 'Employment Type can contain only letters and spaces.'),
  city: createPatternRule(/^[A-Za-z ]+$/, 'City can contain only letters and spaces.')
}
const initials = name => name.split(' ').filter(Boolean).map(part => part[0]).join('').slice(0, 2).toUpperCase()
const roleLabel = role => role === 'admin' ? 'Admin' : 'User'
const formatDate = date => date ? new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(date)) : '—'

async function fetchMembers () { loading.value = true; try { const { data } = await api.get('/v1/users?page=1&page_size=500'); members.value = data.items.map(user => ({ id: user.id, name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email, email: user.email, avatar: '', role: (user.role || 'user').toLowerCase(), department: user.department || '', phone: user.phone_number || '', employeeId: user.employee_id || '', client: user.client || '', project: user.project || '', vlinker: user.vlinker || '', devQa: user.dev_qa || '', roleDescription: user.role_description || '', workLocation: user.work_location || '',       employmentType: user.employment_type || '',
      onboarding: user.onboarding || '',
      city: user.city || '',
      address: user.address || '',
      country: user.country || '',
      status: user.is_active ? 'Active' : 'Inactive',
      createdAt: user.created_at,
      team_lead_id: user.team_lead_id
    })) } catch (error) { console.error('Error fetching members:', error); $q.notify({ type: 'negative', message: 'Unable to load members. Please try again.' }) } finally { loading.value = false } }
async function loadTeamLeads () { try { const { data } = await api.get('/v1/users?page=1&page_size=500'); teamLeadOptions.value = data.items.filter(user => user.id !== editingMember.value?.id).map(user => ({ label: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email, value: user.id }))
filteredTeamLeads.value = teamLeadOptions.value } catch (error) { console.error('Error loading team leads:', error) } }
function openAddDialog () { editingMember.value = null; memberForm.value = emptyMemberForm(); loadTeamLeads(); showMemberDialog.value = true }
function openEditDialog (member) { editingMember.value = member; const [firstName = '', ...last] = member.name.split(' '); memberForm.value = { ...emptyMemberForm(), firstName, lastName: last.join(' '), email: member.email, role: member.role, employeeId: member.employeeId, client: member.client, project: member.project, vlinker: member.vlinker, devQa: member.devQa, department: member.department, status: member.status, phone: member.phone, address: member.address, city: member.city, country: member.country, roleDescription: member.roleDescription, workLocation: member.workLocation, employmentType: member.employmentType, onboarding: member.onboarding, teamLead: member.team_lead_id || null }; loadTeamLeads(); showMemberDialog.value = true }
function closeMemberDialog () { showMemberDialog.value = false; editingMember.value = null }
async function saveMember () { const valid = await memberFormRef.value.validate(); if (!valid) return; const isEditing = !!editingMember.value; saving.value = true; try { const payload = { email: memberForm.value.email, first_name: memberForm.value.firstName, last_name: memberForm.value.lastName, role: memberForm.value.role, is_active: memberForm.value.status === 'Active', phone_number: memberForm.value.phone, employee_id: memberForm.value.employeeId, department: memberForm.value.department, status: memberForm.value.status, address: memberForm.value.address, city: memberForm.value.city, country: memberForm.value.country, team_lead_id: memberForm.value.teamLead, role_description: memberForm.value.roleDescription, work_location: memberForm.value.workLocation, employment_type: memberForm.value.employmentType, client: memberForm.value.client, project: memberForm.value.project, vlinker: memberForm.value.vlinker, dev_qa: memberForm.value.devQa, onboarding: memberForm.value.onboarding }; if (isEditing) { await api.patch(`/v1/users/${editingMember.value.id}`, payload) } else { await api.post('/v1/users', { ...payload, password: memberForm.value.password, send_account_info: memberForm.value.sendAccountInfo }) } await fetchMembers(); closeMemberDialog(); $q.notify({ type: 'positive', message: isEditing ? 'Member updated successfully.' : 'Member added successfully.' }) } catch (error) { console.error('Error saving member:', error); $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to save the member.' }) } finally { saving.value = false } }
function openDeleteDialog (member) { memberToDelete.value = member; showDeleteDialog.value = true }
async function deleteMember () { deleting.value = true; try { await api.delete(`/v1/users/${memberToDelete.value.id}`); await fetchMembers(); showDeleteDialog.value = false; $q.notify({ type: 'positive', message: 'Member deleted successfully.' }) } catch (error) { console.error('Error deleting member:', error); $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to delete the member.' }) } finally { deleting.value = false } }
const handleActivate = async (userId) => {
  activatingUser.value = userId
  try {
    await api.post('/v1/emails/account-setup', {
      user_ids: [userId],
      setup_url_base: `${window.location.origin}/set-password`
    })
    // Refresh members list to update passwordSet status
    await fetchMembers()
    $q.notify({ type: 'positive', message: 'Account activation email sent successfully.' })
  } catch (error) {
    console.error('Error activating user:', error)
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Unable to send activation email.' })
  } finally {
    activatingUser.value = null
  }
}
function exportMembers () { const header = 'Name,Email,Department,Role,Status,Joined On'; const rows = filteredMembers.value.map(member => [member.name, member.email, member.department, roleLabel(member.role), member.status, formatDate(member.createdAt)].map(value => `"${String(value).replaceAll('"', '""')}"`).join(',')); exportFile('members.csv', [header, ...rows].join('\n'), 'text/csv'); }
onMounted(fetchMembers)
</script>

<style scoped>
.members-page { min-height: 100%; background: #f8fafc; color: #1e293b; }
.members-container { max-width: 1680px; margin: 0 auto; padding: 28px 32px 40px; }
.page-header, .header-copy, .stat-content, .filters-row, .member-identity, .pagination-section, .pagination-controls, .dialog-heading { display: flex; align-items: center; }
.page-header { justify-content: space-between; margin-bottom: 28px; }.header-copy { gap: 16px; }.title-icon { display: grid; width: 48px; height: 48px; place-items: center; border-radius: 14px; color: #4f46e5; background: #eef2ff; font-size: 26px; }.header-copy h1 { margin: 0; font-size: 30px; line-height: 1.15; font-weight: 750; letter-spacing: -.6px; }.header-copy p { margin: 5px 0 0; color: #64748b; font-size: 14px; }.add-member-btn { min-height: 42px; padding: 0 17px; border-radius: 10px; color: white; background: #4f46e5; box-shadow: 0 7px 18px rgba(79,70,229,.24); font-weight: 650; }.add-member-btn:hover { background: #4338ca; transform: translateY(-1px); }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; margin-bottom: 22px; }.stat-card, .members-panel { border: 1px solid #e6eaf0; border-radius: 16px; background: #fff; box-shadow: 0 3px 14px rgba(15,23,42,.035); }.stat-content { gap: 17px; padding: 25px; }.stat-icon { display: grid; place-items: center; width: 58px; height: 58px; border-radius: 50%; font-size: 28px; }.stat-icon.indigo { color: #4f46e5; background: #eef2ff; }.stat-icon.green { color: #16a34a; background: #e9f9ee; }.stat-icon.blue { color: #2563eb; background: #ebf3ff; }.stat-icon.orange { color: #f97316; background: #fff3e7; }.stat-label { color: #64748b; font-size: 14px; font-weight: 600; }.stat-value { margin-top: 3px; font-size: 25px; font-weight: 750; }.stat-hint { margin-top: 3px; color: #94a3b8; font-size: 13px; }
.members-panel { overflow: hidden; }.filters-section { padding: 26px 20px 24px; }.filters-row { gap: 16px; }.search-input { width: 395px; }.filter-select { width: 190px; }.export-btn { min-height: 42px; border: 1px solid #dfe5ed; border-radius: 9px; color: #334155; font-weight: 600; }.members-table :deep(th) { height: 54px; color: #334155; font-weight: 700; font-size: 13px; }.members-table :deep(thead tr) { background: #fbfcfe; }.members-table :deep(td) { height: 84px; border-color: #edf0f5; }.member-row { transition: background .18s ease; }.member-row:hover { background: #f8faff; }.member-identity { gap: 13px; min-width: 250px; }.member-avatar { font-weight: 750; }.member-name { color: #172033; font-size: 14px; font-weight: 700; }.member-email { margin-top: 3px; color: #7b8798; font-size: 13px; }.department-cell, .joined-cell { color: #64748b; font-size: 13px; }.role-chip, .status-chip { min-height: 28px; padding: 0 10px; border: 1px solid; border-radius: 7px; font-weight: 650; font-size: 12px; }.admin-chip { color: #ef4444; border-color: #fecaca; background: #fff7f7; }.user-chip { color: #2563eb; border-color: #bfdbfe; background: #f5f9ff; }.active-chip { color: #16a34a; border-color: #bbf7d0; background: #f0fdf4; }.inactive-chip { color: #64748b; border-color: #d7dde5; background: #f8fafc; }.actions-cell { white-space: nowrap; }.pagination-section { justify-content: space-between; min-height: 68px; padding: 0 18px; color: #475569; font-size: 14px; }.pagination-controls { gap: 8px; }.empty-state { padding: 70px 20px; text-align: center; }.empty-icon { display: grid; width: 64px; height: 64px; margin: 0 auto 16px; place-items: center; color: #818cf8; background: #eef2ff; border-radius: 50%; font-size: 32px; }.empty-state h2 { margin: 0; font-size: 18px; }.empty-state p { margin: 7px 0 20px; color: #64748b; }
.member-dialog { display: flex; width: min(1000px, calc(100vw - 48px)); max-height: calc(100dvh - 48px); flex-direction: column; overflow: hidden; border-radius: 18px; box-shadow: 0 24px 60px rgba(15, 23, 42, .22); }.dialog-heading { position: relative; z-index: 1; flex: 0 0 auto; justify-content: space-between; gap: 20px; padding: 20px 28px; background: #fff; }.member-dialog-body { min-height: 0; flex: 1 1 auto; overflow-y: auto; padding: 20px 28px; }.member-form { padding: 0; }.form-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px 16px; }.member-dialog :deep(.q-field__control) { min-height: 46px; height: 46px; border-radius: 9px; }.member-dialog :deep(.q-field--dense .q-field__label) { top: 13px; }.member-dialog :deep(.q-field--float .q-field__label) { top: 7px; }.member-dialog :deep(.q-field__native), .member-dialog :deep(.q-field__input) { min-height: 46px; }.dialog-title { color: #1e293b; font-size: 19px; font-weight: 750; }.dialog-subtitle { margin-top: 3px; color: #64748b; font-size: 13px; }.dialog-actions { z-index: 1; flex: 0 0 auto; justify-content: flex-end; gap: 10px; min-height: 72px; margin: 0; padding: 14px 28px; background: #fff; }.delete-dialog { width: min(440px, calc(100vw - 32px)); border-radius: 16px; }.delete-dialog .dialog-heading { justify-content: left; }.delete-icon { display: grid; width: 42px; height: 42px; place-items: center; color: #ef4444; background: #fef2f2; border-radius: 12px; font-size: 23px; }
@media (max-width: 1100px) { .stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }.filters-row { flex-wrap: wrap; }.filters-row .q-space { display: none; }.export-btn { margin-left: auto; } }
@media (max-width: 900px) { .member-dialog { width: min(720px, calc(100vw - 32px)); }.form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 680px) { .members-container { padding: 20px 16px 100px; }.page-header { align-items: flex-start; gap: 12px; }.header-copy { gap: 11px; }.title-icon { width: 42px; height: 42px; }.header-copy h1 { font-size: 24px; }.header-copy p { max-width: 200px; }.add-member-btn { padding: 0 12px; }.stats-grid { grid-template-columns: 1fr; gap: 12px; }.stat-content { padding: 17px; }.filters-section { padding: 16px; }.filters-row { display: grid; grid-template-columns: 1fr; }.search-input, .filter-select { width: 100%; }.export-btn { margin-left: 0; }.members-table :deep(thead) { display: none; }.members-table :deep(tbody tr) { display: grid; grid-template-columns: 1fr auto; padding: 15px; border-bottom: 1px solid #edf0f5; }.members-table :deep(tbody td) { display: none; height: auto; padding: 0; border: 0; }.members-table :deep(tbody td:first-child), .members-table :deep(tbody td:last-child) { display: table-cell; }.member-identity { min-width: 0; }.pagination-section { align-items: flex-start; gap: 12px; flex-direction: column; padding: 15px 16px; }.pagination-controls { display: none; }.member-dialog { width: calc(100vw - 20px); max-height: calc(100dvh - 20px); }.dialog-heading, .member-dialog-body, .dialog-actions { padding-right: 18px; padding-left: 18px; }.form-grid { grid-template-columns: 1fr; }.dialog-actions { min-height: 66px; } }
</style>
