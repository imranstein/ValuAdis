<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-th-large text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Physical Characteristics</h2>
        <p class="step-subtitle">Dimensions, structure, and condition details</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Area & Dimensions -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-arrows-alt text-emerald-600" /> Area & Dimensions
        </h3>
        <div class="form-grid">
          <div class="field" :class="{ 'has-error': errors.area_sqm }">
            <label>Land Area (m²) <span class="required">*</span></label>
            <InputNumber
              v-model="form.area_sqm"
              placeholder="e.g., 250"
              :min="0"
              :useGrouping="false"
              class="w-full"
              :class="{ 'p-invalid': errors.area_sqm }"
              @update:modelValue="onAreaChange"
            />
            <small class="error-msg" v-if="errors.area_sqm">{{ errors.area_sqm }}</small>
          </div>

          <div class="field">
            <label>Building / Floor Area (m²)</label>
            <InputNumber
              v-model="form.building_area_sqm"
              placeholder="e.g., 180"
              :min="0"
              :useGrouping="false"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Number of Floors</label>
            <InputNumber
              v-model="form.number_of_floors"
              placeholder="e.g., 2"
              :min="1"
              :max="99"
              :useGrouping="false"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Number of Rooms</label>
            <InputNumber
              v-model="form.number_of_rooms"
              placeholder="e.g., 6"
              :min="1"
              :useGrouping="false"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Number of Bedrooms</label>
            <InputNumber
              v-model="form.number_of_bedrooms"
              placeholder="e.g., 3"
              :min="0"
              :useGrouping="false"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Number of Bathrooms</label>
            <InputNumber
              v-model="form.number_of_bathrooms"
              placeholder="e.g., 2"
              :min="0"
              :useGrouping="false"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Year Built</label>
            <InputNumber
              v-model="form.year_built"
              placeholder="e.g., 2005"
              :min="1800"
              :max="currentYear"
              :useGrouping="false"
              class="w-full"
            />
            <small v-if="buildingAge !== null" class="age-hint">
              Building Age: {{ buildingAge }} year{{ buildingAge !== 1 ? 's' : '' }}
            </small>
          </div>

          <div class="field">
            <label>Parking Spaces</label>
            <InputNumber
              v-model="form.parking_spaces"
              placeholder="e.g., 1"
              :min="0"
              :useGrouping="false"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- Materials -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-box text-emerald-600" /> Construction Materials
        </h3>
        <div class="form-grid">
          <div class="field">
            <label>Construction Material</label>
            <Dropdown
              v-model="form.construction_material"
              :options="constructionMaterials"
              optionLabel="label"
              optionValue="value"
              placeholder="Select material"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Roof Material</label>
            <Dropdown
              v-model="form.roof_material"
              :options="roofMaterials"
              optionLabel="label"
              optionValue="value"
              placeholder="Select material"
              class="w-full"
            />
          </div>

          <div class="field">
            <label>Floor Material</label>
            <Dropdown
              v-model="form.floor_material"
              :options="floorMaterials"
              optionLabel="label"
              optionValue="value"
              placeholder="Select material"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- Quality & Condition -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-star text-emerald-600" /> Quality & Condition
        </h3>

        <!-- Construction Quality -->
        <div class="field">
          <label>Construction Quality</label>
          <div class="quality-cards">
            <button
              v-for="q in constructionQualities"
              :key="q.value"
              type="button"
              class="quality-card"
              :class="{ selected: form.construction_quality === q.value }"
              @click="selectQuality(q.value)"
            >
              <i :class="q.icon" class="quality-icon" />
              <span>{{ q.label }}</span>
            </button>
          </div>
        </div>

        <!-- Condition -->
        <div class="field" :class="{ 'has-error': errors.condition }">
          <label>Property Condition <span class="required">*</span></label>
          <div class="quality-cards">
            <button
              v-for="c in propertyConditions"
              :key="c.value"
              type="button"
              class="quality-card"
              :class="[{ selected: form.condition === c.value }, c.colorClass]"
              @click="selectCondition(c.value)"
            >
              <i :class="[c.icon, 'quality-icon', c.iconColor]" />
              <span>{{ c.label }}</span>
            </button>
          </div>
          <small class="error-msg" v-if="errors.condition">{{ errors.condition }}</small>
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
const errors = computed(() => store.stepErrors[3] || {})

const currentYear = new Date().getFullYear()

const buildingAge = computed(() =>
  form.year_built ? currentYear - form.year_built : null
)

function onAreaChange() {
  if (store.stepErrors[3]) delete store.stepErrors[3].area_sqm
}

function selectQuality(value: string) {
  form.construction_quality = value
}

function selectCondition(value: string) {
  form.condition = value
  if (store.stepErrors[3]) delete store.stepErrors[3].condition
}

const constructionMaterials = [
  { label: 'Concrete Reinforced', value: 'concrete' },
  { label: 'Brick', value: 'brick' },
  { label: 'Wood', value: 'wood' },
  { label: 'Iron / Steel Sheet', value: 'iron' },
  { label: 'Mixed', value: 'mixed' },
]

const roofMaterials = [
  { label: 'Concrete Slab', value: 'concrete' },
  { label: 'Iron Sheet', value: 'iron_sheet' },
  { label: 'Ceramic Tiles', value: 'tiles' },
  { label: 'Thatch', value: 'thatch' },
]

const floorMaterials = [
  { label: 'Ceramic Tiles', value: 'tiles' },
  { label: 'Marble', value: 'marble' },
  { label: 'Cement Screed', value: 'cement' },
  { label: 'Hardwood', value: 'wood' },
  { label: 'Carpet', value: 'carpet' },
]

const constructionQualities = [
  { value: 'premium', label: 'Premium', icon: 'pi pi-star' },
  { value: 'good', label: 'Good', icon: 'pi pi-thumbs-up' },
  { value: 'average', label: 'Average', icon: 'pi pi-minus' },
  { value: 'poor', label: 'Poor', icon: 'pi pi-exclamation-circle' },
]

const propertyConditions = [
  { value: 'excellent', label: 'Excellent', icon: 'pi pi-check-circle', iconColor: 'text-emerald', colorClass: '' },
  { value: 'good', label: 'Good', icon: 'pi pi-thumbs-up', iconColor: 'text-blue', colorClass: '' },
  { value: 'fair', label: 'Fair', icon: 'pi pi-minus', iconColor: 'text-amber', colorClass: '' },
  { value: 'poor', label: 'Poor', icon: 'pi pi-exclamation-circle', iconColor: 'text-red', colorClass: '' },
]
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
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

.form-section { display: flex; flex-direction: column; gap: 1rem; }

.section-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.95rem; font-weight: 600; color: #334155;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field.full-width { grid-column: 1 / -1; }
.field label { font-size: 0.8rem; font-weight: 600; color: #475569; }
.required { color: #dc2626; }
.error-msg { color: #dc2626; font-size: 0.75rem; }
.has-error label { color: #dc2626; }

.age-hint {
  font-size: 0.75rem;
  color: #059669;
  font-weight: 500;
}

.quality-cards {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
}

.quality-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
  padding: 0.6rem 1.2rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
  font-weight: 500;
  color: #64748b;
  min-width: 90px;
}
.quality-card:hover { border-color: #059669; color: #059669; }
.quality-card.selected { border-color: #059669; background: #f0fdf4; color: #059669; font-weight: 700; }

.quality-icon { font-size: 1.2rem; }

/* Condition icon colour hints */
.text-emerald { color: #059669; }
.text-blue { color: #3b82f6; }
.text-amber { color: #f59e0b; }
.text-red { color: #ef4444; }

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .form-grid { grid-template-columns: 1fr; }
  .quality-cards { gap: 0.35rem; }
  .quality-card { min-width: 75px; padding: 0.5rem 0.6rem; }
}
</style>
