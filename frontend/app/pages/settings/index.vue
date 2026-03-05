<template>
  <div class="settings-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Settings</h1>
        <p>Configure system settings, preferences, and platform configurations</p>
      </div>
    </div>

    <!-- Settings Navigation -->
    <div class="settings-nav">
      <div class="nav-tabs">
        <button 
          v-for="tab in settingsTabs" 
          :key="tab.id"
          class="nav-tab"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Settings Content -->
    <div class="settings-content">
      <!-- General Settings -->
      <GeneralSettings v-if="activeTab === 'general'" />

      <!-- Valuation Settings -->
      <div v-if="activeTab === 'valuation'" class="settings-section">
        <div class="section-header">
          <h2>Valuation Settings</h2>
          <p>Property valuation methods and calculation parameters</p>
        </div>
        <div class="coming-soon">
          <i class="pi pi-info-circle"></i>
          <span>Valuation settings coming soon...</span>
        </div>
      </div>

      <!-- Notification Settings -->
      <div v-if="activeTab === 'notifications'" class="settings-section">
        <div class="section-header">
          <h2>Notification Settings</h2>
          <p>Configure system notifications and alerts</p>
        </div>
        <div class="coming-soon">
          <i class="pi pi-info-circle"></i>
          <span>Notification settings coming soon...</span>
        </div>
      </div>

      <!-- Security Settings -->
      <div v-if="activeTab === 'security'" class="settings-section">
        <div class="section-header">
          <h2>Security Settings</h2>
          <p>Security policies and access control</p>
        </div>
        <div class="coming-soon">
          <i class="pi pi-info-circle"></i>
          <span>Security settings coming soon...</span>
        </div>
      </div>

      <!-- Backup Settings -->
      <div v-if="activeTab === 'backup'" class="settings-section">
        <div class="section-header">
          <h2>Backup Settings</h2>
          <p>Data backup and recovery configuration</p>
        </div>
        <div class="coming-soon">
          <i class="pi pi-info-circle"></i>
          <span>Backup settings coming soon...</span>
        </div>
      </div>

      <!-- API Settings -->
      <div v-if="activeTab === 'api'" class="settings-section">
        <div class="section-header">
          <h2>API Settings</h2>
          <p>API configuration and integration settings</p>
        </div>
        <div class="coming-soon">
          <i class="pi pi-info-circle"></i>
          <span>API settings coming soon...</span>
        </div>
      </div>
      
      <!-- Web Scraper Settings -->
      <ScraperManagement v-if="activeTab === 'scraper'" />
    </div>

    <!-- Save Status -->
    <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
      <i :class="saveStatus.icon"></i>
      <span>{{ saveStatus.message }}</span>
    </div>
    
    <!-- Notification Toast -->
    <NotificationToast 
      v-for="notification in notifications" 
      :key="notification.id"
      :notification="notification"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GeneralSettings from '~/components/settings/GeneralSettings.vue'
import ScraperManagement from '~/components/settings/ScraperManagement.vue'
import NotificationToast from '~/components/ui/NotificationToast.vue'
import { useNotifications } from '~/composables/useNotifications.js'

// Reactive data
const activeTab = ref('general')
const isSaving = ref(false)
const saveStatus = ref(null)

// Notifications
const { notifications } = useNotifications()

const settingsTabs = [
  { id: 'general', label: 'General', icon: 'pi pi-cog' },
  { id: 'valuation', label: 'Valuation', icon: 'pi pi-calculator' },
  { id: 'notifications', label: 'Notifications', icon: 'pi pi-envelope' },
  { id: 'security', label: 'Security', icon: 'pi pi-shield' },
  { id: 'backup', label: 'Backup', icon: 'pi pi-database' },
  { id: 'api', label: 'API', icon: 'pi pi-code' },
  { id: 'scraper', label: 'Web Scraper', icon: 'pi pi-globe' }
]

const settings = ref({
  general: {
    platform_name: 'ValuAdis',
    platform_description: 'Ethiopian Property Valuation Platform',
    organization_name: 'Ethiopian Valuation Authority',
    contact_email: 'info@valuadis.gov.et',
    default_language: 'en',
    timezone: 'Africa/Addis_Ababa',
    date_format: 'DD/MM/YYYY',
    currency: 'ETB'
  },
  valuation: {
    default_method: 'comparative',
    market_adjustment_factor: 5.0,
    depreciation_rate: 2.5,
    min_property_value: 10000,
    proclamation_compliance: true,
    validity_period: 365,
    required_docs: {
      title_deed: true,
      tax_clearance: true,
      land_use_permit: true,
      building_permit: false
    }
  },
  notifications: {
    email_enabled: true,
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    types: {
      valuation_completed: true,
      user_registration: true,
      system_alerts: true,
      backup_completed: true
    }
  },
  security: {
    min_password_length: 8,
    require_uppercase: true,
    require_numbers: true,
    require_special_chars: true,
    password_expiry: 90,
    session_timeout: 120,
    max_concurrent_sessions: 3,
    enable_2fa: false,
    login_attempts: 5,
    lockout_duration: 30
  },
  backup: {
    enabled: true,
    frequency: 'daily',
    time: '02:00',
    retention: 30,
    storage: {
      location: 'both',
      provider: 'aws'
    },
    encryption: true,
    compression: true
  },
  api: {
    base_url: 'http://localhost:8020/api',
    version: 'v1',
    rate_limit: 100,
    enable_docs: true,
    integrations: {
      box: true,
      sacra: false,
      caplight: false,
      pitchbook: false
    }
  }
})


// Methods
// Settings endpoint not implemented yet
/*
async function loadSettings() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/settings`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      if (data.data) {
        settings.value = { ...settings.value, ...data.data }
      }
    } else {
      console.error('Failed to load settings from API')
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  }
}
*/

/*
async function saveAllSettings() {
  isSaving.value = true
  saveStatus.value = null

  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(settings.value)
    })

    if (response.ok) {
      saveStatus.value = {
        type: 'success',
        icon: 'pi pi-check-circle',
        message: 'Settings saved successfully!'
      }
    } else {
      const error = await response.json()
      saveStatus.value = {
        type: 'error',
        icon: 'pi pi-exclamation-circle',
        message: error.detail || 'Failed to save settings'
      }
    }
  } catch (error) {
    console.error('Error saving settings:', error)
    saveStatus.value = {
      type: 'error',
      icon: 'pi pi-exclamation-circle',
      message: 'Network error. Please try again.'
    }
  } finally {
    isSaving.value = false
    setTimeout(() => {
      saveStatus.value = null
    }, 5000)
  }
}
*/

function exportSettings() {
  const dataStr = JSON.stringify(settings.value, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `valuadis-settings-${new Date().toISOString().split('T')[0]}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

onMounted(() => {
  // Settings page mounted - components handle their own data loading
})
</script>

<style scoped>
/* Settings Container */
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

/* Page Header */
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

.header-actions {
  display: flex;
  gap: 1rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button.primary {
  background: white;
  color: #059669;
}

.action-button.primary:hover {
  background: #f8fafc;
  transform: translateY(-2px);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Settings Navigation */
.settings-nav {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
  overflow: hidden;
}

.nav-tabs {
  display: flex;
  overflow-x: auto;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border: none;
  background: none;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
}

.nav-tab:hover {
  color: #059669;
  background: #f8fafc;
}

.nav-tab.active {
  color: #059669;
  border-bottom-color: #059669;
  background: #f0fdf4;
}

/* Settings Content */
.settings-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.settings-section {
  padding: 2rem;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.section-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.setting-group {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
}

.setting-group h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.form-field {
  margin-bottom: 1.5rem;
}

.form-field:last-child {
  margin-bottom: 0;
}

.form-field label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
  transition: all 0.2s;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.form-field textarea {
  resize: vertical;
  min-height: 80px;
}

/* Switch Toggle */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  margin-left: 0.5rem;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #059669;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

/* Checkbox Group */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.checkbox-item input[type="checkbox"] {
  width: auto;
  margin: 0;
  accent-color: #059669;
}

/* Save Status */
.save-status {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.save-status.success {
  background: #bbf7d0;
  color: #059669;
}

.save-status.error {
  background: #fee2e2;
  color: #991b1b;
}

/* Scraper Actions */
.scraper-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .nav-tabs {
    flex-direction: column;
  }
  
  .nav-tab {
    border-bottom: none;
    border-right: 3px solid transparent;
  }
  
  .nav-tab.active {
    border-right-color: #059669;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .save-status {
    bottom: 1rem;
    right: 1rem;
    left: 1rem;
  }
}
</style>
