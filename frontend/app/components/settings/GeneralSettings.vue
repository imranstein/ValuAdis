<template>
  <div class="general-settings">
    <div class="section-header">
      <h2>General Settings</h2>
      <p>Basic platform configuration and system-wide settings</p>
    </div>
    
    <div class="settings-grid">
      <!-- Platform Information -->
      <div class="setting-group">
        <h3>Platform Information</h3>
        <div class="form-field">
          <label>Platform Name</label>
          <input v-model="settings.general.platform_name" type="text" />
        </div>
        <div class="form-field">
          <label>Platform Description</label>
          <textarea v-model="settings.general.platform_description" rows="3"></textarea>
        </div>
        <div class="form-field">
          <label>Organization Name</label>
          <input v-model="settings.general.organization_name" type="text" />
        </div>
        <div class="form-field">
          <label>Contact Email</label>
          <input v-model="settings.general.contact_email" type="email" />
        </div>
      </div>

      <!-- System Configuration -->
      <div class="setting-group">
        <h3>System Configuration</h3>
        <div class="form-field">
          <label>Default Language</label>
          <select v-model="settings.general.default_language">
            <option value="en">English</option>
            <option value="am">Amharic</option>
            <option value="om">Oromo</option>
            <option value="ti">Tigrinya</option>
          </select>
        </div>
        <div class="form-field">
          <label>Timezone</label>
          <select v-model="settings.general.timezone">
            <option value="Africa/Addis_Ababa">Addis Ababa (EAT)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>
        <div class="form-field">
          <label>Date Format</label>
          <select v-model="settings.general.date_format">
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
          </select>
        </div>
        <div class="form-field">
          <label>Currency</label>
          <select v-model="settings.general.currency">
            <option value="ETB">Ethiopian Birr (ETB)</option>
            <option value="USD">US Dollar (USD)</option>
          </select>
        </div>
      </div>

      <!-- Display Settings -->
      <div class="setting-group">
        <h3>Display Settings</h3>
        <div class="form-field">
          <label>Items Per Page</label>
          <input v-model.number="settings.display.items_per_page" type="number" min="10" max="100" />
        </div>
        <div class="form-field">
          <label>Theme</label>
          <select v-model="settings.display.theme">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
        <div class="form-field">
          <label>
            <input v-model="settings.display.show_tooltips" type="checkbox" />
            Show Tooltips
          </label>
        </div>
        <div class="form-field">
          <label>
            <input v-model="settings.display.enable_animations" type="checkbox" />
            Enable Animations
          </label>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="setting-group">
        <h3>Notification Settings</h3>
        <div class="form-field">
          <label>
            <input v-model="settings.notifications.email_enabled" type="checkbox" />
            Email Notifications
          </label>
        </div>
        <div class="form-field">
          <label>
            <input v-model="settings.notifications.browser_enabled" type="checkbox" />
            Browser Notifications
          </label>
        </div>
        <div class="form-field">
          <label>Notification Frequency</label>
          <select v-model="settings.notifications.frequency">
            <option value="immediate">Immediate</option>
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="setting-group">
        <h3>Security Settings</h3>
        <div class="form-field">
          <label>Session Timeout (minutes)</label>
          <input v-model.number="settings.security.session_timeout" type="number" min="15" max="1440" />
        </div>
        <div class="form-field">
          <label>
            <input v-model="settings.security.require_2fa" type="checkbox" />
            Require Two-Factor Authentication
          </label>
        </div>
        <div class="form-field">
          <label>Password Policy</label>
          <select v-model="settings.security.password_policy">
            <option value="basic">Basic (8+ chars)</option>
            <option value="medium">Medium (8+ chars, mixed case)</option>
            <option value="strong">Strong (12+ chars, symbols)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="settings-actions">
      <button @click="resetToDefaults" class="btn-secondary">
        <i class="pi pi-undo"></i>
        Reset to Defaults
      </button>
      <button @click="exportSettings" class="btn-secondary">
        <i class="pi pi-download"></i>
        Export Config
      </button>
      <button @click="importSettings" class="btn-secondary">
        <i class="pi pi-upload"></i>
        Import Config
      </button>
      <button @click="saveSettings" class="btn-primary" :disabled="isSaving">
        <i v-if="isSaving" class="pi pi-spin pi-spinner"></i>
        <i v-else class="pi pi-save"></i>
        Save Changes
      </button>
    </div>

    <!-- Save Status -->
    <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
      <i :class="saveStatus.icon"></i>
      <span>{{ saveStatus.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useNotifications } from '~/composables/useNotifications.js'

// Reactive data
const isSaving = ref(false)
const saveStatus = ref(null)

// Settings data
const settings = reactive({
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
  display: {
    items_per_page: 25,
    theme: 'light',
    show_tooltips: true,
    enable_animations: true
  },
  notifications: {
    email_enabled: true,
    browser_enabled: true,
    frequency: 'immediate'
  },
  security: {
    session_timeout: 120,
    require_2fa: false,
    password_policy: 'medium'
  }
})

// Notifications
const { success, error, warning, info } = useNotifications()

// Methods
const saveSettings = async () => {
  isSaving.value = true
  saveStatus.value = null

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Save to localStorage for demo
    localStorage.setItem('valuadis_settings', JSON.stringify(settings))
    
    saveStatus.value = {
      type: 'success',
      icon: 'pi pi-check',
      message: 'Settings saved successfully'
    }
    
    success('Settings saved successfully')
  } catch (err) {
    saveStatus.value = {
      type: 'error',
      icon: 'pi pi-times',
      message: 'Failed to save settings'
    }
    
    error('Failed to save settings')
  } finally {
    isSaving.value = false
    
    // Clear status after 5 seconds
    setTimeout(() => {
      saveStatus.value = null
    }, 5000)
  }
}

const resetToDefaults = () => {
  if (!confirm('Are you sure you want to reset all settings to defaults?')) return
  
  // Reset to default values
  settings.general.platform_name = 'ValuAdis'
  settings.general.platform_description = 'Ethiopian Property Valuation Platform'
  settings.general.organization_name = 'Ethiopian Valuation Authority'
  settings.general.contact_email = 'info@valuadis.gov.et'
  settings.general.default_language = 'en'
  settings.general.timezone = 'Africa/Addis_Ababa'
  settings.general.date_format = 'DD/MM/YYYY'
  settings.general.currency = 'ETB'
  
  settings.display.items_per_page = 25
  settings.display.theme = 'light'
  settings.display.show_tooltips = true
  settings.display.enable_animations = true
  
  settings.notifications.email_enabled = true
  settings.notifications.browser_enabled = true
  settings.notifications.frequency = 'immediate'
  
  settings.security.session_timeout = 120
  settings.security.require_2fa = false
  settings.security.password_policy = 'medium'
  
  warning('Settings reset to defaults')
}

const exportSettings = () => {
  try {
    const dataStr = JSON.stringify(settings, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `valuadis-settings-${new Date().toISOString().split('T')[0]}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
    
    success('Settings exported successfully')
  } catch (err) {
    error('Failed to export settings')
  }
}

const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  
  input.onchange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const importedSettings = JSON.parse(e.target.result)
        
        // Merge imported settings with current settings
        Object.assign(settings, importedSettings)
        
        success('Settings imported successfully')
      } catch (err) {
        error('Failed to import settings - Invalid file format')
      }
    }
    
    reader.readAsText(file)
  }
  
  input.click()
}

// Load settings from localStorage on mount
const loadSettings = () => {
  try {
    const saved = localStorage.getItem('valuadis_settings')
    if (saved) {
      const savedSettings = JSON.parse(saved)
      Object.assign(settings, savedSettings)
    }
  } catch (err) {
    console.warn('Failed to load settings from localStorage')
  }
}

// Initialize
loadSettings()
</script>

<style scoped>
.general-settings {
  padding: 20px;
}

.section-header {
  margin-bottom: 32px;
}

.section-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.section-header p {
  margin: 0;
  color: #666;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
  margin-bottom: 32px;
}

.setting-group {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.setting-group h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.form-field {
  margin-bottom: 20px;
}

.form-field:last-child {
  margin-bottom: 0;
}

.form-field label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
}

.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.settings-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 24px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 16px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 6px;
  font-weight: 500;
}

.save-status.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.save-status.error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
</style>
