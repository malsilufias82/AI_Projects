<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="text-h4">My Profile</h1>
      <p class="text-subtitle1 text-grey-6">Manage your personal and work information</p>
    </div>

    <div class="profile-container">
      <q-card class="profile-card">
        <div class="profile-content">
          <!-- Left Sidebar Navigation -->
          <div class="sidebar">
            <q-list class="q-py-xs">
              <q-item
                clickable
                :class="{ 'active-section': activeSection === 'personal' }"
                @click="activeSection = 'personal'"
              >
                <q-item-section avatar>
                  <q-icon name="person" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Personal Details</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                clickable
                :class="{ 'active-section': activeSection === 'work' }"
                @click="activeSection = 'work'"
              >
                <q-item-section avatar>
                  <q-icon name="work" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Work Info</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                clickable
                :class="{ 'active-section': activeSection === 'project' }"
                @click="activeSection = 'project'"
              >
                <q-item-section avatar>
                  <q-icon name="folder" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Project Details</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Right Content Area -->
          <div class="content-area">
            <!-- Personal Details Section -->
            <div v-if="activeSection === 'personal'" class="section-content">
              <div class="section-header">
                <h2 class="text-h6">Personal Details</h2>
              </div>

              <q-form @submit="saveProfile" class="q-gutter-md">
                <div class="row q-col-gutter-md q-pl-md q-pt-xs">
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="profile.first_name"
                      label="First Name"
                      outlined
                      hide-bottom-space
                      :rules="[val => val && val.length > 0 || 'First name is required']"
                    />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="profile.last_name"
                      label="Last Name"
                      outlined
                      hide-bottom-space
                      :rules="[val => val && val.length > 0 || 'Last name is required']"
                    />
                  </div>
                </div>

                <q-input
                  v-model="profile.email"
                  label="Email"
                  outlined
                  readonly
                  disable
                />

                <q-input
                  v-model="profile.phone_number"
                  label="Phone Number"
                  outlined
                  type="tel"
                />

                <q-btn
                  type="submit"
                  label="Save Changes"
                  color="primary"
                  :loading="loading"
                  class="q-mt-md"
                />
              </q-form>
            </div>

            <!-- Work Info Section -->
            <div v-if="activeSection === 'work'" class="section-content">
              <div class="section-header">
                <h2 class="text-h6">Work Information</h2>
              </div>

              <div class="q-gutter-md q-pt-xs">
                <q-input
                  v-model="profile.team_lead"
                  label="Team Lead"
                  outlined
                  readonly
                  disable
                />

                <q-input
                  v-model="profile.position"
                  label="Position"
                  outlined
                  readonly
                  disable
                />
              </div>
            </div>

            <!-- Project Details Section -->
            <div v-if="activeSection === 'project'" class="section-content">
              <div class="section-header">
                <h2 class="text-h6">Project Details</h2>
              </div>

              <div class="q-gutter-md q-pt-xs">
                <q-input
                  v-model="profile.pillar"
                  label="Pillar"
                  outlined
                  readonly
                  disable
                />

                <q-input
                  v-model="profile.client"
                  label="Client"
                  outlined
                  readonly
                  disable
                />

                <q-input
                  v-model="profile.project"
                  label="Project"
                  outlined
                  readonly
                  disable
                />
              </div>
            </div>
          </div>
        </div>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { Notify } from 'quasar'

const activeSection = ref('personal')

const profile = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  team_lead: '',
  position: '',
  pillar: '',
  client: '',
  project: ''
})

const loading = ref(false)

const fetchProfile = async () => {
  try {
    const response = await api.get('/v1/users/profile')
    profile.value = response.data
  } catch (error) {
    console.error('Failed to fetch profile:', error)
    Notify.create({
      type: 'negative',
      message: 'Failed to load profile data'
    })
  }
}

const saveProfile = async () => {
  loading.value = true
  try {
    await api.put('/v1/users/profile', {
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      phone_number: profile.value.phone_number
    })
    Notify.create({
      type: 'positive',
      message: 'Profile updated successfully'
    })
  } catch (error) {
    console.error('Failed to update profile:', error)
    Notify.create({
      type: 'negative',
      message: 'Failed to update profile'
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-weight: 600;
}

.page-header p {
  margin: 0;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  /* border-right: 2px solid #e0e0e0; */
  overflow: hidden;
}

.profile-content {
  display: flex;
  min-height: 500px;
}

.sidebar {
  width: 280px;
  border-right: 1px solid #e0e0e0;
  background: #fafafa;
}

.sidebar .q-list {
  padding: 8px 0;
}

.sidebar .q-item {
  padding: 12px 24px;
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar .q-item.active-section {
  background: #e3f2fd;
  color: #1976d2;
}

.sidebar .q-item:hover:not(.active-section) {
  background: #e0e0e0;
}

.content-area {
  flex: 1;
  padding: 32px;
  background: white;
}

.section-content {
  max-width: 600px;
}

.section-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
}

.section-header h2 {
  margin: 0;
  font-weight: 600;
  color: #333;
}
</style>
