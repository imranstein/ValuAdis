<template>
  <div class="wizard-indicator">
    <!-- Progress bar -->
    <div class="progress-track">
      <div
        class="progress-fill"
        :style="{ width: progressPercent + '%' }"
      />
    </div>

    <!-- Step bubbles -->
    <div class="steps-row">
      <div
        v-for="step in steps"
        :key="step.number"
        class="step-item"
        :class="{
          'is-active': current === step.number,
          'is-completed': completed.has(step.number) && current !== step.number,
          'is-clickable': completed.has(step.number),
        }"
        @click="completed.has(step.number) ? emit('go-to', step.number) : null"
      >
        <div class="bubble">
          <i v-if="completed.has(step.number) && current !== step.number" class="pi pi-check text-sm" />
          <span v-else>{{ step.number }}</span>
        </div>
        <span class="step-label">{{ step.label }}</span>
      </div>
    </div>

    <!-- Completion text -->
    <p class="progress-text">
      <span class="font-semibold text-emerald-600">{{ progressPercent }}%</span> complete
      <span v-if="progressPercent === 100" class="text-emerald-600 ml-1">— Ready to submit!</span>
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  completed: Set<number>
  progressPercent: number
}>()

const emit = defineEmits<{
  (e: 'go-to', step: number): void
}>()

const steps = [
  { number: 1, label: 'Basic Info' },
  { number: 2, label: 'Location' },
  { number: 3, label: 'Physical' },
  { number: 4, label: 'Amenities' },
  { number: 5, label: 'Valuation' },
  { number: 6, label: 'Ownership' },
  { number: 7, label: 'Review' },
]
</script>

<style scoped>
.wizard-indicator {
  background: white;
  border-radius: 12px;
  padding: 1.25rem 1.5rem 1rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.progress-track {
  height: 4px;
  background: #e2e8f0;
  border-radius: 9999px;
  margin-bottom: 1.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #059669, #10b981);
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.steps-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.25rem;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  flex: 1;
  min-width: 0;
}

.is-clickable {
  cursor: pointer;
}

.bubble {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  background: #e2e8f0;
  color: #64748b;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e2e8f0;
  transition: all 0.25s ease;
}

.is-active .bubble {
  background: #059669;
  color: white;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.2);
}

.is-completed .bubble {
  background: #10b981;
  color: white;
  box-shadow: 0 0 0 2px #10b981;
}

.step-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: #94a3b8;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 72px;
}

.is-active .step-label {
  color: #059669;
  font-weight: 700;
}

.is-completed .step-label {
  color: #10b981;
}

.progress-text {
  text-align: center;
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 0.75rem;
  margin-bottom: 0;
}

@media (max-width: 640px) {
  .step-label {
    display: none;
  }
  .bubble {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
}
</style>
