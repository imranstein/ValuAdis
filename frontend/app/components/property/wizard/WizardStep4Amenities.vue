<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-star text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Amenities &amp; Utilities</h2>
        <p class="step-subtitle">Select all available features and services</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Summary Badge -->
      <div class="summary-row">
        <span class="summary-badge">
          <i class="pi pi-info-circle" />
          {{ amenityCount }} amenit{{ amenityCount !== 1 ? 'ies' : 'y' }}, {{ utilityCount }} utilit{{ utilityCount !== 1 ? 'ies' : 'y' }} selected
        </span>
      </div>

      <!-- Amenities Section -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-building text-emerald-600" /> Amenities
        </h3>
        <div class="feature-grid">
          <div
            v-for="item in amenityItems"
            :key="item.key"
            class="feature-card"
            :class="{ selected: form.amenities[item.key] }"
            @click="toggleAmenity(item.key)"
          >
            <i :class="item.icon" class="feature-icon" />
            <span>{{ item.label }}</span>
          </div>
        </div>
      </section>

      <!-- Utilities Section -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-bolt text-emerald-600" /> Utilities
        </h3>
        <div class="feature-grid">
          <div
            v-for="item in utilityItems"
            :key="item.key"
            class="feature-card"
            :class="{ selected: form.utilities[item.key] }"
            @click="toggleUtility(item.key)"
          >
            <i :class="item.icon" class="feature-icon" />
            <span>{{ item.label }}</span>
          </div>
        </div>
      </section>

      <!-- Additional Features Section -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-pencil text-emerald-600" /> Additional Features
        </h3>
        <div class="field">
          <label>Describe any other notable features</label>
          <Textarea
            v-model="form.additional_features"
            :rows="4"
            placeholder="e.g., rooftop terrace, servant quarters, double-glazed windows, backup borehole..."
            class="w-full"
            auto-resize
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePropertyWizardStore } from '~/stores/propertyWizard'

const store = usePropertyWizardStore()
const form = store.formData

// Initialize amenities with defaults if empty
if (!form.amenities || Object.keys(form.amenities).length === 0) {
  form.amenities = {
    elevator: false,
    security: false,
    generator: false,
    water_tank: false,
    solar: false,
    cctv: false,
    gym: false,
    pool: false,
    garden: false,
    fence: false,
  }
}

// Initialize utilities with defaults if empty
if (!form.utilities || Object.keys(form.utilities).length === 0) {
  form.utilities = {
    electricity: true,
    water: true,
    internet: false,
    sewage: false,
    gas: false,
  }
}

function toggleAmenity(key: string) {
  form.amenities[key] = !form.amenities[key]
}

function toggleUtility(key: string) {
  form.utilities[key] = !form.utilities[key]
}

const amenityCount = computed(() =>
  Object.values(form.amenities).filter(Boolean).length
)

const utilityCount = computed(() =>
  Object.values(form.utilities).filter(Boolean).length
)

const amenityItems = [
  { key: 'elevator',   icon: 'pi pi-arrow-up', label: 'Elevator' },
  { key: 'security',   icon: 'pi pi-shield',   label: 'Security Guard' },
  { key: 'generator',  icon: 'pi pi-bolt',     label: 'Generator' },
  { key: 'water_tank', icon: 'pi pi-tint',     label: 'Water Tank' },
  { key: 'solar',      icon: 'pi pi-sun',      label: 'Solar Panels' },
  { key: 'cctv',       icon: 'pi pi-video',    label: 'CCTV' },
  { key: 'gym',        icon: 'pi pi-heart',    label: 'Gym / Fitness' },
  { key: 'pool',       icon: 'pi pi-circle',   label: 'Swimming Pool' },
  { key: 'garden',     icon: 'pi pi-images',   label: 'Garden' },
  { key: 'fence',      icon: 'pi pi-lock',     label: 'Perimeter Fence' },
]

const utilityItems = [
  { key: 'electricity', icon: 'pi pi-bolt',   label: 'Electricity' },
  { key: 'water',       icon: 'pi pi-tint',   label: 'Water Supply' },
  { key: 'internet',    icon: 'pi pi-wifi',   label: 'Internet / Fiber' },
  { key: 'sewage',      icon: 'pi pi-filter', label: 'Sewage System' },
  { key: 'gas',         icon: 'pi pi-circle', label: 'Natural Gas' },
]
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.step-icon-wrap {
  width: 48px; height: 48px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.step-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.2rem; }
.step-subtitle { font-size: 0.875rem; opacity: 0.85; margin: 0; }

.step-body { padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }

.summary-row { display: flex; justify-content: flex-start; }

.summary-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.9rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1d4ed8;
}

.form-section { display: flex; flex-direction: column; gap: 1rem; }

.section-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.95rem; font-weight: 600; color: #334155;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
  margin: 0;
}

.feature-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.feature-card {
  width: 130px;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
  font-weight: 500;
  color: #64748b;
  background: white;
  user-select: none;
}

.feature-card:hover {
  border-color: #059669;
  color: #059669;
}

.feature-card.selected {
  border-color: #059669;
  background: #f0fdf4;
  color: #059669;
  font-weight: 700;
}

.feature-icon { font-size: 1.5rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: #475569; }

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .feature-card { width: 100px; min-height: 70px; font-size: 0.75rem; }
  .feature-icon { font-size: 1.2rem; }
}
</style>
