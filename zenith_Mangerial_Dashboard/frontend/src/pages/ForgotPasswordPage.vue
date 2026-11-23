<template>
  <q-page class="forgot-password-page">
    <div class="password-container">
      <!-- Left Side - Image and Quote -->
      <div class="network-section">
        <div class="network-content">
          <div class="image-placeholder">
            <img src="/login-left.svg" alt="Forgot Password Illustration" style="width: 100%; max-width: 100%; height: auto;" />
          </div>
          <div class="quote-section">
            <div class="text-h5 text-white text-weight-medium">"Security starts with knowing your password is safe."</div>
            <div class="text-grey-4 q-mt-sm">- Unknown</div>
          </div>
        </div>
      </div>

      <!-- Right Side - Forgot Password Form -->
      <div class="form-section">
        <div class="form-content">
          <div class="flex q-mb-md items-center">
            <q-avatar size="40px">
              <img src="/logo.png" alt="Logo">
            </q-avatar>
            <q-toolbar-title class="text-bold text-primary text-h5">Zenith</q-toolbar-title>
          </div>
          <div class="text-h3 text-weight-bold text-dark q-mb-md">Forgot Password?</div>
          <div class="text-subtitle1 text-grey-7 q-mb-xl">Enter your email address and we'll send you a link to reset your password</div>

          <q-form @submit="handleForgotPassword" class="column">
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

            <q-btn
              type="submit"
              label="Send Reset Link"
              color="primary"
              class="full-width q-mb-md"
              :loading="loading"
              unelevated
              size="md"
              style="border-radius: 8px; height: 48px;"
            />

            <div class="text-center">
              <q-btn flat no-caps color="primary" label="Back to Sign In" dense @click="goToLogin" />
            </div>
          </q-form>

          <div class="text-center q-mt-lg">
            <div class="text-caption text-grey-6">
              We'll send a password reset link to your registered email address
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
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const router = useRouter()
const $q = useQuasar()

const email = ref('')
const loading = ref(false)

const isValidEmail = (val) => {
  if (!val) return true
  const emailPattern = /^(?=[a-zA-Z0-9@._%+-]{6,254}$)[a-zA-Z0-9._%+-]{1,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,8}[a-zA-Z]{2,63}$/
  return emailPattern.test(val)
}

const handleForgotPassword = async () => {
  loading.value = true

  try {
    await api.post('/v1/auth/forgot-password', {
      email: email.value
    })

    $q.notify({
      type: 'positive',
      message: 'Password reset link sent! Please check your email.',
      position: 'top'
    })

    router.push('/login')
  } catch (error) {
    console.error('Forgot password error:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to send reset link. Please try again.',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.forgot-password-page {
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
  position: relative;
  padding: 40px;
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
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  max-width: 80%;
  padding: 20px;
  z-index: 2;
  background: linear-gradient(135deg, rgba(0, 80, 213, 0.6) 0%, rgba(0, 51, 153, 0.8) 100%);
  border-radius: 12px;
  backdrop-filter: blur(4px);
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
