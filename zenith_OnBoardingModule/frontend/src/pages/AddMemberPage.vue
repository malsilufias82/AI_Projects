<template>
  <q-page class="add-member-page">
    <div class="add-member-container">
      <div class="page-header q-mb-md">
        <q-btn flat round dense icon="arrow_back" @click="goBack" />
        <div class="text-h5">{{ isEditMode ? 'Edit Member' : 'Add New Member' }}</div>
        <div></div>
      </div>

      <q-card class="form-card">
        <q-card-section>
          <q-form @submit="handleSubmit" class="q-gutter-md">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-input
                  v-model="form.firstName"
                  label="First Name *"
                  outlined
                  :rules="[val => !!val || 'First name is required']"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  v-model="form.lastName"
                  label="Last Name *"
                  outlined
                  :rules="[val => !!val || 'Last name is required']"
                />
              </div>
            </div>

            <q-input
              v-model="form.email"
              label="Email *"
              outlined
              type="email"
              :rules="[val => !!val || 'Email is required', val => isValidEmail(val) || 'Invalid email']"
            />

            <q-input
              v-model="form.phone"
              label="Phone Number"
              outlined
              type="tel"
            />

            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-select
                  v-model="form.role"
                  label="Role *"
                  outlined
                  :options="roleOptions"
                  :rules="[val => !!val || 'Role is required']"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-select
                  v-model="form.department"
                  label="Department *"
                  outlined
                  :options="departmentOptions"
                  :rules="[val => !!val || 'Department is required']"
                />
              </div>
            </div>

            <q-select
              v-model="form.status"
              label="Status *"
              outlined
              :options="statusOptions"
              :rules="[val => !!val || 'Status is required']"
            />

            <q-input
              v-model="form.address"
              label="Address"
              outlined
              type="textarea"
              rows="3"
            />

            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-input
                  v-model="form.city"
                  label="City"
                  outlined
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  v-model="form.country"
                  label="Country"
                  outlined
                />
              </div>
            </div>

            <div class="row q-mt-md">
              <div class="col-12">
                <q-btn label="Cancel" color="grey" outline class="q-mr-md" @click="goBack" />
                <q-btn :label="isEditMode ? 'Update Member' : 'Add Member'" color="primary" type="submit" unelevated />
              </div>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isEditMode = computed(() => !!route.params.id)

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  role: '',
  department: '',
  status: 'Active',
  address: '',
  city: '',
  country: ''
})

const roleOptions = [
  'Admin',
  'Manager',
  'Developer',
  'Designer',
  'HR Manager',
  'Marketing Lead',
  'QA Engineer',
  'Product Manager'
]

const departmentOptions = [
  'Engineering',
  'Marketing',
  'Design',
  'Human Resources',
  'Product',
  'Sales',
  'Finance',
  'Operations'
]

const statusOptions = ['Active', 'Inactive']

const isValidEmail = (email) => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailPattern.test(email)
}

onMounted(() => {
  if (isEditMode.value) {
    // TODO: Fetch member data by ID and populate form
    console.log('Edit mode for member ID:', route.params.id)
    // Example: loadMemberData(route.params.id)
  }
})

const handleSubmit = () => {
  if (isEditMode.value) {
    console.log('Update member:', route.params.id, form.value)
    // TODO: Implement actual member update logic
  } else {
    console.log('Add member:', form.value)
    // TODO: Implement actual member creation logic
  }
  router.push('/members')
}

const goBack = () => {
  router.push('/members')
}
</script>

<style scoped>
.add-member-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.add-member-container {
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-card {
  box-shadow: none;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}
</style>
