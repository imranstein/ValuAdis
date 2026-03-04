<template>
  <div class="create-property-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Create Property</h1>
        <p>Add a new property to the system with comprehensive details</p>
      </div>
      <div class="header-actions">
        <Button
          label="Back to Properties"
          icon="pi pi-arrow-left"
          severity="secondary"
          @click="goBack"
        />
      </div>
    </div>

    <!-- Progress Indicator -->
    <div class="progress-indicator">
      <div class="progress-steps">
        <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
          <div class="step-number">1</div>
          <span class="step-label">Basic Info</span>
        </div>
        <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
          <div class="step-number">2</div>
          <span class="step-label">Characteristics</span>
        </div>
        <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
          <div class="step-number">3</div>
          <span class="step-label">Location</span>
        </div>
        <div class="step" :class="{ active: currentStep >= 4, completed: currentStep > 4 }">
          <div class="step-number">4</div>
          <span class="step-label">Ownership</span>
        </div>
        <div class="step" :class="{ active: currentStep >= 5, completed: currentStep > 5 }">
          <div class="step-number">5</div>
          <span class="step-label">Documents</span>
        </div>
      </div>
    </div>

    <!-- Property Form -->
    <div class="form-container">
      <!-- Messages moved to top of form -->
      <Message v-if="error" severity="error" :closable="false">
        {{ error }}
      </Message>

      <Message v-if="success" severity="success" :closable="false">
        {{ success }}
      </Message>
      
      <PropertyForm
        :initial-data="formData"
        :loading="loading"
        @submit="handleSubmit"
        @cancel="goBack"
        @save-draft="saveDraft"
        @update-step="(step) => currentStep = step"
        v-model:step="currentStep"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PropertyForm from '~/components/property/PropertyForm.vue'

const router = useRouter()

const formData = ref({})
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const currentStep = ref(1)

// Restore draft on mount
onMounted(() => {
  try {
    const draft = localStorage.getItem('property_draft')
    if (draft) {
      const parsedDraft = JSON.parse(draft)
      // Merge draft into form data
      formData.value = { ...formData.value, ...parsedDraft }
    }
  } catch (err) {
    console.warn('Failed to restore draft:', err)
    // Leave formData as-is if draft is invalid
  }
})

async function handleSubmit(data) {
  loading.value = true
  error.value = null
  success.value = null

  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'
    
    const response = await fetch(`${API_BASE}/api/v1/properties`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })

    let result
    try {
      if (response.headers.get('content-type')?.includes('application/json')) {
        result = await response.json()
      } else {
        result = { text: await response.text() }
      }
    } catch (parseErr) {
      result = { text: await response.text() }
    }

    if (response.ok) {
      success.value = 'Property created successfully!'
      // Clear draft on successful submit
      localStorage.removeItem('property_draft')
      setTimeout(() => {
        router.push('/properties')
      }, 1500)
    } else {
      const errorMessage = result.detail || result.message || result.text || 'Failed to create property'
      error.value = `Error ${response.status}: ${errorMessage}`
    }
  } catch (err) {
    error.value = 'Network error. Please check your connection.'
  } finally {
    loading.value = false
  }
}

function saveDraft(data) {
  // Save draft to localStorage
  localStorage.setItem('property_draft', JSON.stringify(data))
  success.value = 'Draft saved successfully!'
}

function goBack() {
  router.push('/properties')
}
</script>

<style scoped>
.create-property-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2);
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.header-content p {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

.progress-indicator {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: #e2e8f0;
  z-index: 0;
  transform: translateY(-50%);
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  background: #e2e8f0;
  color: #64748b;
  border: 2px solid white;
  transition: all 0.3s;
}

.step.active .step-number {
  background: #059669;
  color: white;
  box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.1);
}

.step.completed .step-number {
  background: #10b981;
  color: white;
}

.step-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.step.active .step-label {
  color: #059669;
  font-weight: 600;
}

.step.completed .step-label {
  color: #10b981;
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .progress-steps {
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .progress-steps::before {
    display: none;
  }
  
  .step {
    flex: 1;
    min-width: 80px;
  }
}
</style>
