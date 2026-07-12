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

      <form ref="formEl" @submit.prevent="handleLogin" class="login-form">
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

        <div v-if="errorMessage" class="login-error" role="alert" aria-live="assertive">
          <p>{{ errorMessage }}</p>
        </div>

        <button
          type="submit"
          class="login-btn"
          :disabled="authStore.loading"
        >
          {{ authStore.loading ? 'Signing in...' : 'Sign In' }}
        </button>

        <button
          v-if="canUseDemoLogin"
          type="button"
          class="demo-login-btn"
          :disabled="authStore.loading"
          @click="loginAsDemoUser"
        >
          Use demo account
        </button>

        <p v-if="canUseDemoLogin" class="login-hint">Local demo access is available in development mode.</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'guest', layout: 'landing' })

const authStore = useAuthStore()
const route = useRoute()
const config = useRuntimeConfig()

const isLocalApi = String(config.public.apiBaseUrl).includes('127.0.0.1') || String(config.public.apiBaseUrl).includes('localhost')
const demoCredentials = {
  email: String(config.public.demoLoginEmail || ''),
  password: String(config.public.demoLoginPassword || '')
}
const canUseDemoLogin = Boolean(demoCredentials.email && demoCredentials.password) && (import.meta.dev || isLocalApi)

const formEl = ref<HTMLFormElement | null>(null)
const credentials = ref({ email: '', password: '' })
const errorMessage = ref<string | null>(null)

onMounted(() => {
  const hashDemo = process.client && window.location.hash === '#demo'
  if ((route.query.demo === '1' || hashDemo) && canUseDemoLogin) {
    loginAsDemoUser()
  }
})

async function handleLogin() {
  errorMessage.value = null
  syncCredentialsFromForm()
  
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
    await navigateTo(getRedirectPath(), { replace: true })
  } catch (err: any) {
    errorMessage.value =
      err?.message ||
    authStore.error ||
      'Login failed. Please check your credentials.'
  }
}

function getRedirectPath() {
  const redirect = Array.isArray(route.query.redirect) ? route.query.redirect[0] : route.query.redirect
  if (!redirect || !redirect.startsWith('/') || redirect.startsWith('//')) return '/dashboard'
  return redirect
}

async function loginAsDemoUser() {
  credentials.value = { ...demoCredentials }
  await handleLogin()
}

function syncCredentialsFromForm() {
  const form = formEl.value
  if (!form) return

  const email = form.querySelector<HTMLInputElement>('input[type="email"]')?.value
  const password = form.querySelector<HTMLInputElement>('input[type="password"]')?.value

  credentials.value = {
    email: email || credentials.value.email,
    password: password || credentials.value.password
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
  background:
    linear-gradient(rgba(23, 26, 23, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 26, 23, 0.025) 1px, transparent 1px),
    var(--canvas);
  background-size: 56px 56px, 56px 56px, auto;
  color: var(--ink);
}

.login-bg {
  position: absolute;
  inset: 0;
}

.login-gradient {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(115deg, rgba(236, 239, 233, 0.92) 0%, rgba(246, 247, 244, 0.46) 45%, rgba(31, 107, 79, 0.08) 100%);
}

.login-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(23, 26, 23, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 26, 23, 0.04) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.86), rgba(0, 0, 0, 0.32));
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 28rem;
  padding: 2.5rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(252, 252, 250, 0.94);
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
}

.login-header {
  margin-bottom: 2rem;
  text-align: left;
}

.login-logo {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--ink);
  font-family: var(--display);
  font-size: 2rem;
  font-weight: 760;
  letter-spacing: 0;
  text-decoration: none;
  transition: color 160ms var(--ease);
}

.login-logo:hover {
  color: var(--green);
}

.login-tagline {
  margin: 0;
  color: var(--muted);
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--ink-soft);
  font-size: 0.875rem;
  font-weight: 800;
}

.login-input {
  width: 100%;
  border: 1px solid var(--line-strong) !important;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  padding: 0.875rem 1rem !important;
  transition: background-color 160ms var(--ease), border-color 160ms var(--ease), box-shadow 160ms var(--ease) !important;
}

.login-input :deep(.p-inputtext) {
  width: 100% !important;
  box-sizing: border-box !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  padding: 0.875rem 1rem !important;
  transition: background-color 160ms var(--ease), border-color 160ms var(--ease), box-shadow 160ms var(--ease) !important;
}

.login-input :deep(.p-password) {
  width: 100% !important;
  position: relative !important;
}

.login-input :deep(.p-password-input) {
  width: 100% !important;
  box-sizing: border-box !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  padding: 0.875rem 1rem !important;
  outline: none !important;
  transition: background-color 160ms var(--ease), border-color 160ms var(--ease), box-shadow 160ms var(--ease) !important;
}

.login-input :deep(.p-password .p-inputtext) {
  background: transparent !important;
  border: none !important;
  color: var(--ink) !important;
  border-radius: 0 !important;
  padding: 0 !important;
  width: calc(100% - 40px) !important;
  box-shadow: none !important;
  outline: none !important;
  margin: 0 !important;
}

.login-input :deep(.p-password .p-password-panel-open) {
  position: absolute !important;
  right: 12px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  background: transparent !important;
  border: none !important;
  color: var(--muted) !important;
  padding: 4px !important;
  cursor: pointer !important;
  border-radius: var(--radius) !important;
  transition: background-color 160ms var(--ease), color 160ms var(--ease) !important;
}

.login-input :deep(.p-password .p-password-panel-open:hover) {
  color: var(--green) !important;
  background: var(--green-soft) !important;
}

.login-input:focus,
.login-input :deep(.p-inputtext:focus),
.login-input :deep(.p-password-input:focus) {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(31, 107, 79, 0.14) !important;
  background: var(--surface) !important;
  outline: none !important;
}

.demo-login-btn {
  min-height: 42px;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink);
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 800;
  transition: background-color 160ms var(--ease), border-color 160ms var(--ease), color 160ms var(--ease), transform 120ms var(--ease);
}

.demo-login-btn:hover {
  border-color: var(--green);
  color: var(--green);
}

.demo-login-btn:active {
  transform: scale(0.98);
}

.login-input:hover,
.login-input :deep(.p-inputtext:hover),
.login-input :deep(.p-password-input:hover) {
  border-color: var(--green) !important;
}

.login-input::placeholder {
  color: var(--muted) !important;
}

.login-input :deep(.p-inputtext::placeholder) {
  color: var(--muted) !important;
}

.login-input :deep(.p-password-input::placeholder) {
  color: var(--muted) !important;
}

.login-input:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(31, 107, 79, 0.14) !important;
  background: var(--surface) !important;
}

.login-input :deep(.p-inputtext:focus) {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(31, 107, 79, 0.14) !important;
  background: var(--surface) !important;
}

.login-input :deep(.p-password-input:focus) {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(31, 107, 79, 0.14) !important;
  background: var(--surface) !important;
}

.login-input:hover {
  border-color: var(--green) !important;
}

.login-input :deep(.p-inputtext:hover) {
  border-color: var(--green) !important;
}

.login-input :deep(.p-password-input:hover) {
  border-color: var(--green) !important;
}

.login-error {
  padding: 0.75rem;
  border: 1px solid var(--red);
  border-radius: var(--radius);
  background: var(--red-soft);
}

.login-error p {
  margin: 0;
  color: var(--red);
  font-size: 0.875rem;
}

.login-btn {
  width: 100%;
  border: 1px solid var(--green) !important;
  border-radius: var(--radius) !important;
  background: var(--green) !important;
  color: var(--surface) !important;
  font-weight: 850;
  padding: 0.875rem !important;
  transition: background-color 160ms var(--ease), transform 120ms var(--ease) !important;
}

.login-btn:hover {
  background: var(--green-dark) !important;
}

.login-btn:active {
  transform: scale(0.98);
}

.login-hint {
  text-align: center;
  font-size: 0.8rem;
  color: var(--muted);
}
</style>
