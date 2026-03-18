<template>
  <div class="enhanced-wizard-container">
    <!-- Enhanced Progress Bar -->
    <div class="progress-section">
      <div class="progress-header">
        <h2 class="progress-title">Property Registration</h2>
        <p class="progress-subtitle">Complete the 7-step process to register your property</p>
      </div>
      
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: `${progressPercentage}%` }"></div>
      </div>
      
      <div class="steps-indicator">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          :class="['step-item', { 
            'active': currentStep === index + 1, 
            'completed': completedSteps.has(index + 1),
            'upcoming': currentStep < index + 1 
          }]"
          @click="goToStep(index + 1)"
        >
          <div class="step-circle">
            <i v-if="completedSteps.has(index + 1)" class="pi pi-check"></i>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-info">
            <div class="step-name">{{ step.name }}</div>
            <div class="step-description">{{ step.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Content Area -->
    <div class="content-area">
      <div class="content-header">
        <div class="step-icon-container">
          <i :class="currentStepData.icon" class="step-icon"></i>
        </div>
        <div class="step-text">
          <h1 class="step-title">{{ currentStepData.title }}</h1>
          <p class="step-subtitle">{{ currentStepData.subtitle }}</p>
        </div>
        
        <div class="step-actions">
          <button class="draft-btn" @click="saveDraft">
            <i class="pi pi-save"></i>
            <span>Save Draft</span>
          </button>
          <button class="help-btn" @click="showHelp">
            <i class="pi pi-question-circle"></i>
          </button>
        </div>
      </div>

      <!-- Step Content -->
      <div class="step-content">
        <slot></slot>
      </div>

      <!-- Enhanced Navigation -->
      <div class="navigation-section">
        <div class="nav-buttons">
          <button 
            v-if="currentStep > 1"
            class="nav-btn secondary"
            @click="previousStep"
          >
            <i class="pi pi-chevron-left"></i>
            <span>Previous</span>
          </button>
          
          <button 
            v-if="currentStep < steps.length"
            class="nav-btn primary"
            :class="{ disabled: !canProceed }"
            @click="nextStep"
            :disabled="!canProceed"
          >
            <span>{{ currentStep === steps.length ? 'Submit' : 'Next' }}</span>
            <i class="pi pi-chevron-right"></i>
          </button>
          
          <button 
            v-if="currentStep === steps.length"
            class="nav-btn success"
            @click="submitProperty"
          >
            <i class="pi pi-check"></i>
            <span>Complete Registration</span>
          </button>
        </div>
        
        <div class="step-info-text">
          <span class="step-counter">Step {{ currentStep }} of {{ steps.length }}</span>
          <span class="progress-text">{{ progressPercentage }}% Complete</span>
        </div>
      </div>
    </div>

    <!-- Help Modal -->
    <div v-if="showHelpModal" class="help-modal-overlay" @click="closeHelp">
      <div class="help-modal" @click.stop>
        <div class="help-header">
          <h3>Step {{ currentStep }} Help</h3>
          <button class="close-btn" @click="closeHelp">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <div class="help-content">
          <p>{{ currentStepData.helpText }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Step {
  name: string
  description: string
  icon: string
  title: string
  subtitle: string
  helpText: string
}

const props = defineProps<{
  currentStep: number
  completedSteps: Set<number>
  canProceed: boolean
}>()

const emit = defineEmits<{
  goToStep: [step: number]
  previousStep: []
  nextStep: []
  saveDraft: []
  submitProperty: []
}>()

const steps: Step[] = [
  {
    name: 'Basic Info',
    description: 'Property details',
    icon: 'pi pi-home',
    title: 'Basic Property Information',
    subtitle: 'Start with the essential details about this property',
    helpText: 'Enter the basic property information including type, address, and administrative details. All fields marked with * are required.'
  },
  {
    name: 'Location',
    description: 'Map location',
    icon: 'pi pi-map',
    title: 'Location & Mapping',
    subtitle: 'Pin the exact location and optionally draw the property boundary',
    helpText: 'Click on the map to set the property location. You can also draw the property boundary by selecting the polygon tool.'
  },
  {
    name: 'Physical',
    description: 'Building details',
    icon: 'pi pi-th-large',
    title: 'Physical Characteristics',
    subtitle: 'Dimensions, structure, and condition details',
    helpText: 'Provide detailed information about the property size, construction materials, and overall condition.'
  },
  {
    name: 'Amenities',
    description: 'Features',
    icon: 'pi pi-list',
    title: 'Amenities & Features',
    subtitle: 'Additional features and facilities',
    helpText: 'List all amenities and special features that add value to the property.'
  },
  {
    name: 'Valuation',
    description: 'Value estimate',
    icon: 'pi pi-dollar',
    title: 'Valuation Details',
    subtitle: 'Market value and assessment information',
    helpText: 'Enter the estimated market value and any professional valuation details.'
  },
  {
    name: 'Ownership',
    description: 'Legal details',
    icon: 'pi pi-user',
    title: 'Ownership Information',
    subtitle: 'Legal ownership and documentation',
    helpText: 'Provide ownership details and upload relevant legal documents.'
  },
  {
    name: 'Review',
    description: 'Final check',
    icon: 'pi pi-eye',
    title: 'Review & Submit',
    subtitle: 'Review all information before submission',
    helpText: 'Carefully review all entered information before submitting the property registration.'
  }
]

const currentStepData = computed(() => steps[props.currentStep - 1])

const progressPercentage = computed(() => {
  return Math.round((props.currentStep / steps.length) * 100)
})

const showHelpModal = ref(false)

const goToStep = (step: number) => {
  if (step <= props.currentStep || props.completedSteps.has(step - 1)) {
    emit('goToStep', step)
  }
}

const previousStep = () => emit('previousStep')
const nextStep = () => emit('nextStep')
const saveDraft = () => emit('saveDraft')
const submitProperty = () => emit('submitProperty')

const showHelp = () => {
  showHelpModal.value = true
}

const closeHelp = () => {
  showHelpModal.value = false
}
</script>

<style scoped>
/* Design System Integration */
.enhanced-wizard-container {
  /* Colors */
  --primary: #078160;
  --primary-dark: #065043;
  --primary-light: #10b981;
  --cyan: #00d4ff;
  --gold: #F59E0B;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --text-light: #e2e8f0;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --border: rgba(7, 129, 96, 0.12);
  --border-light: rgba(0, 0, 0, 0.06);

  /* Typography */
  --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-display: 'Syne', 'Inter', sans-serif;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  /* Spacing */
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Shadows */
  --shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px var(--border);
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.25);

  /* Animations */
  --transition-base: 0.25s ease;
  --transition-slow: 0.35s ease;

  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  font-family: var(--font-family-base);
}

/* Progress Section */
.progress-section {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: var(--spacing-2xl);
  margin: var(--spacing-xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}

.progress-section::after {
  content: '';
  position: absolute;
  top: 0;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at -30% 120%, rgba(0, 212, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.progress-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  position: relative;
  z-index: 1;
}

.progress-title {
  font-size: 2.25rem;
  font-weight: var(--font-weight-extrabold);
  color: var(--text-primary);
  margin: 0 0 0.75rem;
  letter-spacing: -0.5px;
  font-family: var(--font-family-display);
}

.progress-subtitle {
  font-size: 1.05rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
  letter-spacing: 0.2px;
}

.progress-bar-container {
  width: 100%;
  height: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
  margin: var(--spacing-2xl) 0;
  position: relative;
  border: 1px solid var(--border);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
  border-radius: 8px;
  transition: width var(--transition-slow);
  box-shadow: var(--shadow-glow);
}

/* Steps Indicator */
.steps-indicator {
  display: flex;
  justify-content: space-between;
  position: relative;
  gap: var(--spacing-md);
}

.steps-indicator::before {
  content: '';
  position: absolute;
  top: 24px;
  left: 4%;
  right: 4%;
  height: 2px;
  background: var(--border);
  z-index: 0;
  pointer-events: none;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  z-index: 1;
}

.step-item:hover .step-circle {
  transform: scale(1.08);
}

.step-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: 1.25rem;
  margin-bottom: 1rem;
  transition: all var(--transition-base);
  position: relative;
  border: 2px solid transparent;
  background: var(--bg-secondary);
  color: var(--text-muted);
}

/* Upcoming Steps */
.step-item.upcoming .step-circle {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  border-color: var(--border);
}

/* Active Step */
.step-item.active .step-circle {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  box-shadow: 0 0 0 8px rgba(7, 129, 96, 0.12), var(--shadow-glow);
  border-color: var(--primary);
  transform: scale(1.1);
}

/* Completed Steps */
.step-item.completed .step-circle {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  border-color: var(--primary);
}

.step-info {
  text-align: center;
  max-width: 110px;
}

.step-name {
  font-weight: var(--font-weight-semibold);
  font-size: 0.95rem;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
  letter-spacing: 0.2px;
}

.step-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.3;
}

.step-item.upcoming .step-name {
  color: var(--text-muted);
}

.step-item.upcoming .step-description {
  color: #cbd5e1;
}

.step-item.active .step-name,
.step-item.completed .step-name {
  color: var(--primary);
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0 var(--spacing-xl) var(--spacing-xl);
  gap: 0;
}

.content-header {
  background: var(--bg-primary);
  border-radius: 16px 16px 0 0;
  padding: var(--spacing-2xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border);
  border-bottom: none;
  gap: var(--spacing-lg);
}

.step-icon-container {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(7, 129, 96, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.step-icon {
  font-size: 1.75rem;
  color: white;
}

.step-text {
  flex: 1;
}

.step-title {
  font-size: 1.75rem;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 0.375rem;
  letter-spacing: -0.3px;
  font-family: var(--font-family-display);
}

.step-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.step-actions {
  display: flex;
  gap: var(--spacing-md);
  flex-shrink: 0;
}

.draft-btn, .help-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  font-weight: 500;
  font-size: 0.9rem;
}

.draft-btn:hover, .help-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(7, 129, 96, 0.05);
  box-shadow: var(--shadow-sm);
}

.step-content {
  background: var(--bg-primary);
  padding: var(--spacing-2xl);
  flex: 1;
  border: 1px solid var(--border);
  border-top: none;
  border-bottom: none;
}

/* Navigation */
.navigation-section {
  background: var(--bg-primary);
  border-radius: 0 0 16px 16px;
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border);
  border-top: none;
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.95rem 1.75rem;
  border: none;
  border-radius: 8px;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: 0.95rem;
  letter-spacing: 0.3px;
}

.nav-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.nav-btn.secondary:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary);
  color: var(--primary);
}

.nav-btn.primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(7, 129, 96, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-btn.primary:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(7, 129, 96, 0.3), var(--shadow-glow);
}

.nav-btn.primary.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.nav-btn.success {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(7, 129, 96, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-btn.success:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(7, 129, 96, 0.3), var(--shadow-glow);
}

.step-info-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
}

/* Help Modal */
.help-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.help-modal {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: var(--spacing-2xl);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  animation: slideUp var(--transition-slow) ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.help-header h3 {
  font-size: 1.5rem;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  transition: color var(--transition-base);
}

.close-btn:hover {
  color: var(--text-primary);
}

.help-content {
  color: var(--text-secondary);
  line-height: 1.7;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .progress-section {
    margin: var(--spacing-lg);
    padding: var(--spacing-xl);
  }

  .progress-title {
    font-size: 1.75rem;
  }

  .steps-indicator {
    flex-wrap: wrap;
    gap: 1.5rem;
  }

  .step-item {
    flex: 0 0 calc(50% - 0.75rem);
  }

  .content-area {
    margin: 0 var(--spacing-lg) var(--spacing-lg);
  }

  .content-header {
    flex-direction: column;
    text-align: center;
    padding: var(--spacing-xl);
  }

  .step-icon-container {
    margin-right: 0;
  }

  .nav-buttons {
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
  }

  .step-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .step-item {
    flex: 0 0 100%;
  }

  .progress-title {
    font-size: 1.5rem;
  }

  .step-title {
    font-size: 1.25rem;
  }

  .steps-indicator::before {
    left: 2%;
    right: 2%;
  }
}
</style>
