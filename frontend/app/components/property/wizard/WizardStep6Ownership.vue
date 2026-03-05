<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-id-card text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Ownership Information</h2>
        <p class="step-subtitle">Owner details and legal ownership type</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Owner Identity -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-user text-indigo-600" /> Owner Details
        </h3>
        <div class="form-grid">
          <div class="field full-width">
            <label>Owner Full Name</label>
            <InputText v-model="form.owner_name" placeholder="e.g. Abebe Kebede" class="w-full" />
          </div>

          <div class="field">
            <label>Phone Number</label>
            <div class="phone-input">
              <span class="phone-prefix">+251</span>
              <InputText
                v-model="phoneLocal"
                placeholder="9X XXX XXXX"
                class="w-full"
                maxlength="10"
                @blur="formatPhone"
              />
            </div>
            <small v-if="phoneError" class="error-msg">{{ phoneError }}</small>
          </div>

          <div class="field">
            <label>Email Address</label>
            <InputText
              v-model="form.owner_email"
              type="email"
              placeholder="e.g. abebe@email.com"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- ID Details -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-credit-card text-indigo-600" /> Identification
        </h3>
        <div class="form-grid">
          <div class="field">
            <label>ID Type</label>
            <Dropdown
              v-model="form.owner_id_type"
              :options="idTypes"
              optionLabel="label"
              optionValue="value"
              placeholder="Select ID type"
              class="w-full"
            />
          </div>
          <div class="field">
            <label>ID Number</label>
            <InputText
              v-model="form.owner_id_number"
              :placeholder="idPlaceholder"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- Ownership Type -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-building text-indigo-600" /> Ownership Type
        </h3>
        <div class="ownership-cards">
          <button
            v-for="ot in ownershipTypes"
            :key="ot.value"
            class="ownership-card"
            :class="{ selected: form.ownership_type === ot.value }"
            type="button"
            @click="form.ownership_type = ot.value"
          >
            <i :class="ot.icon" class="ow-icon" />
            <strong>{{ ot.label }}</strong>
            <span class="ow-desc">{{ ot.desc }}</span>
          </button>
        </div>
      </section>

      <!-- Legal Description -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-file-edit text-indigo-600" /> Legal Description
        </h3>
        <Textarea
          v-model="form.legal_description"
          :rows="4"
          placeholder="Describe any legal encumbrances, easements, covenants, or special conditions..."
          class="w-full"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePropertyWizardStore } from '~/stores/propertyWizard'

const store = usePropertyWizardStore()
const form = store.formData
const phoneError = ref('')

// Strip +251 prefix for local display
const phoneLocal = ref(
  form.owner_phone?.startsWith('+251') ? form.owner_phone.slice(4) : (form.owner_phone || '')
)

watch(phoneLocal, (val) => {
  phoneError.value = ''
  // Strip all non-digits and cap at 9 chars before writing to store
  const digits = val.replace(/\D/g, '').slice(0, 9)
  form.owner_phone = digits ? `+251${digits}` : ''
})

function formatPhone() {
  const stripped = phoneLocal.value.replace(/\D/g, '')
  if (stripped && !stripped.startsWith('9')) {
    phoneError.value = 'Ethiopian number should start with 9'
  } else if (stripped.length > 0 && stripped.length !== 9) {
    phoneError.value = 'Number should be 9 digits after +251'
  } else {
    phoneError.value = ''
  }
}

const idTypes = [
  { label: 'National ID (Fayda)', value: 'national_id' },
  { label: 'Passport', value: 'passport' },
  { label: 'Kebele ID', value: 'kebele_id' },
  { label: 'Driver\'s License', value: 'drivers_license' },
  { label: 'Business Registration', value: 'business_reg' },
]

const idPlaceholder = computed(() => {
  const map: Record<string, string> = {
    national_id: 'e.g. FYD-0000001234',
    passport: 'e.g. EP123456',
    kebele_id: 'e.g. AA/BOLE/001234',
    drivers_license: 'e.g. DL-ETH-001234',
    business_reg: 'e.g. AA-REG-001234',
  }
  return map[form.owner_id_type] || 'Enter ID number'
})

const ownershipTypes = [
  { value: 'private', label: 'Private', icon: 'pi pi-user', desc: 'Individual owner' },
  { value: 'joint_venture', label: 'Joint Venture', icon: 'pi pi-users', desc: 'Co-owned property' },
  { value: 'corporate', label: 'Corporate', icon: 'pi pi-building', desc: 'Company owned' },
  { value: 'government', label: 'Government', icon: 'pi pi-globe', desc: 'State owned' },
  { value: 'trust', label: 'Trust / Estate', icon: 'pi pi-shield', desc: 'Trust or estate' },
]
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}
.step-icon-wrap {
  width: 48px; height: 48px;
  background: rgba(255,255,255,0.2); border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.2rem; }
.step-subtitle { font-size: 0.875rem; opacity: 0.85; margin: 0; }

.step-body { padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }

.form-section { display: flex; flex-direction: column; gap: 1rem; }
.section-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.95rem; font-weight: 600; color: #334155;
  padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field.full-width { grid-column: 1 / -1; }
.field label { font-size: 0.8rem; font-weight: 600; color: #475569; }
.error-msg { color: #dc2626; font-size: 0.75rem; }

.phone-input { display: flex; align-items: center; gap: 0; }
.phone-prefix {
  padding: 0.65rem 0.75rem;
  background: #f1f5f9; border: 1px solid #e2e8f0;
  border-right: none; border-radius: 6px 0 0 6px;
  font-size: 0.875rem; font-weight: 600; color: #475569;
  white-space: nowrap;
}
.phone-input .p-inputtext { border-radius: 0 6px 6px 0; }

.ownership-cards { display: flex; flex-wrap: wrap; gap: 0.75rem; }
.ownership-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
  padding: 0.85rem 1rem; min-width: 120px;
  border: 2px solid #e2e8f0; border-radius: 12px;
  background: white; cursor: pointer; transition: all 0.2s;
  font-size: 0.8rem; color: #64748b; text-align: center;
}
.ownership-card:hover { border-color: #4f46e5; color: #4f46e5; }
.ownership-card.selected { border-color: #4f46e5; background: #eef2ff; color: #3730a3; font-weight: 600; }
.ow-icon { font-size: 1.3rem; }
.ow-desc { font-size: 0.7rem; color: #94a3b8; font-weight: 400; }

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .form-grid { grid-template-columns: 1fr; }
  .ownership-cards { gap: 0.5rem; }
  .ownership-card { min-width: 100px; padding: 0.6rem; }
}
</style>
