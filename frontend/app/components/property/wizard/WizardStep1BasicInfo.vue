<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-home text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Basic Property Information</h2>
        <p class="step-subtitle">Start with the essential details about this property</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Property Classification -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-tag text-emerald-600" /> Classification
        </h3>
        <div class="form-grid">
          <div class="field" :class="{ 'has-error': errors.property_type }">
            <label>Property Type <span class="required">*</span></label>
            <div class="type-cards">
              <button
                v-for="t in propertyTypes"
                :key="t.value"
                type="button"
                class="type-card"
                :class="{ selected: form.property_type === t.value }"
                @click="selectType(t.value)"
              >
                <i :class="t.icon" class="type-icon" />
                <span>{{ t.label }}</span>
              </button>
            </div>
            <small class="error-msg" v-if="errors.property_type">{{ errors.property_type }}</small>
          </div>

          <div class="field" v-if="form.property_type">
            <label>Property Subtype</label>
            <Dropdown
              v-model="form.property_subtype"
              :options="subtypes"
              optionLabel="label"
              optionValue="value"
              placeholder="Select subtype"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- Location Details -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-map-marker text-emerald-600" /> Location Details
        </h3>
        <div class="form-grid">
          <div class="field full-width" :class="{ 'has-error': errors.address }">
            <label>Full Address <span class="required">*</span></label>
            <InputText
              v-model="form.address"
              placeholder="e.g., Bole Road, Near Atlas Hotel, Addis Ababa"
              class="w-full"
              :class="{ 'p-invalid': errors.address }"
            />
            <small class="error-msg" v-if="errors.address">{{ errors.address }}</small>
          </div>

          <div class="field" :class="{ 'has-error': errors.region }">
            <label>Region <span class="required">*</span></label>
            <Dropdown
              v-model="form.region"
              :options="ethiopianRegions"
              placeholder="Select region"
              class="w-full"
              :class="{ 'p-invalid': errors.region }"
              filter
            />
            <small class="error-msg" v-if="errors.region">{{ errors.region }}</small>
          </div>

          <div class="field" :class="{ 'has-error': errors.municipality }">
            <label>Municipality / City <span class="required">*</span></label>
            <Dropdown
              v-model="form.municipality"
              :options="municipalities"
              placeholder="Select municipality"
              class="w-full"
              :class="{ 'p-invalid': errors.municipality }"
              filter
            />
            <small class="error-msg" v-if="errors.municipality">{{ errors.municipality }}</small>
          </div>

          <div class="field">
            <label>Subcity</label>
            <InputText v-model="form.subcity" placeholder="e.g., Bole" class="w-full" />
          </div>

          <div class="field">
            <label>Woreda</label>
            <InputText v-model="form.woreda" placeholder="e.g., Woreda 03" class="w-full" />
          </div>

          <div class="field">
            <label>Kebele</label>
            <InputText v-model="form.kebele" placeholder="e.g., Kebele 01" class="w-full" />
          </div>

          <div class="field">
            <label>Zone / Block</label>
            <InputText v-model="form.zone" placeholder="e.g., Zone 4, Block 12" class="w-full" />
          </div>

          <div class="field">
            <label>Neighborhood</label>
            <InputText v-model="form.neighborhood" placeholder="e.g., CMC, Sarbet" class="w-full" />
          </div>
        </div>
      </section>

      <!-- Identity & Registration -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-id-card text-emerald-600" /> Identity & Registration
        </h3>
        <div class="form-grid">
          <div class="field">
            <label>Parcel Number</label>
            <InputText v-model="form.parcel_number" placeholder="e.g., 123/456" class="w-full" />
          </div>

          <div class="field">
            <label>Title Deed Number</label>
            <InputText v-model="form.title_deed_number" placeholder="e.g., TD-2024-001" class="w-full" />
          </div>

          <div class="field">
            <label>Registration Date</label>
            <Calendar
              v-model="registrationDateObj"
              dateFormat="yy-mm-dd"
              placeholder="Select date"
              class="w-full"
              showIcon
              @date-select="onDateSelect"
            />
          </div>

          <div class="field" v-if="form.property_ref">
            <label>Property Reference</label>
            <div class="ref-badge">
              <i class="pi pi-hashtag text-emerald-600" />
              <span class="font-mono font-semibold text-emerald-700">{{ form.property_ref }}</span>
              <span class="text-xs text-slate-400 ml-1">(auto-generated)</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePropertyWizardStore } from '~/stores/propertyWizard'

const store = usePropertyWizardStore()
const form = store.formData
const errors = computed(() => store.stepErrors[1] || {})

// Auto-generate property ref from municipality + address
watch(
  () => [form.municipality, form.address],
  ([muni, addr]) => {
    if (muni && addr && !form.property_ref) {
      const prefix = muni.substring(0, 3).toUpperCase()
      const year = new Date().getFullYear()
      const rand = Math.floor(10000 + Math.random() * 90000)
      form.property_ref = `${prefix}-${year}-${rand}`
    }
  }
)

const registrationDateObj = ref<Date | null>(
  form.registration_date ? new Date(form.registration_date) : null
)

function onDateSelect(date: Date) {
  // Use toLocaleDateString('sv') to get YYYY-MM-DD in the *local* timezone.
  // toISOString() converts to UTC first which shifts the date by -1 day for
  // users east of UTC+0 when the picker fires at midnight local time.
  form.registration_date = date.toLocaleDateString('sv')
}

function selectType(value: string) {
  form.property_type = value
  form.property_subtype = ''
  if (store.stepErrors[1]) delete store.stepErrors[1].property_type
}

const propertyTypes = [
  { value: 'residential', label: 'Residential', icon: 'pi pi-home' },
  { value: 'commercial', label: 'Commercial', icon: 'pi pi-building' },
  { value: 'industrial', label: 'Industrial', icon: 'pi pi-cog' },
  { value: 'agricultural', label: 'Agricultural', icon: 'pi pi-leaf' },
  { value: 'mixed_use', label: 'Mixed Use', icon: 'pi pi-th-large' },
  { value: 'institutional', label: 'Institutional', icon: 'pi pi-briefcase' },
]

const subtypeMap: Record<string, Array<{ label: string; value: string }>> = {
  residential: [
    { label: 'Apartment', value: 'apartment' },
    { label: 'Villa / House', value: 'villa' },
    { label: 'Condominium', value: 'condominium' },
    { label: 'Studio', value: 'studio' },
    { label: 'Guesthouse', value: 'guesthouse' },
  ],
  commercial: [
    { label: 'Office', value: 'office' },
    { label: 'Shop / Retail', value: 'shop' },
    { label: 'Hotel', value: 'hotel' },
    { label: 'Restaurant', value: 'restaurant' },
    { label: 'Warehouse', value: 'warehouse' },
  ],
  industrial: [
    { label: 'Factory', value: 'factory' },
    { label: 'Workshop', value: 'workshop' },
    { label: 'Storage Facility', value: 'storage' },
  ],
  agricultural: [
    { label: 'Farmland', value: 'farmland' },
    { label: 'Greenhouse', value: 'greenhouse' },
    { label: 'Ranch', value: 'ranch' },
  ],
  mixed_use: [{ label: 'Mixed Use', value: 'mixed_use' }],
  institutional: [
    { label: 'School / University', value: 'school' },
    { label: 'Hospital / Clinic', value: 'hospital' },
    { label: 'Government', value: 'government' },
    { label: 'Religious', value: 'religious' },
  ],
}

const subtypes = computed(() => subtypeMap[form.property_type] || [])

const ethiopianRegions = [
  'Addis Ababa', 'Dire Dawa', 'Oromia', 'Amhara', 'Tigray',
  'SNNPR', 'Somali', 'Afar', 'Benishangul-Gumuz', 'Gambela',
  'Harari', 'Sidama', 'South West Ethiopia',
]

const municipalities = [
  'Addis Ababa', 'Dire Dawa', 'Mekelle', 'Gondar', 'Bahir Dar',
  'Hawassa', 'Adama', 'Jimma', 'Dessie', 'Harar', 'Shashamane',
  'Arba Minch', 'Jijiga', 'Debre Berhan', 'Hosaena', 'Nekemte',
  'Wolaita Sodo', 'Dilla', 'Bishoftu', 'Asella',
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

.type-cards {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
}

.type-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
  padding: 0.6rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
  font-weight: 500;
  color: #64748b;
  min-width: 80px;
}
.type-card:hover { border-color: #059669; color: #059669; }
.type-card.selected { border-color: #059669; background: #f0fdf4; color: #059669; font-weight: 700; }
.type-icon { font-size: 1.2rem; }

.ref-badge {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .form-grid { grid-template-columns: 1fr; }
  .type-cards { gap: 0.35rem; }
  .type-card { min-width: 70px; padding: 0.5rem 0.6rem; }
}
</style>
