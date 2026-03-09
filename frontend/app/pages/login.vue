<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="login-gradient"></div>
      <div class="login-pattern"></div>
    </div>
    <div class="login-card">
      <div class="login-header">
        <NuxtLink to="/" class="login-logo">ValuAdis</NuxtLink>
        <p class="login-tagline">Ethiopian Property Valuation Platform</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <InputText
            id="email"
            v-model="credentials.email"
            type="email"
            class="login-input"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <Password
            id="password"
            v-model="credentials.password"
            class="login-input"
            :feedback="false"
            toggleMask
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="errorMessage" class="login-error">
          <p>{{ errorMessage }}</p>
        </div>

        <Button
          type="submit"
          label="Sign In"
          class="login-btn"
          :loading="authStore.loading"
          :disabled="authStore.loading"
        />

        <p v-if="isDev" class="login-hint">Test: admin@valuadis.com / Admin123!</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'guest', layout: 'landing' })

const router = useRouter()
const authStore = useAuthStore()

const isDev = import.meta.dev

const credentials = ref({ email: '', password: '' })
const errorMessage = ref<string | null>(null)

async function handleLogin() {
  errorMessage.value = null
  
  // Client-side validation
  if (!credentials.value.email || !credentials.value.password) {
    errorMessage.value = 'Please fill in all fields'
    return
  }
  
  if (!credentials.value.email.includes('@')) {
    errorMessage.value = 'Please enter a valid email address'
    return
  }
  
  try {
    await authStore.login(credentials.value)
    router.push('/dashboard')
  } catch (err: any) {
    errorMessage.value =
      err?.message ||
      authStore.error ||
      'Login failed. Please check your credentials.'
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  background: #0a0a0a;
}

.login-bg {
  position: absolute;
  inset: 0;
}

.login-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% 0%, rgba(26, 26, 46, 0.9) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(212, 175, 55, 0.06) 0%, transparent 50%);
}

.login-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(212, 175, 55, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(212, 175, 55, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 28rem;
  padding: 2.5rem;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-logo {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: 2rem;
  font-weight: 600;
  color: #d4af37;
  text-decoration: none;
  letter-spacing: 0.08em;
  display: block;
  margin-bottom: 0.5rem;
}

.login-logo:hover {
  color: #e8c547;
}

.login-tagline {
  font-size: 0.9rem;
  color: rgba(245, 240, 232, 0.7);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(245, 240, 232, 0.9);
  margin-bottom: 0.5rem;
}

.login-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(212, 175, 55, 0.4) !important;
  color: #fffff5 !important;
  border-radius: 0.5rem !important;
  padding: 0.875rem 1rem !important;
  transition: all 0.3s ease !important;
}

/* PrimeVue components - base styling */
.login-input :deep(.p-inputtext) {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(212, 175, 55, 0.4) !important;
  color: #fffff5 !important;
  border-radius: 0.5rem !important;
  padding: 0.875rem 1rem !important;
  transition: all 0.3s ease !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Password component container - make it look like email field */
.login-input :deep(.p-password) {
  width: 100% !important;
  position: relative !important;
}

/* Password input field - match email field exactly */
.login-input :deep(.p-password-input) {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(212, 175, 55, 0.4) !important;
  color: #fffff5 !important;
  border-radius: 0.5rem !important;
  padding: 0.875rem 1rem !important;
  transition: all 0.3s ease !important;
  width: 100% !important;
  box-sizing: border-box !important;
  outline: none !important;
}

/* Remove nested input styling completely */
.login-input :deep(.p-password .p-inputtext) {
  background: transparent !important;
  border: none !important;
  color: #fffff5 !important;
  border-radius: 0 !important;
  padding: 0 !important;
  width: calc(100% - 40px) !important;
  box-shadow: none !important;
  outline: none !important;
  margin: 0 !important;
}

/* Password toggle button - style to match theme */
.login-input :deep(.p-password .p-password-panel-open) {
  position: absolute !important;
  right: 12px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  background: transparent !important;
  border: none !important;
  color: rgba(212, 175, 55, 0.7) !important;
  padding: 4px !important;
  cursor: pointer !important;
  border-radius: 4px !important;
  transition: all 0.3s ease !important;
}

.login-input :deep(.p-password .p-password-panel-open:hover) {
  color: #d4af37 !important;
  background: rgba(212, 175, 55, 0.1) !important;
}

/* Focus states - make both fields identical */
.login-input:focus,
.login-input :deep(.p-inputtext:focus),
.login-input :deep(.p-password-input:focus) {
  border-color: #d4af37 !important;
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.15) !important;
  background: rgba(255, 255, 255, 0.12) !important;
  outline: none !important;
}

/* Hover states - make both fields identical */
.login-input:hover,
.login-input :deep(.p-inputtext:hover),
.login-input :deep(.p-password-input:hover) {
  border-color: rgba(212, 175, 55, 0.6) !important;
}

.login-input::placeholder {
  color: rgba(245, 240, 232, 0.5) !important;
}

.login-input :deep(.p-inputtext::placeholder) {
  color: rgba(245, 240, 232, 0.5) !important;
}

.login-input :deep(.p-password-input::placeholder) {
  color: rgba(245, 240, 232, 0.5) !important;
}

.login-input:focus {
  border-color: #d4af37 !important;
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.15) !important;
  background: rgba(255, 255, 255, 0.12) !important;
}

.login-input :deep(.p-inputtext:focus) {
  border-color: #d4af37 !important;
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.15) !important;
  background: rgba(255, 255, 255, 0.12) !important;
}

.login-input :deep(.p-password-input:focus) {
  border-color: #d4af37 !important;
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.15) !important;
  background: rgba(255, 255, 255, 0.12) !important;
}

.login-input:hover {
  border-color: rgba(212, 175, 55, 0.6) !important;
}

.login-input :deep(.p-inputtext:hover) {
  border-color: rgba(212, 175, 55, 0.6) !important;
}

.login-input :deep(.p-password-input:hover) {
  border-color: rgba(212, 175, 55, 0.6) !important;
}

.login-error {
  padding: 0.75rem;
  background: rgba(220, 38, 38, 0.15);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 0.5rem;
}

.login-error p {
  font-size: 0.875rem;
  color: #fca5a5;
}

.login-btn {
  width: 100%;
  background: linear-gradient(135deg, #d4af37 0%, #c9a227 100%) !important;
  border: none !important;
  color: #0a0a0a !important;
  font-weight: 600;
  padding: 0.875rem !important;
}

.login-btn:hover {
  background: linear-gradient(135deg, #e8c547 0%, #d4af37 100%) !important;
}

.login-hint {
  text-align: center;
  font-size: 0.8rem;
  color: rgba(245, 240, 232, 0.5);
}
</style>
