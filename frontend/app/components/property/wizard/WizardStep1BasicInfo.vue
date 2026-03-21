<template>
  <div class="wizard-step bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
    <!-- Premium Header with Gradient -->
    <div class="step-header bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 p-8 relative overflow-hidden">
      <div class="absolute inset-0 bg-black opacity-10"></div>
      <div class="absolute top-0 right-0 w-40 h-40 bg-white opacity-5 rounded-full -mr-20 -mt-20"></div>
      <div class="absolute bottom-0 left-0 w-32 h-32 bg-white opacity-5 rounded-full -ml-16 -mb-16"></div>
      
      <div class="relative z-10 flex items-center gap-6">
        <div class="step-icon-wrap bg-white/20 backdrop-blur-sm p-4 rounded-2xl border border-white/30 shadow-lg">
          <i class="pi pi-home text-4xl text-white"></i>
        </div>
        <div class="flex-1">
          <h2 class="step-title text-3xl font-bold text-white mb-2 tracking-tight">Basic Property Information</h2>
          <p class="step-subtitle text-emerald-50 text-lg font-medium">Start with the essential details about this property</p>
        </div>
      </div>
    </div>

    <div class="step-body p-10 space-y-10">
      <!-- Property Classification Section -->
      <section class="form-section bg-gradient-to-br from-gray-50 to-emerald-50 rounded-2xl p-8 border border-gray-200 shadow-sm">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-lg">
            <i class="pi pi-tag text-white text-xl"></i>
          </div>
          <div>
            <h3 class="section-title text-xl font-bold text-gray-800">Property Classification</h3>
            <p class="text-gray-600 text-sm mt-1">Select the primary category of your property</p>
          </div>
        </div>
        
        <div class="space-y-6">
          <!-- Property Type Cards -->
          <div class="field" :class="{ 'has-error': errors.property_type }">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Property Type <span class="required text-red-500">*</span>
            </label>
            <div class="type-cards grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <button
                v-for="t in propertyTypes"
                :key="t.value"
                type="button"
                class="type-card group relative overflow-hidden transition-all duration-500 transform hover:scale-105 hover:shadow-xl"
                :class="{ 
                  'selected': form.property_type === t.value,
                  'ring-4 ring-emerald-500 ring-offset-4': form.property_type === t.value
                }"
                @click="selectType(t.value)"
              >
                <div class="absolute inset-0 bg-gradient-to-br from-emerald-50 to-teal-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <div class="relative p-6 text-center">
                  <i :class="[
                    t.icon,
                    'type-icon text-3xl mb-3 transition-all duration-500',
                    form.property_type === t.value ? 'text-emerald-600 scale-110' : 'text-gray-500 group-hover:text-emerald-600 group-hover:scale-105'
                  ]"></i>
                  <span class="block text-sm font-semibold transition-all duration-500"
                        :class="form.property_type === t.value ? 'text-emerald-700' : 'text-gray-700 group-hover:text-emerald-700'">{{ t.label }}</span>
                </div>
              </button>
            </div>
            <div v-if="errors.property_type" class="error-msg mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
              <i class="pi pi-exclamation-triangle text-red-500"></i>
              <span class="font-medium">{{ errors.property_type }}</span>
            </div>
          </div>

          <!-- Property Subtype -->
          <div v-if="form.property_type" class="field animate-fadeIn">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-list text-emerald-500"></i>
              Property Subtype
            </label>
            <div class="relative">
              <Dropdown
                v-model="form.property_subtype"
                :options="subtypes"
                optionLabel="label"
                optionValue="value"
                placeholder="Select subtype"
                class="w-full"
                :class="{ 'border-red-500 ring-red-500': errors.property_subtype }"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Location Details Section -->
      <section class="form-section bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-200 shadow-sm">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
            <i class="pi pi-map-marker text-white text-xl"></i>
          </div>
          <div>
            <h3 class="section-title text-xl font-bold text-gray-800">Location Details</h3>
            <p class="text-gray-600 text-sm mt-1">Provide the complete address information</p>
          </div>
        </div>
        
        <div class="form-grid grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Full Address Field -->
          <div class="field md:col-span-2" :class="{ 'has-error': errors.address }">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-home text-blue-500"></i>
              Full Address <span class="required text-red-500 ml-1">*</span>
            </label>
            <div class="relative group">
              <InputText
                v-model="form.address"
                placeholder="e.g., Bole Road, Near Atlas Hotel, Addis Ababa"
                class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg"
                :class="{ 'border-red-500 ring-red-500/20': errors.address }"
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-map-marker text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
            <div v-if="errors.address" class="error-msg mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
              <i class="pi pi-exclamation-circle text-red-500"></i>
              <span class="font-medium">{{ errors.address }}</span>
            </div>
          </div>

          <!-- Region Field -->
          <div class="field" :class="{ 'has-error': errors.region }">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-globe text-blue-500"></i>
              Region <span class="required text-red-500 ml-1">*</span>
            </label>
            <div class="relative group">
              <Dropdown
                v-model="form.region"
                :options="ethiopianRegions"
                placeholder="Select region"
                class="w-full"
                :class="{ 'border-red-500 ring-red-500/20': errors.region }"
                filter
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-chevron-down text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
            <div v-if="errors.region" class="error-msg mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
              <i class="pi pi-exclamation-circle text-red-500"></i>
              <span class="font-medium">{{ errors.region }}</span>
            </div>
          </div>

          <!-- Municipality Field -->
          <div class="field" :class="{ 'has-error': errors.municipality }">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-building text-blue-500"></i>
              Municipality / City <span class="required text-red-500 ml-1">*</span>
            </label>
            <div class="relative group">
              <Dropdown
                v-model="form.municipality"
                :options="municipalities"
                placeholder="Select municipality"
                class="w-full"
                :class="{ 'border-red-500 ring-red-500/20': errors.municipality }"
                filter
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-building text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
            <div v-if="errors.municipality" class="error-msg mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
              <i class="pi pi-exclamation-circle text-red-500"></i>
              <span class="font-medium">{{ errors.municipality }}</span>
            </div>
          </div>

          <!-- Subcity Field -->
          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-home text-blue-500"></i>
              Subcity
            </label>
            <div class="relative group">
              <InputText 
                v-model="form.subcity" 
                placeholder="e.g., Bole" 
                class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg"
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-home text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
          </div>

          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-map text-blue-500"></i>
              Woreda
            </label>
            <InputText v-model="form.woreda" placeholder="e.g., Woreda 03" class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg" />
          </div>

          <!-- Kebele Field -->
          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-map text-blue-500"></i>
              Kebele
            </label>
            <div class="relative group">
              <InputText 
                v-model="form.kebele" 
                placeholder="e.g., Kebele 01" 
                class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg"
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-map text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
          </div>

          <!-- Zone / Block Field -->
          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-th-large text-blue-500"></i>
              Zone / Block
            </label>
            <div class="relative group">
              <InputText 
                v-model="form.zone" 
                placeholder="e.g., Zone 4, Block 12" 
                class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg"
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-th-large text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
          </div>

          <!-- Neighborhood Field -->
          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-users text-blue-500"></i>
              Neighborhood
            </label>
            <div class="relative group">
              <InputText 
                v-model="form.neighborhood" 
                placeholder="e.g., CMC, Sarbet" 
                class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg"
              />
              <div class="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                <i class="pi pi-users text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Property Reference Section -->
      <section class="form-section bg-gradient-to-r from-emerald-50 via-teal-50 to-cyan-50 rounded-2xl p-8 border border-emerald-200 shadow-sm">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-lg">
            <i class="pi pi-hashtag text-white text-xl"></i>
          </div>
          <div>
            <h3 class="section-title text-xl font-bold text-gray-800">Property Reference</h3>
            <p class="text-gray-600 text-sm mt-1">Unique identifier for your property</p>
          </div>
        </div>
        
        <div class="ref-badge bg-white rounded-2xl p-6 border border-emerald-200 shadow-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
              <i class="pi pi-info-circle text-white text-xl"></i>
            </div>
            <div class="flex-1">
              <p class="text-lg font-semibold text-gray-700 mb-2">
                Reference: 
                <span :class="form.property_ref ? 'text-emerald-600 font-bold text-xl' : 'text-gray-500 italic'">
                  {{ form.property_ref || 'Will be auto-generated when you save' }}
                </span>
              </p>
              <p class="text-sm text-gray-600 bg-emerald-50 px-3 py-1 rounded-lg inline-block">Format: ADD-YYYY-XXXXX (Ethiopian Property ID)</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Identity & Registration -->
      <section class="form-section bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-8 border border-purple-200 shadow-sm">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
            <i class="pi pi-id-card text-white text-xl"></i>
          </div>
          <div>
            <h3 class="section-title text-xl font-bold text-gray-800">Identity & Registration</h3>
            <p class="text-gray-600 text-sm mt-1">Legal and registration information</p>
          </div>
        </div>
        <div class="form-grid grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-file text-purple-500"></i>
              Parcel Number
            </label>
            <InputText v-model="form.parcel_number" placeholder="e.g., 123/456" class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 transition-all duration-300 text-lg" />
          </div>

          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-certificate text-purple-500"></i>
              Title Deed Number
            </label>
            <InputText v-model="form.title_deed_number" placeholder="e.g., TD-2024-001" class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 transition-all duration-300 text-lg" />
          </div>

          <div class="field">
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-calendar text-purple-500"></i>
              Registration Date
            </label>
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
            <label class="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <i class="pi pi-hashtag text-purple-500"></i>
              Property Reference
            </label>
            <div class="ref-badge bg-gradient-to-r from-purple-100 to-indigo-100 rounded-2xl p-4 border border-purple-200 shadow-lg">
              <div class="flex items-center gap-3">
                <i class="pi pi-hashtag text-purple-600 text-xl" />
                <span class="font-mono font-bold text-purple-700 text-lg">{{ form.property_ref }}</span>
                <span class="text-xs text-purple-500 ml-2 bg-purple-200 px-2 py-1 rounded-full">auto-generated</span>
              </div>
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
/* Professional Modern Styles with Enhanced Interactivity */

/* Type card animations and styling */
.type-card {
  @apply bg-white border-2 border-gray-200 rounded-2xl cursor-pointer;
  min-width: 100px;
  min-height: 120px;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.type-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.5s ease;
}

.type-card:hover::before {
  opacity: 1;
}

.type-card:hover {
  @apply border-emerald-500 shadow-2xl transform scale-105;
  box-shadow: 0 20px 25px -5px rgba(16, 185, 129, 0.15), 0 10px 10px -5px rgba(16, 185, 129, 0.1);
}

.type-card.selected {
  @apply border-emerald-500 bg-gradient-to-br from-emerald-50 to-teal-50 shadow-xl;
  box-shadow: 0 20px 25px -5px rgba(16, 185, 129, 0.2), 0 10px 10px -5px rgba(16, 185, 129, 0.15);
}

.type-card.selected::before {
  opacity: 1;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
}

/* Enhanced form sections with design system */
.form-section {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border-color: var(--border);
}

.form-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--gradient-start, #10b981) 0%, var(--gradient-end, #059669) 100%);
}

.form-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Professional error states with design system */
.has-error :deep(.p-inputtext) {
  border-color: var(--error) !important;
  box-shadow: 0 0 0 3px rgba(255, 68, 68, 0.15);
}

.has-error :deep(.p-dropdown) {
  border-color: var(--error) !important;
  box-shadow: 0 0 0 3px rgba(255, 68, 68, 0.15);
}

.error-msg {
  animation: slideInUp var(--transition-base);
  border-left: 4px solid var(--error);
  color: var(--error);
  background: rgba(255, 68, 68, 0.08);
}

/* Enhanced focus states with design system glow */
.field :deep(.p-inputtext) {
  min-height: 44px !important;
  font-family: var(--font-family-base);
  transition: all var(--transition-base);
}

.field :deep(.p-inputtext:focus) {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 4px var(--cyan-dim), var(--shadow-glow);
  transform: translateY(-1px);
}

.field :deep(.p-dropdown) {
  min-height: 44px !important;
  font-family: var(--font-family-base);
  transition: all var(--transition-base);
}

.field :deep(.p-dropdown:focus) {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 4px var(--cyan-dim), var(--shadow-glow);
  transform: translateY(-1px);
}

/* Smooth transitions for all interactive elements */
.field :deep(.p-inputtext),
.field :deep(.p-dropdown),
.type-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Professional loading states */
.field :deep(.p-inputtext:disabled),
.field :deep(.p-dropdown:disabled) {
  @apply bg-gray-100 cursor-not-allowed opacity-60;
}

/* Enhanced mobile responsiveness */
@media (max-width: 768px) {
  .type-cards {
    @apply grid-cols-2 gap-4;
  }
  
  .type-card {
    @apply min-w-[80px] p-4;
    min-height: 100px;
  }
  
  .form-section {
    @apply p-6;
  }
}

/* Professional animations */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out;
}

.form-section {
  animation: slideInUp 0.6s ease-out;
}

/* Enhanced reference badge styling */
.ref-badge {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.ref-badge::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.ref-badge:hover::before {
  left: 100%;
}

.ref-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Professional input field enhancements with design system */
.field {
  position: relative;
}

.field label {
  transition: all var(--transition-base);
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-family: var(--font-family-base);
}

.field label .required {
  color: var(--error);
  margin: 0 var(--spacing-xs);
}

.field:hover label {
  color: var(--primary);
}

/* Gradient definitions for different sections */
.form-section:nth-child(1) {
  --gradient-start: #10b981;
  --gradient-end: #059669;
}

.form-section:nth-child(2) {
  --gradient-start: #3b82f6;
  --gradient-end: #1d4ed8;
}

.form-section:nth-child(3) {
  --gradient-start: #10b981;
  --gradient-end: #059669;
}

.form-section:nth-child(4) {
  --gradient-start: #8b5cf6;
  --gradient-end: #7c3aed;
}

/* Icon enhancements */
.step-icon-wrap {
  transition: all 0.3s ease;
}

.step-icon-wrap:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 15px -3px rgba(255, 255, 255, 0.3);
}

/* Professional typography */
.section-title {
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.step-title {
  letter-spacing: -0.05em;
  line-height: 1.1;
}

/* Enhanced shadow system */
.shadow-professional {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.shadow-professional-lg {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
</style>
