<template>
  <q-page class="permissions-page">
    <div class="permissions-container">
      <div class="page-header q-mb-md">
        <div class="text-h5">Permissions</div>
        <q-btn v-if="activeTab === 'roles'" label="Create Role" color="primary" icon="add" unelevated @click="showCreateRoleDialog = true" />
      </div>
      <q-card class="permissions-card">
        <q-card-section class="q-pa-none">
          <q-tabs v-model="activeTab" align="left" class="tabs" no-caps active-color="primary">
            <q-tab name="members" label="Member View" />
            <q-tab name="roles" label="Roles" />
            <q-tab name="permissions" label="Permission View" />
          </q-tabs>
        </q-card-section>
        <q-card-section class="q-pa-none">
          <!-- Permission View -->
          <q-table
            v-if="activeTab === 'permissions'"
            :rows="permissions"
            :columns="permissionColumns"
            row-key="page"
            flat
            :filter="filter"
            v-model:expanded="expanded"
            :loading="loading"
          >
            <template v-slot:top>
              <q-input
                v-model="filter"
                placeholder="Search permissions..."
                dense
                outlined
                class="full-width"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>

            <template v-slot:body="props">
              <q-tr :props="props">
                <!-- <q-td auto-width>

                </q-td> -->
                <q-td v-for="col in props.cols" :key="col.name" :props="props" :auto-width="col.name === 'expand'">
                  <template v-if="col.name === 'expand'">
                    <q-btn
                      flat
                      round
                      dense
                      :icon="props.expand ? 'expand_less' : 'expand_more'"
                      @click="props.expand = !props.expand"
                    />
                  </template>
                  <template v-if="col.name === 'page'">
                    <div class="text-weight-medium">{{ col.value }}</div>
                  </template>
                  <template v-else-if="col.name === 'totalAssigned'">
                    <q-chip color="primary" text-color="white">
                      <q-avatar icon="person" />
                      {{ col.value }}
                    </q-chip>
                  </template>
                  <template v-else-if="col.name === 'actions'">
                    <q-btn flat round dense icon="more_vert">
                      <q-menu>
                        <q-list style="min-width: 150px">
                          <q-item clickable v-close-popup @click="viewPermissionAssignments(props.row)">
                            <q-item-section avatar>
                              <q-icon name="visibility" />
                            </q-item-section>
                            <q-item-section>View Assignments</q-item-section>
                          </q-item>
                          <q-item clickable v-close-popup @click="editPermission(props.row)">
                            <q-item-section avatar>
                              <q-icon name="edit" />
                            </q-item-section>
                            <q-item-section>Edit</q-item-section>
                          </q-item>
                          <q-item clickable v-close-popup @click="deletePermission(props.row)">
                            <q-item-section avatar>
                              <q-icon name="delete" color="negative" />
                            </q-item-section>
                            <q-item-section class="text-negative">Delete</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </template>
                  <template v-else>
                    {{ col.value }}
                  </template>
                </q-td>
              </q-tr>
              <!-- <q-tr v-show="props.expand" > -->
              <template v-for="action in props.row.actions" :key="action.page">
                <q-tr v-show="props.expand" :props="props">
                  <q-td auto-width :props="props" key="expand"></q-td>
                  <q-td :props="props" key="page">
                    <div class="">
                      <q-badge :color="getActionColor(action.page)" :text-color="getActionTextColor(action.page)" class="q-py-sm q-px-md text-bold text-capitalize">
                        {{ action.page }}
                      </q-badge>
                    </div>
                  </q-td>
                  <q-td :props="props" key="totalAssigned">
                    <q-chip color="grey-7" text-color="white" >
                      <q-avatar icon="person" />
                      {{ action.totalAssigned }}
                    </q-chip>
                  </q-td>
                  <q-td :props="props" key="actions">
                    <q-btn flat round dense icon="more_vert">
                      <q-menu>
                        <q-list style="min-width: 150px">
                          <q-item clickable v-close-popup @click="viewPermissionAssignments(action)">
                            <q-item-section avatar>
                              <q-icon name="visibility" />
                            </q-item-section>
                            <q-item-section>View Assignments</q-item-section>
                          </q-item>
                          <q-item clickable v-close-popup @click="editPermission(action)">
                            <q-item-section avatar>
                              <q-icon name="edit" />
                            </q-item-section>
                            <q-item-section>Edit</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </q-td>
                </q-tr>
              </template>
              <!-- </q-tr> -->
            </template>
          </q-table>

          <!-- Roles View -->
          <div v-if="activeTab === 'roles'">
            <q-table
              :rows="roles"
              :columns="roleColumns"
              row-key="id"
              flat
              :loading="loadingRoles"
              :filter="roleFilter"
            >
              <template v-slot:top>
                <q-input
                  v-model="roleFilter"
                  placeholder="Search roles..."
                  dense
                  outlined
                  class="full-width"
                >
                  <template v-slot:prepend>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </template>
              <template v-slot:body="props">
                <q-tr :props="props">
                  <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <template v-if="col.name === 'permissions'">
                      <q-badge color="primary" :label="props.row.permissions.length" />
                    </template>
                    <template v-else-if="col.name === 'actions'">
                      <q-btn flat round dense icon="edit" class="q-mr-sm" @click="editRole(props.row)" />
                      <q-btn flat round dense icon="delete" color="negative" @click="deleteRole(props.row)" />
                    </template>
                    <template v-else>
                      {{ col.value }}
                    </template>
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </div>

          <!-- Member View -->
          <q-table
            v-if="activeTab === 'members'"
            :rows="members"
            :columns="memberColumns"
            row-key="id"
            flat
            :filter="memberFilter"
            :rows-per-page-options="[10, 20, 50, 0]"
            :loading="loadingMembers"
          >
            <template v-slot:top>
              <q-input
                v-model="memberFilter"
                placeholder="Search members..."
                dense
                outlined
                class="full-width"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>

            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                  <template v-if="col.name === 'totalPermissions'">
                    <q-chip color="primary" text-color="white">
                      <q-avatar icon="vpn_key" />
                      {{ col.value }}
                    </q-chip>
                  </template>
                  <template v-else-if="col.name === 'roles'">
                    <q-chip
                      v-for="role in props.row.roles"
                      :key="role.id"
                      size="sm"
                      color="secondary"
                      text-color="white"
                      class="q-mr-xs"
                    >
                      {{ role.display_name }}
                    </q-chip>
                    <q-chip v-if="props.row.roles.length === 0" size="sm" color="grey-5" text-color="white">
                      No roles
                    </q-chip>
                  </template>
                  <template v-else-if="col.name === 'actions'">
                    <q-btn flat round dense icon="edit" @click="editMemberPermissions(props.row)" />
                  </template>
                  <template v-else>
                    {{ col.value }}
                  </template>
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>

    <!-- Edit Member Permissions Dialog -->
    <q-dialog v-model="showPermissionDialog">
      <q-card style="width: 100%;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Edit Permissions</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-subtitle1 q-mb-md text-weight-medium">{{ selectedMember?.name }}</div>
          <div class="text-caption text-grey q-mb-md">{{ selectedMember?.email }}</div>

          <div class="q-mb-md">
            <div class="text-subtitle2 q-mb-sm">Assign Roles</div>
            <q-select
              v-model="selectedRoles"
              :options="roles"
              option-label="display_name"
              option-value="id"
              label="Select Roles"
              outlined
              dense
              multiple
              use-chips
              emit-value
              map-options
              @update:model-value="updatePermissionsFromRoles"
            />
          </div>

          <q-table
            :rows="permissionMatrix"
            :columns="permissionMatrixColumns"
            row-key="page"
            flat
            bordered
            :loading="loadingPermissions"
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="page" :props="props">
                  <div class="text-weight-medium">{{ props.row.page }}</div>
                </q-td>
                <q-td key="view" :props="props" class="text-center">
                  <q-checkbox
                    v-model="props.row.view"
                    @update:model-value="updatePermission(props.row, 'view', $event)"
                    color="blue"
                  />
                </q-td>
                <q-td key="modify" :props="props" class="text-center">
                  <q-checkbox
                    v-model="props.row.modify"
                    @update:model-value="updatePermission(props.row, 'modify', $event)"
                    color="orange"
                  />
                </q-td>
                <q-td key="add" :props="props" class="text-center">
                  <q-checkbox
                    v-model="props.row.add"
                    @update:model-value="updatePermission(props.row, 'add', $event)"
                    color="green"
                  />
                </q-td>
                <q-td key="delete" :props="props" class="text-center">
                  <q-checkbox
                    v-model="props.row.delete"
                    @update:model-value="updatePermission(props.row, 'delete', $event)"
                    color="red"
                  />
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Save" color="primary" @click="savePermissions" :loading="savingPermissions" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Create Role Dialog -->
    <q-dialog v-model="showCreateRoleDialog" @show="loadAvailablePermissions">
      <q-card style="min-width: 600px; max-width: 800px;">
        <q-card-section class="row items-center ">
          <div class="text-h6">Create New Role</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <q-input
                v-model="newRole.name"
                label="Role Name"
                outlined
                dense hide-bottom-space
                :rules="[val => !!val || 'Role name is required']"
              />
            </div>
            <div class="col-12">
              <q-input
                v-model="newRole.display_name"
                label="Display Name"
                outlined
                dense hide-bottom-space
                :rules="[val => !!val || 'Display name is required']"
              />
            </div>
            <div class="col-12">
              <q-input
                v-model="newRole.description"
                label="Description"
                outlined
                type="textarea"
                rows="2"
                dense hide-bottom-space
              />
            </div>
            <div class="col-12">
              <div class="text-subtitle2 q-mb-sm">Permissions</div>
              <q-table
                :rows="rolePermissionMatrix"
                :columns="permissionSelectionColumns"
                row-key="page"
                flat
                bordered
                dense
                :rows-per-page-options="[0]"
                hide-pagination
                :loading="loadingPermissions"
              >
                <template v-slot:body="props">
                  <q-tr :props="props">
                    <q-td key="page" :props="props">
                      <div class="text-weight-medium">{{ props.row.page }}</div>
                    </q-td>
                    <q-td key="view" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.view"
                        color="blue"
                      />
                    </q-td>
                    <q-td key="modify" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.modify"
                        color="orange"
                      />
                    </q-td>
                    <q-td key="add" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.add"
                        color="green"
                      />
                    </q-td>
                    <q-td key="delete" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.delete"
                        color="red"
                      />
                    </q-td>
                  </q-tr>
                </template>
              </q-table>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Create" color="primary" @click="createRole" :loading="creatingRole" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Role Dialog -->
    <q-dialog v-model="showEditRoleDialog">
      <q-card style="min-width: 600px; max-width: 800px;">
        <q-card-section class="row items-center ">
          <div class="text-h6">Edit Role</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <q-input
                v-model="editingRoleData.display_name"
                label="Display Name"
                outlined
                dense hide-bottom-space
                :rules="[val => !!val || 'Display name is required']"
              />
            </div>
            <div class="col-12">
              <q-input
                v-model="editingRoleData.description"
                label="Description"
                outlined
                type="textarea"
                rows="2"
                dense hide-bottom-space
              />
            </div>
            <div class="col-12">
              <div class="text-subtitle2 q-mb-sm">Permissions</div>
              <q-table
                :rows="rolePermissionMatrix"
                :columns="permissionSelectionColumns"
                row-key="page"
                flat
                bordered
                dense
                :rows-per-page-options="[0]"
                hide-pagination
                :loading="loadingPermissions"
              >
                <template v-slot:body="props">
                  <q-tr :props="props">
                    <q-td key="page" :props="props">
                      <div class="text-weight-medium">{{ props.row.page }}</div>
                    </q-td>
                    <q-td key="view" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.view"
                        color="blue"
                      />
                    </q-td>
                    <q-td key="modify" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.modify"
                        color="orange"
                      />
                    </q-td>
                    <q-td key="add" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.add"
                        color="green"
                      />
                    </q-td>
                    <q-td key="delete" :props="props" class="text-center">
                      <q-checkbox
                        v-model="props.row.delete"
                        color="red"
                      />
                    </q-td>
                  </q-tr>
                </template>
              </q-table>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Save" color="primary" @click="updateRole" :loading="creatingRole" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- View Permission Assignments Dialog -->
    <q-dialog v-model="showPermissionAssignmentsDialog">
      <q-card style="min-width: 500px; max-width: 700px;">
        <q-card-section class="row items-center">
          <div class="text-h6">Permission Assignments</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-subtitle2 q-mb-md">
            {{ selectedPermission?.display_name || selectedPermission?.page }} - {{ selectedPermission?.action }}
          </div>
          <q-table
            :rows="permissionAssignments"
            :columns="[
              { name: 'type', label: 'Type', align: 'left', field: 'type' },
              { name: 'name', label: 'Name', align: 'left', field: 'name' },
              { name: 'assignment_type', label: 'Assignment Type', align: 'left', field: 'assignment_type' }
            ]"
            row-key="id"
            flat
            bordered
            :loading="loadingAssignments"
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="type" :props="props">
                  <q-icon :name="props.row.type === 'user' ? 'person' : 'group'" class="q-mr-sm" />
                  {{ props.row.type }}
                </q-td>
                <q-td key="name" :props="props">
                  {{ props.row.name }}
                  <div v-if="props.row.email" class="text-caption text-grey">{{ props.row.email }}</div>
                </q-td>
                <q-td key="assignment_type" :props="props">
                  <q-badge :color="props.row.assignment_type === 'direct' ? 'primary' : 'secondary'">
                    {{ props.row.assignment_type }}
                  </q-badge>
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Edit Permission Dialog -->
    <q-dialog v-model="showEditPermissionDialog">
      <q-card style="min-width: 400px;">
        <q-card-section class="row items-center">
          <div class="text-h6">Edit Permission</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="editingPermissionData.display_name"
            label="Display Name"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="editingPermissionData.description"
            label="Description"
            outlined
            type="textarea"
            rows="3"
            dense
            class="q-mb-md"
          />
          <q-toggle
            v-model="editingPermissionData.enabled"
            label="Enabled"
            color="primary"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Save" color="primary" @click="savePermissionEdit" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()

const filter = ref('')
const expanded = ref([])
const loading = ref(false)

const activeTab = ref('members')
const memberFilter = ref('')
const roleFilter = ref('')
const loadingRoles = ref(false)
const loadingMembers = ref(false)
const creatingRole = ref(false)
const showPermissionDialog = ref(false)
const showCreateRoleDialog = ref(false)
const loadingPermissions = ref(false)
const savingPermissions = ref(false)
const selectedMember = ref(null)
const permissionMatrix = ref([])
const rolePermissionMatrix = ref([])
const selectedRoles = ref([])
const roleAssignedPermissions = ref(new Set())
const showPermissionAssignmentsDialog = ref(false)
const showEditPermissionDialog = ref(false)
const selectedPermission = ref(null)
const permissionAssignments = ref([])
const loadingAssignments = ref(false)
const editingPermissionData = ref({
  display_name: '',
  description: '',
  enabled: true
})

const permissionColumns = [
  { name: 'expand', label: '', align: 'left' },
  { name: 'page', label: 'Page', align: 'left', field: 'page', sortable: true },
  { name: 'totalAssigned', label: 'Total Assigned', align: 'left', field: 'totalAssigned', sortable: true },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions' }
]

const roleColumns = [
  { name: 'display_name', label: 'Role Name', align: 'left', field: 'display_name', sortable: true },
  { name: 'description', label: 'Description', align: 'left', field: 'description' },
  { name: 'permissions', label: 'Permissions', align: 'left', field: 'permissions' },
  { name: 'actions', label: 'Actions', align: 'right' }
]

const memberColumns = [
  { name: 'name', label: 'Employee Name', align: 'left', field: 'name', sortable: true },
  { name: 'email', label: 'Email', align: 'left', field: 'email', sortable: true },
  { name: 'totalPermissions', label: 'Total Permissions', align: 'center', field: 'totalPermissions', sortable: true },
  { name: 'roles', label: 'Roles', align: 'left', field: 'roles' },
  { name: 'actions', label: 'Actions', align: 'right' }
]

const permissionMatrixColumns = [
  { name: 'page', label: 'Page', align: 'left', field: 'page', sortable: true },
  { name: 'view', label: 'View', align: 'center' },
  { name: 'modify', label: 'Modify', align: 'center' },
  { name: 'add', label: 'Add', align: 'center' },
  { name: 'delete', label: 'Delete', align: 'center' }
]

const permissionSelectionColumns = [
  { name: 'page', label: 'Page', align: 'left', field: 'page', sortable: true },
  { name: 'view', label: 'View', align: 'center' },
  { name: 'modify', label: 'Modify', align: 'center' },
  { name: 'add', label: 'Add', align: 'center' },
  { name: 'delete', label: 'Delete', align: 'center' }
]

const permissions = ref([])
const roles = ref([])
const members = ref([])

const newRole = ref({
  name: '',
  display_name: '',
  description: '',
  permissions: []
})

const editingRoleData = ref({
  id: null,
  name: '',
  display_name: '',
  description: '',
  permissions: []
})

const showEditRoleDialog = ref(false)

const fetchPermissions = async () => {
  loading.value = true
  try {
    const response = await api.get('/v1/permissions/all')
    const data = response.data

    // Group permissions by page
    const pageMap = new Map()

    data.forEach(perm => {
      const pageName = perm.display_name || perm.page
      if (!pageMap.has(pageName)) {
        pageMap.set(pageName, {
          page: pageName,
          totalAssigned: 0,
          actions: []
        })
      }

      const pageData = pageMap.get(pageName)
      pageData.totalAssigned += perm.total_assigned
      pageData.actions.push({
        page: perm.action,
        totalAssigned: perm.total_assigned,
        id: perm.id
      })
    })

    // Convert to array and sort
    permissions.value = Array.from(pageMap.values()).sort((a, b) => a.page.localeCompare(b.page))
  } catch (error) {
    console.error('Error fetching permissions:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPermissions()
  fetchRoles()
  fetchMembers()
})

const getActionColor = (action) => {
  const colors = {
    'view': 'blue-1',
    'modify': 'orange-1',
    'add': 'green-1',
    'delete': 'red-1'
  }
  return colors[action] || 'grey-1'
}

const getActionTextColor = (action) => {
  const colors = {
    'view': 'blue',
    'modify': 'orange',
    'add': 'green',
    'delete': 'red'
  }
  return colors[action] || 'grey'
}

const fetchRoles = async () => {
  loadingRoles.value = true
  try {
    const response = await api.get('/v1/roles')
    roles.value = response.data
  } catch (error) {
    console.error('Error fetching roles:', error)
  } finally {
    loadingRoles.value = false
  }
}

const fetchMembers = async () => {
  loadingMembers.value = true
  try {
    const response = await api.get('/v1/users/permissions-summary')
    members.value = response.data
  } catch (error) {
    console.error('Error fetching members:', error)
  } finally {
    loadingMembers.value = false
  }
}

const createRole = async () => {
  creatingRole.value = true
  try {
    // Convert matrix selections to permission IDs
    const selectedPermissions = []
    rolePermissionMatrix.value.forEach(row => {
      if (row.view && row.permissionIds.view) selectedPermissions.push(row.permissionIds.view)
      if (row.modify && row.permissionIds.modify) selectedPermissions.push(row.permissionIds.modify)
      if (row.add && row.permissionIds.add) selectedPermissions.push(row.permissionIds.add)
      if (row.delete && row.permissionIds.delete) selectedPermissions.push(row.permissionIds.delete)
    })

    const roleData = {
      name: newRole.value.name,
      display_name: newRole.value.display_name,
      description: newRole.value.description,
      permissions: selectedPermissions
    }

    await api.post('/v1/roles', roleData)
    newRole.value = { name: '', display_name: '', description: '', permissions: [] }
    rolePermissionMatrix.value = []
    showCreateRoleDialog.value = false
    await fetchRoles()
    $q.notify({
      type: 'positive',
      message: 'Role created successfully',
      position: 'top',
      timeout: 2000
    })
  } catch (error) {
    console.error('Error creating role:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to create role',
      caption: error.response?.data?.detail || 'An error occurred',
      position: 'top',
      timeout: 3000
    })
  } finally {
    creatingRole.value = false
  }
}

const loadAvailablePermissions = async () => {
  loadingPermissions.value = true
  try {
    const response = await api.get('/v1/permissions/all')
    const allPerms = response.data

    // Build permission matrix grouped by page
    const pageMap = new Map()

    allPerms.forEach(perm => {
      const pageName = perm.display_name || perm.page
      if (!pageMap.has(pageName)) {
        pageMap.set(pageName, {
          page: pageName,
          view: false,
          modify: false,
          add: false,
          delete: false,
          permissionIds: {
            view: null,
            modify: null,
            add: null,
            delete: null
          }
        })
      }

      const pageData = pageMap.get(pageName)
      const action = perm.action
      if (action === 'view') {
        pageData.permissionIds.view = perm.id
      } else if (action === 'modify') {
        pageData.permissionIds.modify = perm.id
      } else if (action === 'add') {
        pageData.permissionIds.add = perm.id
      } else if (action === 'delete') {
        pageData.permissionIds.delete = perm.id
      }
    })

    rolePermissionMatrix.value = Array.from(pageMap.values()).sort((a, b) => a.page.localeCompare(b.page))
  } catch (error) {
    console.error('Error loading permissions:', error)
  } finally {
    loadingPermissions.value = false
  }
}

const editRole = async (role) => {
  if (role.is_system) {
    $q.notify({
      type: 'warning',
      message: 'Cannot edit system roles',
      caption: 'System roles are protected and cannot be modified through the interface.',
      position: 'top',
      timeout: 3000
    })
    return
  }

  editingRoleData.value = {
    id: role.id,
    name: role.name,
    display_name: role.display_name,
    description: role.description,
    permissions: role.permissions.map(p => p.id)
  }

  // Build permission matrix for editing
  await loadAvailablePermissions()

  // Set current permissions in matrix
  rolePermissionMatrix.value.forEach(row => {
    Object.keys(row.permissionIds).forEach(action => {
      const permId = row.permissionIds[action]
      if (permId && editingRoleData.value.permissions.includes(permId)) {
        row[action] = true
      } else {
        row[action] = false
      }
    })
  })

  showEditRoleDialog.value = true
}

const updateRole = async () => {
  creatingRole.value = true
  try {
    // Convert matrix selections to permission IDs
    const selectedPermissions = []
    rolePermissionMatrix.value.forEach(row => {
      if (row.view && row.permissionIds.view) selectedPermissions.push(row.permissionIds.view)
      if (row.modify && row.permissionIds.modify) selectedPermissions.push(row.permissionIds.modify)
      if (row.add && row.permissionIds.add) selectedPermissions.push(row.permissionIds.add)
      if (row.delete && row.permissionIds.delete) selectedPermissions.push(row.permissionIds.delete)
    })

    const roleData = {
      display_name: editingRoleData.value.display_name,
      description: editingRoleData.value.description,
      permissions: selectedPermissions
    }

    await api.put(`/v1/roles/${editingRoleData.value.id}`, roleData)
    showEditRoleDialog.value = false
    await fetchRoles()
    $q.notify({
      type: 'positive',
      message: 'Role updated successfully',
      position: 'top',
      timeout: 2000
    })
  } catch (error) {
    console.error('Error updating role:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update role',
      caption: error.response?.data?.detail || 'An error occurred',
      position: 'top',
      timeout: 3000
    })
  } finally {
    creatingRole.value = false
  }
}

const deleteRole = async (role) => {
  // Check if it's a system role
  if (role.is_system) {
    $q.notify({
      type: 'warning',
      message: 'Cannot delete system roles',
      caption: 'System roles are protected and cannot be deleted through the interface.',
      position: 'top',
      timeout: 3000
    })
    return
  }

  try {
    await api.delete(`/v1/roles/${role.id}`)
    await fetchRoles()
    $q.notify({
      type: 'positive',
      message: 'Role deleted successfully',
      position: 'top',
      timeout: 2000
    })
  } catch (error) {
    console.error('Error deleting role:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to delete role',
      caption: error.response?.data?.detail || 'An error occurred',
      position: 'top',
      timeout: 3000
    })
  }
}

const viewPermissionAssignments = async (permission) => {
  selectedPermission.value = permission
  showPermissionAssignmentsDialog.value = true
  loadingAssignments.value = true

  try {
    const response = await api.get(`/v1/permissions/${permission.id}/assignments`)
    permissionAssignments.value = response.data
  } catch (error) {
    console.error('Error loading permission assignments:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load assignments',
      caption: error.response?.data?.detail || 'An error occurred',
      position: 'top',
      timeout: 3000
    })
  } finally {
    loadingAssignments.value = false
  }
}

const editPermission = (permission) => {
  selectedPermission.value = permission
  editingPermissionData.value = {
    display_name: permission.display_name || permission.page,
    description: permission.description || '',
    enabled: permission.enabled !== false
  }
  showEditPermissionDialog.value = true
}

const savePermissionEdit = async () => {
  try {
    await api.put(`/v1/permissions/${selectedPermission.value.id}`, editingPermissionData.value)
    showEditPermissionDialog.value = false
    await fetchPermissions()
    $q.notify({
      type: 'positive',
      message: 'Permission updated successfully',
      position: 'top',
      timeout: 2000
    })
  } catch (error) {
    console.error('Error updating permission:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update permission',
      caption: error.response?.data?.detail || 'An error occurred',
      position: 'top',
      timeout: 3000
    })
  }
}

const deletePermission = (permission) => {
  $q.dialog({
    title: 'Delete Permission',
    message: `Are you sure you want to delete the permission "${permission.display_name || permission.page} - ${permission.action}"?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await api.delete(`/v1/permissions/${permission.id}`)
      await fetchPermissions()
      $q.notify({
        type: 'positive',
        message: 'Permission deleted successfully',
        position: 'top',
        timeout: 2000
      })
    } catch (error) {
      console.error('Error deleting permission:', error)
      $q.notify({
        type: 'negative',
        message: 'Failed to delete permission',
        caption: error.response?.data?.detail || 'An error occurred',
        position: 'top',
        timeout: 3000
      })
    }
  })
}

const editMemberPermissions = async (member) => {
  selectedMember.value = member
  showPermissionDialog.value = true
  loadingPermissions.value = true

  try {
    // Fetch all available permissions
    const response = await api.get('/v1/permissions/all')
    const allPerms = response.data

    // Build permission matrix
    const pageMap = new Map()

    // Initialize matrix with all pages and actions
    allPerms.forEach(perm => {
      const pageName = perm.display_name || perm.page
      if (!pageMap.has(pageName)) {
        pageMap.set(pageName, {
          page: pageName,
          view: false,
          modify: false,
          add: false,
          delete: false,
          permissionIds: {
            view: null,
            modify: null,
            add: null,
            delete: null
          }
        })
      }

      const pageData = pageMap.get(pageName)
      const action = perm.action
      if (action === 'view') {
        pageData.permissionIds.view = perm.id
      } else if (action === 'modify') {
        pageData.permissionIds.modify = perm.id
      } else if (action === 'add') {
        pageData.permissionIds.add = perm.id
      } else if (action === 'delete') {
        pageData.permissionIds.delete = perm.id
      }
    })

    // Mark permissions that the user already has
    member.allPermissions.forEach(userPerm => {
      const pageName = userPerm.display_name || userPerm.page
      const action = userPerm.action

      if (pageMap.has(pageName)) {
        const pageData = pageMap.get(pageName)
        if (action === 'view') pageData.view = true
        if (action === 'modify') pageData.modify = true
        if (action === 'add') pageData.add = true
        if (action === 'delete') pageData.delete = true
      }
    })

    permissionMatrix.value = Array.from(pageMap.values()).sort((a, b) => a.page.localeCompare(b.page))

    // Set selected roles from member's current roles
    selectedRoles.value = member.roles ? member.roles.map(r => r.id) : []

    // Initialize role-assigned permissions tracking
    roleAssignedPermissions.value = new Set()
    if (member.roles && member.roles.length > 0) {
      const rolePermissionsPromises = member.roles.map(r => api.get(`/v1/roles/${r.id}`))
      const roleResponses = await Promise.all(rolePermissionsPromises)
      roleResponses.forEach(response => {
        const rolePermissions = response.data.permissions || []
        rolePermissions.forEach(perm => {
          const permId = typeof perm === 'string' ? perm : perm.id
          if (permId) roleAssignedPermissions.value.add(permId)
        })
      })
    }
  } catch (error) {
    console.error('Error loading permissions:', error)
  } finally {
    loadingPermissions.value = false
  }
}

const updatePermission = (row, action, value) => {
  // Track the change locally
  row[action] = value
}

const updatePermissionsFromRoles = async (selectedRoleIds) => {
  try {
    // Get all permissions from selected roles (union)
    const newRolePermissions = new Set()
    if (selectedRoleIds && selectedRoleIds.length > 0) {
      const rolePermissionsPromises = selectedRoleIds.map(roleId =>
        api.get(`/v1/roles/${roleId}`)
      )

      const roleResponses = await Promise.all(rolePermissionsPromises)

      // Collect all permission IDs from all selected roles
      roleResponses.forEach(response => {
        const rolePermissions = response.data.permissions || []
        rolePermissions.forEach(perm => {
          // Handle both string and object permission formats
          const permId = typeof perm === 'string' ? perm : perm.id
          if (permId) newRolePermissions.add(permId)
        })
      })
    }

    // Remove permissions that were from roles but are no longer in selected roles
    roleAssignedPermissions.value.forEach(permId => {
      if (!newRolePermissions.has(permId)) {
        // Find and remove this permission from matrix
        permissionMatrix.value.forEach(row => {
          Object.keys(row.permissionIds).forEach(action => {
            if (row.permissionIds[action] === permId) {
              row[action] = false
            }
          })
        })
      }
    })

    // Add new permissions from selected roles
    newRolePermissions.forEach(permId => {
      permissionMatrix.value.forEach(row => {
        Object.keys(row.permissionIds).forEach(action => {
          if (row.permissionIds[action] === permId) {
            row[action] = true
          }
        })
      })
    })

    // Update tracked role permissions
    roleAssignedPermissions.value = newRolePermissions
  } catch (error) {
    console.error('Error updating permissions from roles:', error)
  }
}

const savePermissions = async () => {
  savingPermissions.value = true

  try {
    const userId = selectedMember.value.id

    // Save roles first
    const currentRoles = selectedMember.value.roles || []
    const currentRoleIds = currentRoles.map(r => r.id)
    const newRoleIds = selectedRoles.value || []

    // Remove roles that are no longer selected
    for (const roleId of currentRoleIds) {
      if (!newRoleIds.includes(roleId)) {
        await api.delete(`/v1/users/roles/${userId}/${roleId}`)
      }
    }

    // Add newly selected roles
    for (const roleId of newRoleIds) {
      if (!currentRoleIds.includes(roleId)) {
        await api.post('/v1/users/roles', {
          user_id: userId,
          role_id: roleId
        })
      }
    }

    // Get current user permissions
    const currentResponse = await api.get(`/v1/users/${userId}/permissions`)
    const currentPerms = currentResponse.data || []

    // Calculate permissions to add and remove
    const toAdd = []
    const toRemove = []

    permissionMatrix.value.forEach(row => {
      ['view', 'modify', 'add', 'delete'].forEach(action => {
        const permId = row.permissionIds[action]
        if (!permId) return

        const hasPermission = currentPerms.some(p => p.permission_id === permId)
        const shouldHave = row[action]

        if (shouldHave && !hasPermission) {
          toAdd.push(permId)
        } else if (!shouldHave && hasPermission) {
          toRemove.push(permId)
        }
      })
    })

    // Add new permissions
    for (const permId of toAdd) {
      await api.post('/v1/users/permissions', {
        user_id: userId,
        permission_id: permId
      })
    }

    // Remove permissions
    for (const permId of toRemove) {
      await api.delete(`/v1/users/permissions/${userId}/${permId}`)
    }

    // Refresh member data
    await fetchMembers()
    showPermissionDialog.value = false
    $q.notify({
      type: 'positive',
      message: 'Permissions and roles saved successfully',
      position: 'top',
      timeout: 2000
    })
  } catch (error) {
    console.error('Error saving permissions:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to save permissions',
      caption: error.response?.data?.detail || 'An error occurred',
      position: 'top',
      timeout: 3000
    })
  } finally {
    savingPermissions.value = false
  }
}
</script>

<style scoped>
.permissions-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.permissions-container {
  padding: 16px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.permissions-card {
  box-shadow: none;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

</style>

