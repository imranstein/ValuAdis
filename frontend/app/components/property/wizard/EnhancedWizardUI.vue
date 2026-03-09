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
.enhanced-wizard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Progress Section */
.progress-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.progress-header {
  text-align: center;
  margin-bottom: 2rem;
}

.progress-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem;
}

.progress-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

.progress-bar-container {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 2rem 0;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #059669 0%, #10b981 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.steps-indicator {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.step-item:hover {
  transform: translateY(-2px);
}

.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.step-item.upcoming .step-circle {
  background: #e2e8f0;
  color: #64748b;
}

.step-item.active .step-circle {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

.step-item.completed .step-circle {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
}

.step-info {
  text-align: center;
  max-width: 100px;
}

.step-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.step-description {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.2;
}

.step-item.upcoming .step-name {
  color: #94a3b8;
}

.step-item.upcoming .step-description {
  color: #cbd5e1;
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0 2rem 2rem;
}

.content-header {
  background: white;
  border-radius: 16px 16px 0 0;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.step-icon-container {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.5rem;
}

.step-icon {
  font-size: 1.5rem;
  color: white;
}

.step-text {
  flex: 1;
}

.step-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem;
}

.step-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

.step-actions {
  display: flex;
  gap: 0.5rem;
}

.draft-btn, .help-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.draft-btn:hover, .help-btn:hover {
  border-color: #059669;
  color: #059669;
}

.step-content {
  background: white;
  padding: 2rem;
  flex: 1;
}

/* Navigation */
.navigation-section {
  background: white;
  border-radius: 0 0 16px 16px;
  padding: 2rem;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn.secondary {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.nav-btn.secondary:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.nav-btn.primary {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
}

.nav-btn.primary:hover:not(.disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.nav-btn.primary.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn.success {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
}

.nav-btn.success:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.step-info-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: #64748b;
}

/* Help Modal */
.help-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.help-modal {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.help-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #1e293b;
}

.help-content {
  color: #475569;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .progress-section {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .steps-indicator {
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .step-item {
    flex: 0 0 calc(50% - 0.5rem);
  }
  
  .content-area {
    margin: 0 1rem 1rem;
  }
  
  .content-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .step-icon-container {
    margin-right: 0;
  }
  
  .nav-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-btn {
    width: 100%;
    justify-content: center;
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
}
</style>
