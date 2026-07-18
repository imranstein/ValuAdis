<template>
  <main class="signup-page">
    <nav class="rent-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="rent-brand">
        <span class="rent-mark" aria-hidden="true">V</span>
        <span>ValuAdis Rentals</span>
      </NuxtLink>
      <div class="rent-nav-links">
        <NuxtLink to="/rent">Listings</NuxtLink>
        <NuxtLink to="/login" class="rent-login">Workspace sign in</NuxtLink>
      </div>
    </nav>

    <section class="signup-panel">
      <p class="rent-kicker">Citizen registration</p>
      <h1>Register for the rental registry.</h1>
      <p class="signup-lede">
        Renters browse and apply to published listings. Property owners list their properties —
        a rental officer verifies each owner account before any listing can publish.
      </p>

      <form class="signup-form" @submit.prevent="submit">
        <div class="field-row">
          <label class="field">
            <span>Account type</span>
            <select v-model="form.account_type" class="signup-input">
              <option value="renter">Renter</option>
              <option value="property_owner">Property owner</option>
            </select>
          </label>
          <label class="field">
            <span>Full name</span>
            <input v-model="form.full_name" type="text" required minlength="3" class="signup-input" autocomplete="name" />
          </label>
        </div>

        <div class="field-row">
          <label class="field">
            <span>Email</span>
            <input v-model="form.email" type="email" required class="signup-input" autocomplete="email" />
          </label>
          <label class="field">
            <span>Phone (+2519… or 09…)</span>
            <input v-model="form.phone" type="tel" required class="signup-input" autocomplete="tel" />
          </label>
        </div>

        <div class="field-row">
          <label class="field">
            <span>Fayda ID number</span>
            <input v-model="form.fayda_id_number" type="text" required minlength="6" class="signup-input" />
          </label>
          <label class="field">
            <span>Municipality</span>
            <input v-model="form.municipality" type="text" required minlength="2" class="signup-input" />
          </label>
        </div>

        <label class="field">
          <span>Password (8+ chars, uppercase, digit, special)</span>
          <input v-model="form.password" type="password" required minlength="8" class="signup-input" autocomplete="new-password" />
        </label>

        <p v-if="errorMessage" class="signup-error" role="alert">{{ errorMessage }}</p>

        <div v-if="ownerPending" class="verification-pending" role="status">
          <strong>Registration complete — verification pending.</strong>
          <span>
            Your owner account must be verified by a rental officer before your listings can
            publish. You can draft listings now; publication unlocks after verification.
          </span>
          <NuxtLink to="/rentals/my-listings" class="rent-btn-primary">Go to my listings</NuxtLink>
        </div>

        <button v-else class="rent-btn-primary" type="submit" :disabled="submitting">
          {{ submitting ? 'Registering…' : 'Register' }}
        </button>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import rentalService from '~/services/rentalService'
import { setAccessToken, setRefreshTokenValue } from '~/utils/authToken'

definePageMeta({ layout: 'landing' })

const router = useRouter()
const submitting = ref(false)
const errorMessage = ref('')
const ownerPending = ref(false)

const form = reactive({
  account_type: 'renter' as 'renter' | 'property_owner',
  full_name: '',
  email: '',
  phone: '',
  fayda_id_number: '',
  municipality: 'Addis Ababa',
  password: '',
})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    const result = await rentalService.citizenSignup({ ...form })
    setAccessToken(result.access_token)
    if (result.refresh_token) setRefreshTokenValue(result.refresh_token)
    const authStore = useAuthStore()
    authStore.activeSession = true
    await authStore.fetchCurrentUser().catch(() => {})

    if (form.account_type === 'property_owner') {
      // Honest state: owner accounts start unverified; no fake progress.
      ownerPending.value = true
    } else {
      router.push('/rent')
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Registration failed.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.signup-page {
  min-height: 100vh;
  background: var(--canvas);
  color: var(--ink);
}

.rent-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  height: 72px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  padding: 0 clamp(18px, 5vw, 64px);
}

.rent-brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 600;
  text-decoration: none;
}

.rent-mark {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-size: 18px;
}

.rent-nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-5);
}

.rent-nav-links a {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
}

.rent-login {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 var(--space-4);
}

.signup-panel {
  max-width: 720px;
  margin: 0 auto;
  padding: clamp(32px, 6vw, 72px) clamp(18px, 5vw, 32px);
}

.rent-kicker {
  margin: 0 0 var(--space-4);
  color: var(--gold);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.signup-panel h1 {
  margin: 0;
  font-family: var(--serif);
  font-size: clamp(32px, 4.6vw, 48px);
  font-weight: 600;
  line-height: 1.06;
}

.signup-lede {
  margin: var(--space-4) 0 var(--space-6);
  color: var(--ink-soft);
  line-height: 1.6;
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.field span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.signup-input {
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink);
  padding: 0 12px;
}

.signup-input:focus {
  outline: none;
  border-color: var(--green);
}

.signup-error {
  margin: 0;
  color: var(--red, #9d3a28);
  font-weight: 600;
}

.verification-pending {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  border: 1px solid var(--line-strong);
  border-left: 3px solid var(--gold-bright);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  padding: var(--space-4);
}

.verification-pending strong {
  color: var(--ink);
}

.rent-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: flex-start;
  min-height: 44px;
  border: 0;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-weight: 700;
  padding: 0 var(--space-5);
  cursor: pointer;
  text-decoration: none;
}

.rent-btn-primary:hover {
  background: var(--green-dark);
}

.rent-btn-primary:disabled {
  opacity: 0.6;
  cursor: default;
}

@media (max-width: 640px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
