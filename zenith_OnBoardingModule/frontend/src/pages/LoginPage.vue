<template>
  <q-page class="login-page">
    <div class="login-container">
      <!-- Left Side - Image and Quote -->
      <div class="network-section">
        <div class="network-content">
          <div class="image-placeholder">
            <img src="/login-left.svg" alt="Login Illustration" style="width: 100%; max-width: 100%; height: auto;" />
          </div>
          <div class="quote-section">
            <div class="text-h5 text-white text-weight-medium">"Innovation distinguishes between a leader and a follower."</div>
            <div class="text-grey-4 q-mt-sm">- Steve Jobs</div>
          </div>
        </div>
      </div>

      <!-- Right Side - Login Form -->
      <div class="form-section">
        <div class="form-content">
          <div class="flex q-mb-md items-center">
            <q-avatar size="40px">
              <img src="/logo.png" alt="Logo">
            </q-avatar>
            <q-toolbar-title class="text-bold text-primary text-h5">Zenith</q-toolbar-title>
          </div>
          <div class="text-h3 text-weight-bold text-dark q-mb-md">Sign In</div>
          <div class="text-subtitle1 text-grey-7 q-mb-xl">Welcome back! Please sign in to continue</div>

          <q-form @submit="handleLogin" class="column">
            <q-input
              v-model="email"
              label="Email"
              type="email"
              outlined
              dense
              color="primary"
              class="q-mb-md"
              :rules="[val => !!val || 'Email is required', val => isValidEmail(val) || 'Invalid email']"
              style="border-radius: 6px;"
            >
              <template v-slot:prepend>
                <q-icon name="email" color="grey-7" />
              </template>
            </q-input>

            <q-input
              v-model="password"
              label="Password"
              :type="showPassword ? 'text' : 'password'"
              outlined
              dense
              color="primary"
              class="q-mb-md"
              :rules="[val => !!val || 'Password is required']"
              style="border-radius: 8px;"
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

            <q-btn
              type="submit"
              label="Sign In"
              color="primary"
              class="full-width q-mb-md"
              :loading="loading"
              unelevated
              size="md"
              style="border-radius: 8px; height: 48px;"
            />

            <div class="text-center">
              <q-btn flat no-caps color="primary" label="Forgot password?" dense />
            </div>
          </q-form>

          <div class="text-center q-mt-lg">
            <div class="text-caption text-grey-6">
              By signing in, you agree to our Terms of Service and Privacy Policy
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/auth-store'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const router = useRouter()
const auth = useAuthStore()
const $q = useQuasar()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)

const isValidEmail = (val) => {
  const emailPattern = /^(?=[a-zA-Z0-9@._%+-]{6,254}$)[a-zA-Z0-9._%+-]{1,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,8}[a-zA-Z]{2,63}$/
  return emailPattern.test(val) || true
}

const handleLogin = async () => {
  loading.value = true

  try {
    const response = await api.post('/v1/auth/login', {
      email: email.value,
      password: password.value
    })

    const { access_token, refresh_token } = response.data

    // Store both tokens in auth store
    auth.setToken(access_token)
    auth.setRefreshToken(refresh_token)

    // Get user info using the token
    const userResponse = await api.get('/v1/users/me')
    const userData = userResponse.data

    // Get user permissions
    const permissionsResponse = await api.get('/v1/auth/permissions')
    const permissions = permissionsResponse.data

    // Update auth store with user data including permissions
    auth.login({
      user: userData,
      token: access_token,
      refreshToken: refresh_token,
      role: userData.role,
      permissions: permissions,
      organization: null
    })

    $q.notify({
      type: 'positive',
      message: 'Login successful!',
      position: 'top'
    })

    router.push('/daily-status')
  } catch (error) {
    console.error('Login error:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Login failed. Please check your credentials.',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0050D5 0%, #4A90E2 100%);
}

.login-container {
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
  .login-container {
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
