<template>
  <div class="error-page">
    <div class="error-card">
      <p class="error-code">{{ error?.statusCode || 500 }}</p>
      <h1 class="error-title">{{ errorTitle }}</h1>
      <p class="error-message">{{ errorMessage }}</p>
      <button type="button" class="error-btn" @click="handleClearError">
        Back to home
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NuxtError } from '#app'

const props = defineProps<{
  error?: NuxtError
}>()

const errorTitle = computed(() =>
  props.error?.statusCode === 404 ? 'Page not found' : 'Something went wrong'
)

const errorMessage = computed(() =>
  props.error?.statusCode === 404
    ? 'The page you requested does not exist or has been moved.'
    : 'An unexpected error occurred. Return to the dashboard and try again.'
)

function handleClearError() {
  clearError({ redirect: '/' })
}
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--canvas);
  font-family: var(--sans);
}

.error-card {
  max-width: 420px;
  width: 100%;
  padding: 48px 40px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  text-align: center;
}

.error-code {
  margin: 0 0 12px;
  font-family: var(--mono);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--green);
}

.error-title {
  margin: 0 0 8px;
  font-family: var(--display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--ink);
}

.error-message {
  margin: 0 0 28px;
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--muted);
}

.error-btn {
  padding: 10px 24px;
  background: var(--green);
  color: var(--shell-ink);
  border: none;
  border-radius: var(--radius);
  font-family: var(--sans);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--duration-normal) var(--ease);
}

.error-btn:hover {
  background: var(--green-dark);
}
</style>
