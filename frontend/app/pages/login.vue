<template>
  <div class="min-h-screen flex items-center justify-center" style="background: linear-gradient(135deg, #078160 0%, #1E3A8A 100%); padding: 1rem;">
    <Card style="width: 100%; max-width: 28rem;">
      <template #header>
        <div style="text-align: center; padding: 1.5rem;">
          <h1 style="font-size: 1.875rem; font-weight: bold; color: #078160; margin-bottom: 0.5rem;">ValuAdis</h1>
          <p style="color: #6b7280;">Ethiopian Property Valuation Platform</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleLogin" style="display: flex; flex-direction: column; gap: 1rem;">
          <div>
            <label for="email" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.25rem;">
              Email
            </label>
            <InputText
              id="email"
              v-model="credentials.email"
              type="email"
              style="width: 100%;"
              required
              autocomplete="email"
            />
          </div>

          <div>
            <label for="password" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.25rem;">
              Password
            </label>
            <Password
              id="password"
              v-model="credentials.password"
              style="width: 100%;"
              :feedback="false"
              toggleMask
              required
              autocomplete="current-password"
            />
          </div>

          <div v-if="errorMessage" style="padding: 0.75rem; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 0.5rem;">
            <p style="font-size: 0.875rem; color: #dc2626;">{{ errorMessage }}</p>
          </div>

          <Button
            type="submit"
            label="Login"
            style="width: 100%; background-color: #078160; border-color: #078160;"
            :loading="authStore.loading"
            :disabled="authStore.loading"
          />

          <div style="text-align: center; font-size: 0.875rem; color: #6b7280;">
            Test credentials: admin@valuadis.com / password123
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'guest' })

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({ email: '', password: '' })
const errorMessage = ref<string | null>(null)

async function handleLogin() {
  errorMessage.value = null
  try {
    await authStore.login(credentials.value)
    router.push('/')
  } catch (err: any) {
    errorMessage.value =
      err?.message ||
      authStore.error ||
      'Login failed. Please check your credentials.'
  }
}
</script>
