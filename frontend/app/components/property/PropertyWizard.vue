<template>
  <EnhancedWizardUI
    :current-step="store.currentStep"
    :completed-steps="store.completedSteps"
    :can-proceed="canProceedToNext"
    @go-to-step="store.goToStep"
    @previous-step="previousStep"
    @next-step="nextStep"
    @save-draft="handleSaveDraft"
    @submit-property="handleSubmit"
  >
    <!-- Draft restored banner -->
    <div v-if="draftRestored" class="draft-banner">
      <i class="pi pi-history text-amber-600" />
      <span>Draft restored from last session.</span>
      <Button label="Discard Draft" severity="warning" text size="small" @click="discardDraft" />
    </div>

    <!-- Active step with slide transition -->
    <div class="wizard-main">
      <Transition name="slide-fade" mode="out-in">
        <component :is="currentStepComponent" :key="store.currentStep" class="step-component" />
      </Transition>
    </div>
  </EnhancedWizardUI>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePropertyWizardStore } from '~/stores/propertyWizard'
import EnhancedWizardUI from './wizard/EnhancedWizardUI.vue'
import WizardStep1BasicInfo from './wizard/WizardStep1BasicInfo.vue'
import WizardStep2Location from './wizard/WizardStep2Location.vue'
import WizardStep3Physical from './wizard/WizardStep3Physical.vue'
import WizardStep4Amenities from './wizard/WizardStep4Amenities.vue'
import WizardStep5Valuation from './wizard/WizardStep5Valuation.vue'
import WizardStep6Ownership from './wizard/WizardStep6Ownership.vue'
import WizardStep7Documents from './wizard/WizardStep7Documents.vue'
import WizardReviewSummary from './wizard/WizardReviewSummary.vue'

const store = usePropertyWizardStore()
const router = useRouter()
const draftRestored = ref(false)
let autoSaveInterval: ReturnType<typeof setInterval> | null = null

const stepComponents = {
  1: WizardStep1BasicInfo,
  2: WizardStep2Location,
  3: WizardStep3Physical,
  4: WizardStep4Amenities,
  5: WizardStep5Valuation,
  6: WizardStep6Ownership,
  7: WizardStep7Documents,
  8: WizardReviewSummary, // Step 7 in indicator = docs; review is the final action in step 7
}

// We use 7 steps in the indicator; the review summary replaces step 7 at step === 7
// Actually let's use step 7 = Documents and step 7 = Review via a flag
// Simpler: show WizardReviewSummary when currentStep > 7
const currentStepComponent = computed(() => {
  const s = store.currentStep
  if (s >= 8) return WizardReviewSummary
  return stepComponents[s as keyof typeof stepComponents] || WizardStep1BasicInfo
})

onMounted(() => {
  // Only restore a draft when we are NOT in edit mode.
  // In edit mode the page already called store.loadFromProperty(), and
  // loading a stale draft on top of that would silently overwrite the
  // data fetched from the server.
  const restored = !store.editPropertyId && store.loadDraft()
  if (restored) draftRestored.value = true

  // Auto-save every 30 seconds
  autoSaveInterval = setInterval(() => {
    store.saveDraft()
  }, 30_000)
})

onUnmounted(() => {
  if (autoSaveInterval) clearInterval(autoSaveInterval)
})

function discardDraft() {
  store.clearWizard()
  draftRestored.value = false
}

function handleCancel() {
  router.push('/properties')
}

function handleSaveDraft() {
  store.saveDraft()
}

function previousStep() {
  store.previousStep()
}

function nextStep() {
  store.nextStep()
}

function handleSubmit() {
  store.submitProperty()
}

const canProceedToNext = computed(() => {
  return !store.stepErrors[store.currentStep] || Object.keys(store.stepErrors[store.currentStep] || {}).length === 0
})
</script>

<style scoped>
.property-wizard {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 860px;
  margin: 0 auto;
}

.draft-banner {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 1rem;
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #92400e;
}

.wizard-body {
  display: flex;
  gap: 1.5rem;
}

.wizard-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.step-component {
  border-radius: 12px;
  box-shadow: 0 1px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

/* Navigation bar */
.wizard-nav {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 0;
  flex-wrap: wrap;
}

.step-counter {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}

.nav-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

/* Slide transition */
.slide-fade-enter-active {
  transition: all 0.25s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
  .wizard-nav {
    padding: 0.75rem 0;
  }
  .step-counter {
    display: none;
  }
}
</style>
