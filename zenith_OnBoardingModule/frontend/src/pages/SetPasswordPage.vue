<template>
  <q-page class="set-password-page">
    <div class="password-container">
      <!-- Left Side - Image and Quote -->
      <div class="network-section">
        <div class="network-content">
          <div class="image-placeholder">
            <img src="/login-left.svg" alt="Password Setup Illustration" style="width: 100%; max-width: 100%; height: auto;" />
          </div>
          <div class="quote-section">
            <div class="text-h5 text-white text-weight-medium">"Security is not a product, but a process."</div>
            <div class="text-grey-4 q-mt-sm">- Bruce Schneier</div>
          </div>
        </div>
      </div>

      <!-- Right Side - Password Form -->
      <div class="form-section">
        <div class="form-content">
          <div class="flex q-mb-md items-center">
            <q-avatar size="40px">
              <img src="/logo.png" alt="Logo">
            </q-avatar>
            <q-toolbar-title class="text-bold text-primary text-h5">Zenith</q-toolbar-title>
          </div>
          <div class="text-h3 text-weight-bold text-dark q-mb-md">Set Your Password</div>
          <div class="text-subtitle1 text-grey-7 q-mb-xl">Create a secure password for your account</div>

          <q-form @submit="handleSetPassword" class="column">
            <q-input
              v-model="password"
              label="Password"
              :type="showPassword ? 'text' : 'password'"
              outlined
              dense
              color="primary"
              class="q-mb-md"
              :rules="[val => !!val || 'Password is required', val => val.length >= 8 || 'Password must be at least 8 characters']"
              style="border-radius: 6px;"
            >
              <template v-slot:prepend>
                <q-icon name="lock" color="grey-7" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  color="grey-7"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>

            <q-input
              v-model="confirmPassword"
              label="Confirm Password"
              :type="showConfirmPassword ? 'text' : 'password'"
              outlined
              dense
              color="primary"
              class="q-mb-md"
              :rules="[val => !!val || 'Please confirm your password', val => val === password || 'Passwords do not match']"
              style="border-radius: 8px;"
            >
              <template v-slot:prepend>
                <q-icon name="lock" color="grey-7" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showConfirmPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  color="grey-7"
                  @click="showConfirmPassword = !showConfirmPassword"
                />
              </template>
            </q-input>

            <q-btn
              type="submit"
              label="Set Password"
              color="primary"
              class="full-width q-mb-md"
              :loading="loading"
              :disable="!password || !confirmPassword || password !== confirmPassword || password.length < 8"
              unelevated
              size="md"
              style="border-radius: 8px; height: 48px;"
            />

            <div v-if="error" class="text-negative text-center q-mt-md">
              {{ error }}
            </div>
          </q-form>

          <div class="text-center q-mt-lg">
            <div class="text-caption text-grey-6">
              Your password should be at least 8 characters long
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const router = useRouter()
const route = useRoute()
const $q = useQuasar()

const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const error = ref('')
const token = ref('')

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    error.value = 'Invalid or missing token'
  }
})

const handleSetPassword = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await api.post('/v1/auth/set-password', {
      token: token.value,
      password: password.value
    })

    $q.notify({
      type: 'positive',
      message: 'Password set successfully! Please login.',
      position: 'top'
    })

    // Redirect to login page
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to set password. Please try again.'
    $q.notify({
      type: 'negative',
      message: error.value,
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.set-password-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0050D5 0%, #4A90E2 100%);
}

.password-container {
  display: flex;
  width: 100%;
  height: 100vh;
}

.network-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px;
  background: linear-gradient(135deg, #0050D5 0%, #003399 100%);
  position: relative;
  overflow: hidden;
}

.network-content {
  text-align: center;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.image-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.quote-section {
  position: absolute;
  bottom: 20%;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  max-width: 80%;
  padding: 20px;
}

.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #FFFFFF;
}

.form-content {
  width: 100%;
  max-width: 400px;
}

.q-input :deep(.q-field__control) {
  border-radius: 8px;
}

.q-btn {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .password-container {
    flex-direction: column;
  }

  .network-section {
    flex: 0 0 auto;
    min-height: 300px;
    padding: 20px;
  }

  .quote-section {
    bottom: 10%;
    padding: 10px;
  }

  .form-section {
    flex: 1;
    padding: 20px;
  }
}
</style>
