<template>
  <div class="wizard-step bg-white rounded-2xl shadow-xl overflow-hidden">
    <!-- Modern Header with Gradient -->
    <div class="step-header bg-gradient-to-r from-emerald-600 to-teal-600 p-6 relative overflow-hidden">
      <div class="absolute inset-0 bg-black opacity-5"></div>
      <div class="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full -mr-16 -mt-16"></div>
      <div class="absolute bottom-0 left-0 w-24 h-24 bg-white opacity-10 rounded-full -ml-12 -mb-12"></div>
      
      <div class="relative z-10 flex items-center gap-4">
        <div class="step-icon-wrap bg-white/20 backdrop-blur-sm p-3 rounded-2xl border border-white/30">
          <i class="pi pi-home text-3xl text-white"></i>
        </div>
        <div>
          <h2 class="step-title text-2xl font-bold text-white mb-1">Basic Property Information</h2>
          <p class="step-subtitle text-emerald-100 text-sm">Start with the essential details about this property</p>
        </div>
      </div>
    </div>

    <div class="step-body p-8 space-y-8">
      <!-- Property Classification Section -->
      <section class="form-section bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-tag text-emerald-600 text-lg"></i>
          </div>
          <h3 class="section-title text-lg font-semibold text-gray-800">Property Classification</h3>
        </div>
        
        <div class="space-y-6">
          <!-- Property Type Cards -->
          <div class="field" :class="{ 'has-error': errors.property_type }">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Property Type <span class="required text-red-500">*</span>
            </label>
            <div class="type-cards grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              <button
                v-for="t in propertyTypes"
                :key="t.value"
                type="button"
                class="type-card group relative overflow-hidden transition-all duration-300 transform hover:scale-105"
                :class="{ 
                  'selected': form.property_type === t.value,
                  'ring-2 ring-emerald-500 ring-offset-2': form.property_type === t.value
                }"
                @click="selectType(t.value)"
              >
                <div class="absolute inset-0 bg-gradient-to-br from-emerald-50 to-teal-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div class="relative p-4 text-center">
                  <i :class="t.icon" class="type-icon text-2xl mb-2 transition-colors duration-300"
                     :class="form.property_type === t.value ? 'text-emerald-600' : 'text-gray-500 group-hover:text-emerald-600'"></i>
                  <span class="block text-sm font-medium transition-colors duration-300"
                        :class="form.property_type === t.value ? 'text-emerald-700' : 'text-gray-700 group-hover:text-emerald-700'">{{ t.label }}</span>
                </div>
              </button>
            </div>
            <div x-show="errors.property_type" x-transition class="error-msg mt-2 text-sm text-red-600 flex items-center gap-2">
              <i class="pi pi-exclamation-triangle"></i>
              <span>{{ errors.property_type }}</span>
            </div>
          </div>

          <!-- Property Subtype -->
          <div x-show="form.property_type" x-transition class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Property Subtype</label>
            <div class="relative">
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
        </div>
      </section>

      <!-- Location Details Section -->
      <section class="form-section bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-map-marker text-blue-600 text-lg"></i>
          </div>
          <h3 class="section-title text-lg font-semibold text-gray-800">Location Details</h3>
        </div>
        
        <div class="form-grid grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Full Address Field -->
          <div class="field md:col-span-2" :class="{ 'has-error': errors.address }">
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Full Address <span class="required text-red-500">*</span>
            </label>
            <div class="relative">
              <InputText
                v-model="form.address"
                placeholder="e.g., Bole Road, Near Atlas Hotel, Addis Ababa"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                :class="{ 'border-red-500 ring-red-500': errors.address }"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-map-marker text-gray-400"></i>
              </div>
            </div>
            <div x-show="errors.address" x-transition class="error-msg mt-2 text-sm text-red-600 flex items-center gap-2">
              <i class="pi pi-exclamation-circle"></i>
              <span>{{ errors.address }}</span>
            </div>
          </div>

          <!-- Region Field -->
          <div class="field" :class="{ 'has-error': errors.region }">
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Region <span class="required text-red-500">*</span>
            </label>
            <div class="relative">
              <Dropdown
                v-model="form.region"
                :options="ethiopianRegions"
                placeholder="Select region"
                class="w-full"
                :class="{ 'border-red-500 ring-red-500': errors.region }"
                filter
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-chevron-down text-gray-400"></i>
              </div>
            </div>
            <div x-show="errors.region" x-transition class="error-msg mt-2 text-sm text-red-600 flex items-center gap-2">
              <i class="pi pi-exclamation-circle"></i>
              <span>{{ errors.region }}</span>
            </div>
          </div>

          <!-- Municipality Field -->
          <div class="field" :class="{ 'has-error': errors.municipality }">
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Municipality / City <span class="required text-red-500">*</span>
            </label>
            <div class="relative">
              <Dropdown
                v-model="form.municipality"
                :options="municipalities"
                placeholder="Select municipality"
                class="w-full"
                :class="{ 'border-red-500 ring-red-500': errors.municipality }"
                filter
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-building text-gray-400"></i>
              </div>
            </div>
            <div x-show="errors.municipality" x-transition class="error-msg mt-2 text-sm text-red-600 flex items-center gap-2">
              <i class="pi pi-exclamation-circle"></i>
              <span>{{ errors.municipality }}</span>
            </div>
          </div>

          <!-- Subcity Field -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Subcity</label>
            <div class="relative">
              <InputText 
                v-model="form.subcity" 
                placeholder="e.g., Bole" 
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-home text-gray-400"></i>
              </div>
            </div>
          </div>

          <div class="field">
            <label>Woreda</label>
            <InputText v-model="form.woreda" placeholder="e.g., Woreda 03" class="w-full" />
          </div>

          <!-- Kebele Field -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Kebele</label>
            <div class="relative">
              <InputText 
                v-model="form.kebele" 
                placeholder="e.g., Kebele 01" 
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-map text-gray-400"></i>
              </div>
            </div>
          </div>

          <!-- Zone / Block Field -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Zone / Block</label>
            <div class="relative">
              <InputText 
                v-model="form.zone" 
                placeholder="e.g., Zone 4, Block 12" 
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-map text-gray-400"></i>
              </div>
            </div>
          </div>

          <!-- Neighborhood Field -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Neighborhood</label>
            <div class="relative">
              <InputText 
                v-model="form.neighborhood" 
                placeholder="e.g., CMC, Sarbet" 
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <i class="pi pi-map text-gray-400"></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Property Reference Section -->
      <section class="form-section bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-hashtag text-emerald-600 text-lg"></i>
          </div>
          <h3 class="section-title text-lg font-semibold text-gray-800">Property Reference</h3>
        </div>
        
        <div class="ref-badge bg-white rounded-lg p-4 border border-emerald-200 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0">
              <i class="pi pi-info-circle text-emerald-600 text-sm"></i>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-700">
                Reference: 
                <span :class="form.property_ref ? 'text-emerald-600 font-semibold' : 'text-gray-500 italic'">
                  {{ form.property_ref || 'Will be auto-generated when you save' }}
                </span>
              </p>
              <p class="text-xs text-gray-500 mt-1">Format: ADD-YYYY-XXXXX (Ethiopian Property ID)</p>
            </div>
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
import { storeToRefs } from 'pinia'
import { usePropertyWizardStore } from '~/stores/propertyWizard'

const store = usePropertyWizardStore()
const { formData: form } = storeToRefs(store)
const errors = computed(() => store.stepErrors[1] || {})

// Auto-generate property ref from municipality + address
watch(
  () => [form.value.municipality, form.value.address],
  ([muni, addr]) => {
    if (muni && addr && !form.value.property_ref) {
      const prefix = muni.substring(0, 3).toUpperCase()
      const year = new Date().getFullYear()
      const rand = Math.floor(10000 + Math.random() * 90000)
      form.value.property_ref = `${prefix}-${year}-${rand}`
    }
  }
)

// Trigger validation when required fields change
watch(
  () => [form.value.property_type, form.value.address, form.value.municipality, form.value.region],
  () => {
    // Re-validate step 1 when any required field changes
    store.validateStep(1)
  },
  { deep: true }
)

const registrationDateObj = ref<Date | null>(
  form.value.registration_date ? new Date(form.value.registration_date) : null
)

function onDateSelect(date: Date) {
  // Use toLocaleDateString('sv') to get YYYY-MM-DD in the *local* timezone.
  // toISOString() converts to UTC first which shifts the date by -1 day for
  // users east of UTC+0 when the picker fires at midnight local time.
  form.value.registration_date = date.toLocaleDateString('sv')
}

function selectType(value: string) {
  form.value.property_type = value
  form.value.property_subtype = ''
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

const subtypes = computed(() => subtypeMap[form.value.property_type] || [])

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
/* Modern Tailwind-based styles with enhanced interactivity */

/* Type card animations */
.type-card {
  @apply bg-white border-2 border-gray-200 rounded-xl cursor-pointer transition-all duration-300;
  min-width: 80px;
}

.type-card:hover {
  @apply border-emerald-500 shadow-lg transform scale-105;
}

.type-card.selected {
  @apply border-emerald-500 bg-emerald-50 shadow-md ring-2 ring-emerald-500 ring-offset-2;
}

/* Error states */
.has-error :deep(.p-inputtext) {
  @apply border-red-500 ring-red-500;
}

.has-error :deep(.p-dropdown) {
  @apply border-red-500 ring-red-500;
}

/* Enhanced focus states */
.field :deep(.p-inputtext:focus) {
  @apply ring-2 ring-blue-500 border-transparent;
}

.field :deep(.p-dropdown:focus) {
  @apply ring-2 ring-blue-500 border-transparent;
}

/* Smooth transitions for all interactive elements */
.field :deep(.p-inputtext),
.field :deep(.p-dropdown),
.type-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Loading states */
.field :deep(.p-inputtext:disabled),
.field :deep(.p-dropdown:disabled) {
  @apply bg-gray-100 cursor-not-allowed opacity-60;
}

/* Mobile responsive improvements */
@media (max-width: 640px) {
  .type-cards {
    @apply grid-cols-2 gap-2;
  }
  
  .type-card {
    @apply min-w-[70px] p-3;
  }
}

/* Enhanced hover effects for property type cards */
.type-card::before {
  content: '';
  @apply absolute inset-0 bg-gradient-to-br from-emerald-50 to-teal-50 opacity-0 transition-opacity duration-300;
}

.type-card:hover::before {
  @apply opacity-100;
}

/* Custom animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-section {
  animation: slideIn 0.5s ease-out;
}

/* Enhanced error message styling */
.error-msg {
  @apply flex items-center gap-2 text-sm text-red-600 mt-2;
  animation: slideIn 0.3s ease-out;
}

/* Reference badge enhancements */
.ref-badge {
  @apply bg-white rounded-lg border border-emerald-200 shadow-sm;
  transition: all 0.3s ease;
}

.ref-badge:hover {
  @apply shadow-md border-emerald-300;
}
</style>
