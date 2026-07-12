<template>
  <div class="login-page">
    <div class="login-bg" aria-hidden="true">
      <div class="login-gradient"></div>
      <div class="login-pattern"></div>
    </div>

    <div class="login-card">
      <aside class="login-brand-panel" aria-hidden="true">
        <div class="brand-panel-top">
          <span class="brand-panel-mark">V</span>
          <p class="brand-panel-title">ValuAdis</p>
          <p class="brand-panel-sub">Civic valuation ledger</p>
        </div>
        <div class="brand-panel-parcels">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <p class="brand-panel-note">
          Property and vehicle records, valuation reviews, and audit exports for Ethiopian
          municipal teams.
        </p>
      </aside>

      <div class="login-form-panel">
        <div class="login-header">
          <NuxtLink to="/" class="login-logo">ValuAdis</NuxtLink>
          <p class="login-tagline">Sign in to the valuation workspace</p>
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
  padding: var(--space-4);
  position: relative;
  background: var(--canvas);
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
    linear-gradient(115deg, rgba(238, 234, 221, 0.92) 0%, rgba(246, 243, 234, 0.46) 45%, rgba(35, 92, 67, 0.08) 100%);
}

.login-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(27, 35, 29, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(27, 35, 29, 0.04) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.86), rgba(0, 0, 0, 0.32));
}

.login-card {
  position: relative;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  width: 100%;
  max-width: 52rem;
  overflow: hidden;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  background: rgba(252, 250, 243, 0.96);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(12px);
}

/* --- Brand panel (green-charcoal, cadastral motif) --- */
.login-brand-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-6);
  background:
    linear-gradient(rgba(241, 238, 224, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(241, 238, 224, 0.022) 1px, transparent 1px),
    var(--shell-bg);
  background-size: 40px 40px, 40px 40px, auto;
  color: var(--shell-ink);
  padding: var(--space-6) var(--space-5);
}

.brand-panel-mark {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-bottom: var(--space-4);
  border-radius: var(--radius);
  background: var(--shell-gold);
  color: var(--shell-bg);
  font-family: var(--serif);
  font-size: 28px;
  font-weight: 700;
}

.brand-panel-title {
  margin: 0;
  font-family: var(--serif);
  font-size: 34px;
  font-weight: 600;
  line-height: 1;
}

.brand-panel-sub {
  margin: var(--space-2) 0 0;
  color: var(--shell-muted);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.brand-panel-parcels {
  display: grid;
  grid-template-columns: 1fr 0.7fr;
  gap: var(--space-2);
  width: 70%;
  aspect-ratio: 1.4;
  opacity: 0.9;
}

.brand-panel-parcels span {
  border: 1px solid rgba(211, 169, 76, 0.55);
  background: rgba(211, 169, 76, 0.07);
}

.brand-panel-parcels span:first-child {
  grid-row: span 2;
  border-color: rgba(157, 176, 160, 0.4);
  background: rgba(157, 176, 160, 0.08);
}

.brand-panel-note {
  margin: 0;
  color: var(--shell-muted);
  font-size: 13px;
  line-height: 1.6;
}

/* --- Form panel --- */
.login-form-panel {
  padding: clamp(28px, 5vw, 44px);
}

.login-header {
  margin-bottom: var(--space-6);
  text-align: left;
}

.login-logo {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 2.1rem;
  font-weight: 600;
  letter-spacing: 0;
  text-decoration: none;
  transition: color var(--duration-normal) var(--ease);
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
  gap: var(--space-4);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--ink-soft);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-input {
  width: 100%;
  border: 1px solid var(--line-strong) !important;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  padding: 0.875rem 1rem !important;
  transition: background-color var(--duration-normal) var(--ease), border-color var(--duration-normal) var(--ease), box-shadow var(--duration-normal) var(--ease) !important;
}

.login-input :deep(.p-inputtext) {
  width: 100% !important;
  box-sizing: border-box !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  padding: 0.875rem 1rem !important;
  transition: background-color var(--duration-normal) var(--ease), border-color var(--duration-normal) var(--ease), box-shadow var(--duration-normal) var(--ease) !important;
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
  transition: background-color var(--duration-normal) var(--ease), border-color var(--duration-normal) var(--ease), box-shadow var(--duration-normal) var(--ease) !important;
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
  transition: background-color var(--duration-normal) var(--ease), color var(--duration-normal) var(--ease) !important;
}

.login-input :deep(.p-password .p-password-panel-open:hover) {
  color: var(--green) !important;
  background: var(--green-soft) !important;
}

.login-input:focus,
.login-input :deep(.p-inputtext:focus),
.login-input :deep(.p-password-input:focus) {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(35, 92, 67, 0.16) !important;
  background: var(--surface) !important;
  outline: none !important;
}

.login-input:hover,
.login-input :deep(.p-inputtext:hover),
.login-input :deep(.p-password-input:hover) {
  border-color: var(--green) !important;
}

.login-input::placeholder,
.login-input :deep(.p-inputtext::placeholder),
.login-input :deep(.p-password-input::placeholder) {
  color: var(--muted) !important;
}

.login-error {
  padding: var(--space-3);
  border: 1px solid var(--red);
  border-left: 3px solid var(--red);
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
  min-height: 48px;
  border: 1px solid var(--green) !important;
  border-radius: var(--radius) !important;
  background: var(--green) !important;
  color: var(--surface) !important;
  cursor: pointer;
  font-weight: 700;
  padding: 0.875rem !important;
  transition: background-color var(--duration-normal) var(--ease), transform var(--duration-fast) var(--ease) !important;
}

.login-btn:hover {
  background: var(--green-dark) !important;
}

.login-btn:active {
  transform: scale(0.98);
}

.login-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.demo-login-btn {
  min-height: 44px;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink);
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 700;
  transition: background-color var(--duration-normal) var(--ease), border-color var(--duration-normal) var(--ease), color var(--duration-normal) var(--ease), transform var(--duration-fast) var(--ease);
}

.demo-login-btn:hover {
  border-color: var(--gold);
  color: var(--gold);
}

.demo-login-btn:active {
  transform: scale(0.98);
}

.login-hint {
  margin: 0;
  text-align: center;
  font-size: 0.8rem;
  color: var(--muted);
}

@media (max-width: 760px) {
  .login-card {
    grid-template-columns: 1fr;
    max-width: 28rem;
  }

  .login-brand-panel {
    display: none;
  }
}
</style>
