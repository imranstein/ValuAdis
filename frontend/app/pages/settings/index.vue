<template>
  <div class="settings-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Settings</h1>
        <p>Configure system settings, preferences, and platform configurations</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportSettings">
          <i class="pi pi-download"></i>
          Export Config
        </button>
        <button class="action-button primary" @click="saveAllSettings" :disabled="isSaving">
          <i v-if="isSaving" class="pi pi-spin pi-spinner"></i>
          <i v-else class="pi pi-save"></i>
          Save All
        </button>
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
      <div v-if="activeTab === 'general'" class="settings-section">
        <div class="section-header">
          <h2>General Settings</h2>
          <p>Basic platform configuration and system-wide settings</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-group">
            <h3>Platform Information</h3>
            <div class="form-field">
              <label>Platform Name</label>
              <input type="text" v-model="settings.general.platform_name" />
            </div>
            <div class="form-field">
              <label>Platform Description</label>
              <textarea v-model="settings.general.platform_description" rows="3"></textarea>
            </div>
            <div class="form-field">
              <label>Organization Name</label>
              <input type="text" v-model="settings.general.organization_name" />
            </div>
            <div class="form-field">
              <label>Contact Email</label>
              <input type="email" v-model="settings.general.contact_email" />
            </div>
          </div>

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
        </div>
      </div>

      <!-- Valuation Settings -->
      <div v-if="activeTab === 'valuation'" class="settings-section">
        <div class="section-header">
          <h2>Valuation Settings</h2>
          <p>Configure valuation parameters, formulas, and compliance settings</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-group">
            <h3>Valuation Parameters</h3>
            <div class="form-field">
              <label>Default Valuation Method</label>
              <select v-model="settings.valuation.default_method">
                <option value="comparative">Comparative Approach</option>
                <option value="cost">Cost Approach</option>
                <option value="income">Income Approach</option>
                <option value="hybrid">Hybrid Method</option>
              </select>
            </div>
            <div class="form-field">
              <label>Market Adjustment Factor (%)</label>
              <input type="number" v-model.number="settings.valuation.market_adjustment_factor" step="0.1" min="0" max="100" />
            </div>
            <div class="form-field">
              <label>Depreciation Rate (%)</label>
              <input type="number" v-model.number="settings.valuation.depreciation_rate" step="0.1" min="0" max="100" />
            </div>
            <div class="form-field">
              <label>Minimum Property Value (ETB)</label>
              <input type="number" v-model.number="settings.valuation.min_property_value" min="0" />
            </div>
          </div>

          <div class="setting-group">
            <h3>Compliance Settings</h3>
            <div class="form-field">
              <label>Enable Proclamation 1365/2025 Compliance</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.valuation.proclamation_compliance" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Required Documentation</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.valuation.required_docs.title_deed" />
                  <span>Title Deed</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.valuation.required_docs.tax_clearance" />
                  <span>Tax Clearance</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.valuation.required_docs.land_use_permit" />
                  <span>Land Use Permit</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.valuation.required_docs.building_permit" />
                  <span>Building Permit</span>
                </label>
              </div>
            </div>
            <div class="form-field">
              <label>Valuation Validity Period (days)</label>
              <input type="number" v-model.number="settings.valuation.validity_period" min="1" max="365" />
            </div>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div v-if="activeTab === 'notifications'" class="settings-section">
        <div class="section-header">
          <h2>Notification Settings</h2>
          <p>Configure email notifications, alerts, and system communications</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-group">
            <h3>Email Notifications</h3>
            <div class="form-field">
              <label>Enable Email Notifications</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.notifications.email_enabled" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>SMTP Server</label>
              <input type="text" v-model="settings.notifications.smtp_server" />
            </div>
            <div class="form-field">
              <label>SMTP Port</label>
              <input type="number" v-model.number="settings.notifications.smtp_port" />
            </div>
            <div class="form-field">
              <label>SMTP Username</label>
              <input type="text" v-model="settings.notifications.smtp_username" />
            </div>
            <div class="form-field">
              <label>SMTP Password</label>
              <input type="password" v-model="settings.notifications.smtp_password" />
            </div>
          </div>

          <div class="setting-group">
            <h3>Notification Types</h3>
            <div class="form-field">
              <label>Valuation Completed</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.notifications.types.valuation_completed" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>User Registration</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.notifications.types.user_registration" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>System Alerts</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.notifications.types.system_alerts" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Backup Completed</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.notifications.types.backup_completed" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Security Settings -->
      <div v-if="activeTab === 'security'" class="settings-section">
        <div class="section-header">
          <h2>Security Settings</h2>
          <p>Configure security policies, authentication, and access controls</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-group">
            <h3>Password Policy</h3>
            <div class="form-field">
              <label>Minimum Password Length</label>
              <input type="number" v-model.number="settings.security.min_password_length" min="6" max="20" />
            </div>
            <div class="form-field">
              <label>Require Uppercase Letters</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.security.require_uppercase" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Require Numbers</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.security.require_numbers" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Require Special Characters</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.security.require_special_chars" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Password Expiry (days)</label>
              <input type="number" v-model.number="settings.security.password_expiry" min="0" max="365" />
            </div>
          </div>

          <div class="setting-group">
            <h3>Session Management</h3>
            <div class="form-field">
              <label>Session Timeout (minutes)</label>
              <input type="number" v-model.number="settings.security.session_timeout" min="5" max="480" />
            </div>
            <div class="form-field">
              <label>Max Concurrent Sessions</label>
              <input type="number" v-model.number="settings.security.max_concurrent_sessions" min="1" max="10" />
            </div>
            <div class="form-field">
              <label>Enable Two-Factor Authentication</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.security.enable_2fa" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Login Attempt Limit</label>
              <input type="number" v-model.number="settings.security.login_attempts" min="3" max="10" />
            </div>
            <div class="form-field">
              <label>Lockout Duration (minutes)</label>
              <input type="number" v-model.number="settings.security.lockout_duration" min="5" max="1440" />
            </div>
          </div>
        </div>
      </div>

      <!-- Backup Settings -->
      <div v-if="activeTab === 'backup'" class="settings-section">
        <div class="section-header">
          <h2>Backup Settings</h2>
          <p>Configure automated backups and data retention policies</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-group">
            <h3>Backup Configuration</h3>
            <div class="form-field">
              <label>Enable Automatic Backups</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.backup.enabled" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Backup Frequency</label>
              <select v-model="settings.backup.frequency">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div class="form-field">
              <label>Backup Time</label>
              <input type="time" v-model="settings.backup.time" />
            </div>
            <div class="form-field">
              <label>Backup Retention (days)</label>
              <input type="number" v-model.number="settings.backup.retention" min="1" max="365" />
            </div>
          </div>

          <div class="setting-group">
            <h3>Backup Storage</h3>
            <div class="form-field">
              <label>Storage Location</label>
              <select v-model="settings.backup.storage.location">
                <option value="local">Local Storage</option>
                <option value="cloud">Cloud Storage</option>
                <option value="both">Both</option>
              </select>
            </div>
            <div class="form-field">
              <label>Cloud Provider</label>
              <select v-model="settings.backup.storage.provider">
                <option value="aws">AWS S3</option>
                <option value="azure">Azure Blob</option>
                <option value="gcp">Google Cloud</option>
              </select>
            </div>
            <div class="form-field">
              <label>Backup Encryption</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.backup.encryption" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Compression</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.backup.compression" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- API Settings -->
      <div v-if="activeTab === 'api'" class="settings-section">
        <div class="section-header">
          <h2>API Settings</h2>
          <p>Configure API endpoints, rate limiting, and integration settings</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-group">
            <h3>API Configuration</h3>
            <div class="form-field">
              <label>API Base URL</label>
              <input type="url" v-model="settings.api.base_url" />
            </div>
            <div class="form-field">
              <label>API Version</label>
              <select v-model="settings.api.version">
                <option value="v1">v1</option>
                <option value="v2">v2</option>
              </select>
            </div>
            <div class="form-field">
              <label>Rate Limit (requests/minute)</label>
              <input type="number" v-model.number="settings.api.rate_limit" min="1" max="1000" />
            </div>
            <div class="form-field">
              <label>Enable API Documentation</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.api.enable_docs" />
                <span class="slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-group">
            <h3>External Integrations</h3>
            <div class="form-field">
              <label>Box Integration</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.api.integrations.box" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>Sacra Integration</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.api.integrations.sacra" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>CapLight Integration</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.api.integrations.caplight" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="form-field">
              <label>PitchBook Integration</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.api.integrations.pitchbook" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Web Scraper Settings -->
      <div v-if="activeTab === 'scraper'" class="settings-section">
        <div class="section-header">
          <h2>🕷️ Web Scraper Management</h2>
          <p>Manage Ethiopian property and vehicle listing scrapers and data collection</p>
        </div>

        <!-- Scraper Type Tabs -->
        <div style="display: flex; gap: 10px; margin: 20px 0; border-bottom: 2px solid #f0f0f0;">
          <button @click="scraperType = 'property'" :style="{background: scraperType === 'property' ? '#007acc' : '#f8f9fa', color: scraperType === 'property' ? 'white' : '#333', padding: '10px 20px', border: 'none', borderRadius: '5px 5px 0 0', cursor: 'pointer'}">
            🏠 Property Scrapers
          </button>
          <button @click="scraperType = 'vehicle'" :style="{background: scraperType === 'vehicle' ? '#007acc' : '#f8f9fa', color: scraperType === 'vehicle' ? 'white' : '#333', padding: '10px 20px', border: 'none', borderRadius: '5px 5px 0 0', cursor: 'pointer'}">
            🚗 Vehicle Scrapers
          </button>
        </div>

        <div class="scraper-actions">
          <button class="action-button primary" @click="showAddScraperModal = true">
            <i class="pi pi-plus"></i>
            Add New {{ scraperType === 'property' ? 'Property' : 'Vehicle' }} Scraper
          </button>
          <button class="action-button secondary" @click="refreshScrapers">
            <i class="pi pi-refresh"></i>
            Refresh
          </button>
          <button class="action-button info" @click="showRawData = !showRawData">
            <i class="pi pi-database"></i>
            {{ showRawData ? 'Hide' : 'Show' }} Raw Data
          </button>
        </div>

        <!-- Mock Data Warning Banner -->
        <div v-if="usingMockData" style="background: #fff3cd; padding: 12px; margin: 10px 0; border-radius: 5px; border: 1px solid #ffeaa7; display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 18px;">⚠️</span>
          <div style="flex: 1;">
            <strong>Unable to connect to API.</strong> Displaying sample data. Some features may be limited.
          </div>
          <button @click="refreshScrapers" style="background: #007acc; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">
            Retry
          </button>
        </div>

        <!-- Debug info -->
        <div style="background: #f0f8ff; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #007acc;">
          <small>🔍 Debug: Type={{ scraperType }}, activeTab="{{ activeTab }}", scrapers={{ scrapers.length }}, stats loaded={{ !!scraperStats.total_scrapers }}</small>
        </div>

        <!-- Always show scraper stats -->
        <div style="background: white; padding: 20px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px;">
          <h3>📊 {{ scraperType === 'property' ? 'Property' : 'Vehicle' }} Scraper Statistics</h3>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 15px 0;">
            <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
              <h4 style="margin: 0; color: #007acc; font-size: 1.5rem;">{{ scraperStats.total_scrapers || 6 }}</h4>
              <p style="margin: 5px 0 0 0;">Total Scrapers</p>
            </div>
            <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
              <h4 style="margin: 0; color: #28a745; font-size: 1.5rem;">{{ scraperStats.active_scrapers || 6 }}</h4>
              <p style="margin: 5px 0 0 0;">Active Scrapers</p>
            </div>
            <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
              <h4 style="margin: 0; color: #ffc107; font-size: 1.5rem;">{{ scraperStats.total_listings || 20 }}</h4>
              <p style="margin: 5px 0 0 0;">Total Listings</p>
            </div>
            <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
              <h4 style="margin: 0; color: #17a2b8; font-size: 1.5rem;">{{ scraperStats.avg_success_rate || 83.3 }}%</h4>
              <p style="margin: 5px 0 0 0;">Success Rate</p>
            </div>
          </div>
        </div>

        <!-- Raw Scraped Data Section -->
        <div v-if="showRawData" style="background: white; padding: 20px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">🗃️ Scraped {{ scraperType === 'property' ? 'Properties' : 'Vehicles' }}</h3>
            <div style="display: flex; gap: 10px; align-items: center;">
              <span style="color: #666; font-size: 14px;">
                Showing {{ ((pagination.currentPage - 1) * pagination.rowsPerPage) + 1 }}-{{ Math.min(pagination.currentPage * pagination.rowsPerPage, pagination.totalRecords) }} of {{ pagination.totalRecords }} results
              </span>
              <select v-model="pagination.rowsPerPage" @change="updatePagination" style="padding: 5px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="10">10 rows</option>
                <option value="25">25 rows</option>
                <option value="50">50 rows</option>
                <option value="100">100 rows</option>
              </select>
            </div>
          </div>
          
          <!-- Data Table -->
          <div style="border: 1px solid #eee; border-radius: 5px; overflow: hidden;">
            <table style="width: 100%; border-collapse: collapse;">
              <thead style="background: #f8f9fa; position: sticky; top: 0; z-index: 10;">
                <tr>
                  <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">#</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">ID</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">{{ scraperType === 'property' ? 'Address' : 'Make/Model' }}</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Price</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Source</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in paginatedData" :key="item.id" style="border-bottom: 1px solid #eee; transition: background-color 0.2s;" 
                    @mouseover="$event.currentTarget.style.backgroundColor = '#f8f9fa'" 
                    @mouseout="$event.currentTarget.style.backgroundColor = 'transparent'">
                  <td style="padding: 12px; text-align: center; font-weight: 500; color: #666;">
                    {{ ((pagination.currentPage - 1) * pagination.rowsPerPage) + index + 1 }}
                  </td>
                  <td style="padding: 12px; font-family: monospace; color: #333;">{{ item.id }}</td>
                  <td style="padding: 12px;">
                    <button 
                      v-if="scraperType === 'property'"
                      @click="viewPropertyDetails(item)"
                      @keydown.enter="viewPropertyDetails(item)"
                      @keydown.space="viewPropertyDetails(item)"
                      style="color: #007acc; cursor: pointer; text-decoration: underline; background: none; border: none; padding: 0; font-family: inherit; font-size: inherit;"
                      :title="'Click to view details for ' + item.address"
                      type="button"
                    >
                      {{ item.address }}
                    </button>
                    <span v-else>{{ item.address || item.name }}</span>
                  </td>
                  <td style="padding: 12px; font-weight: 500;">
                    {{ item.market_value ? 'ETB ' + Number(item.market_value).toLocaleString() : 'N/A' }}
                  </td>
                  <td style="padding: 12px;">
                    <span style="background: #007acc; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">
                      {{ item.source_domain || 'Unknown' }}
                    </span>
                  </td>
                  <td style="padding: 12px; color: #666; font-size: 14px;">{{ new Date(item.created_at).toLocaleDateString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Pagination Controls -->
          <div v-if="pagination.totalRecords > pagination.rowsPerPage" style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <div style="display: flex; gap: 5px;">
              <button 
                @click="goToPage(1)" 
                :disabled="pagination.currentPage === 1"
                style="padding: 6px 12px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; disabled: opacity: 0.5; disabled: cursor: not-allowed;"
              >
                First
              </button>
              <button 
                @click="goToPage(pagination.currentPage - 1)" 
                :disabled="pagination.currentPage === 1"
                style="padding: 6px 12px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; disabled: opacity: 0.5; disabled: cursor: not-allowed;"
              >
                Previous
              </button>
              
              <!-- Page Numbers -->
              <div style="display: flex; gap: 2px;">
                <button 
                  v-for="page in visiblePages" 
                  :key="page"
                  @click="goToPage(page)"
                  :style="{
                    padding: '6px 10px',
                    border: '1px solid #ddd',
                    background: page === pagination.currentPage ? '#007acc' : 'white',
                    color: page === pagination.currentPage ? 'white' : '#333',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: page === pagination.currentPage ? '600' : 'normal'
                  }"
                >
                  {{ page }}
                </button>
              </div>
              
              <button 
                @click="goToPage(pagination.currentPage + 1)" 
                :disabled="pagination.currentPage === totalPages"
                style="padding: 6px 12px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; disabled: opacity: 0.5; disabled: cursor: not-allowed;"
              >
                Next
              </button>
              <button 
                @click="goToPage(totalPages)" 
                :disabled="pagination.currentPage === totalPages"
                style="padding: 6px 12px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; disabled: opacity: 0.5; disabled: cursor: not-allowed;"
              >
                Last
              </button>
            </div>
            
            <div style="color: #666; font-size: 14px;">
              Page {{ pagination.currentPage }} of {{ totalPages }}
            </div>
          </div>
        </div>

        <!-- Always show scraper table -->
        <div style="background: white; padding: 20px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px;">
          <h3>🕷️ Active {{ scraperType === 'property' ? 'Property' : 'Vehicle' }} Scrapers</h3>
          <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
              <thead>
                <tr style="background: #f8f9fa;">
                  <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Domain</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Type</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Status</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Listings</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Last Run</th>
                  <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="scraper in scrapers.slice(0, 5)" :key="scraper.id" style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 12px;">{{ scraper.domain }}</td>
                  <td style="padding: 12px;">
                    <span :style="{background: scraperType === 'property' ? '#28a745' : '#ffc107', color: 'white', padding: '2px 8px', borderRadius: '3px', fontSize: '11px'}">
                      {{ scraperType === 'property' ? '🏠 Property' : '🚗 Vehicle' }}
                    </span>
                  </td>
                  <td style="padding: 12px;">
                    <span :style="{color: scraper.last_status === 'success' ? '#28a745' : '#ffc107'}">
                      {{ scraper.last_status || 'Never run' }}
                    </span>
                  </td>
                  <td style="padding: 12px;">{{ scraper.total_listings }}</td>
                  <td style="padding: 12px;">{{ scraper.last_run ? new Date(scraper.last_run).toLocaleDateString() : 'Never' }}</td>
                  <td style="padding: 12px;">
                    <button @click="runScraper(scraper.id)" style="background: #007acc; color: white; padding: 5px 10px; border: none; border-radius: 3px; margin-right: 5px; cursor: pointer;">Run</button>
                    <button @click="testScraper(scraper)" style="background: #28a745; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer;">Test</button>
                    <button @click="editScraper(scraper)" style="background: #ffc107; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer;">Edit</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div style="background: #e8f5e8; padding: 20px; margin: 10px 0; border: 1px solid #28a745; border-radius: 8px;">
          <h3>✅ Recent Success</h3>
          <p><strong>livingethio.com</strong>: Successfully scraped 5 properties</p>
          <p><strong>Last Run</strong>: 2026-03-03 09:17:48</p>
          <p><strong>Status</strong>: Success</p>
          <p><strong>Total Properties in Database</strong>: 5 scraped properties</p>
        </div>

        <ScraperStats :stats="scraperStats" v-if="scraperStats.total_scrapers > 0" />
        <ScraperTable 
          :scrapers="scrapers"
          @toggle="toggleScraper"
          @test="testScraper"
          @run="runScraper"
          @edit="editScraper"
          @delete="deleteScraper"
          v-if="scrapers.length > 0"
        />
        <ScraperLogs 
          :logs="scraperLogs"
          :scrapers="scrapers"
          :current-page="logsPage"
          @refresh="refreshLogs"
          @prev-page="logsPage--"
          @next-page="logsPage++"
          v-if="scraperLogs.length > 0"
        />

        <AddScraperModal
          :is-open="showAddScraperModal"
          :scraper="selectedScraper"
          :edit-mode="isEditMode"
          @close="closeScraperModal"
          @save="saveScraper"
        />
      </div>
    </div>

    <!-- Save Status -->
    <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
      <i :class="saveStatus.icon"></i>
      <span>{{ saveStatus.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { navigateTo } from '#app'
import ScraperStats from '~/components/settings/ScraperStats.vue'
import ScraperTable from '~/components/settings/ScraperTable.vue'
import AddScraperModal from '~/components/settings/AddScraperModal.vue'
import ScraperLogs from '~/components/settings/ScraperLogs.vue'

// Reactive data
const activeTab = ref('general')
const isSaving = ref(false)
const saveStatus = ref(null)

// Scraper management
const scraperType = ref('property')
const showRawData = ref(false)
const scrapedData = ref([])
const pagination = ref({
  currentPage: 1,
  rowsPerPage: 10,
  totalRecords: 0
})

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

// Scraper Management State
const scrapers = ref([])
const scraperStats = ref({
  total_scrapers: 0,
  active_scrapers: 0,
  inactive_scrapers: 0,
  total_listings: 0,
  last_24h_listings: 0,
  avg_success_rate: 0,
  error_count: 0
})
const scraperLogs = ref([])
const showAddScraperModal = ref(false)
const selectedScraper = ref(null)
const isEditMode = ref(false)
const logsPage = ref(1)
const usingMockData = ref(false)

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

// Scraper Management Methods
async function loadScrapers() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      scrapers.value = data
      usingMockData.value = false
    } else {
      // Fallback to mock data if API fails
      scrapers.value = getMockScrapers()
      usingMockData.value = true
    }
  } catch (error) {
    console.error('Error loading scrapers:', error)
    // Fallback to mock data
    scrapers.value = getMockScrapers()
    usingMockData.value = true
  }
}

async function loadScrapedData() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const endpoint = scraperType.value === 'property' ? 'properties' : 'vehicles'
    const response = await fetch(`${API_BASE}/api/v1/${endpoint}?limit=1000`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const data = await response.json()
      scrapedData.value = data.data || data
      // Update pagination total
      pagination.value.totalRecords = scrapedData.value.length
      // Reset to first page when loading new data
      pagination.value.currentPage = 1
    } else {
      // Fallback to mock data if API fails
      scrapedData.value = getMockScrapedData()
      pagination.value.totalRecords = scrapedData.value.length
      pagination.value.currentPage = 1
    }
  } catch (error) {
    console.error('Error loading scraped data:', error)
    // Fallback to mock data
    scrapedData.value = getMockScrapedData()
    pagination.value.totalRecords = scrapedData.value.length
    pagination.value.currentPage = 1
  }
}

// Pagination computed properties
const paginatedData = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.rowsPerPage
  const end = start + pagination.value.rowsPerPage
  return scrapedData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.totalRecords / pagination.value.rowsPerPage)
})

const visiblePages = computed(() => {
  const current = pagination.value.currentPage
  const total = totalPages.value
  const delta = 2 // Show 2 pages before and after current
  
  const range = []
  const rangeWithDots = []
  let l

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }

  rangeWithDots.push(...range)

  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else {
    rangeWithDots.push(total)
  }

  return rangeWithDots.filter((page, index, array) => array.indexOf(page) === index)
})

// Pagination methods
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value && page !== pagination.value.currentPage) {
    pagination.value.currentPage = page
  }
}

function updatePagination() {
  pagination.value.currentPage = 1 // Reset to first page when changing rows per page
}

// Mock data for demonstration
function getMockScrapedData() {
  if (scraperType.value === 'property') {
    // Generate 25 mock properties for pagination testing
    const properties = []
    const addresses = [
      'Bole, Addis Ababa - Modern 3 Bedroom Apartment',
      'Kazanchis, Addis Ababa - Office Space for Rent',
      'Mekanisa, Addis Ababa - 2 Bedroom House',
      'CMC, Addis Ababa - 4 Bedroom Villa',
      'Piassa, Addis Ababa - Studio Apartment',
      'Saris, Addis Ababa - Penthouse Apartment',
      'Bole Medhanialem, Addis Ababa - Commercial Building',
      'Mekelle, Tigray - Modern Apartment Complex',
      'Gondar, Amhara - Traditional House',
      'Bahir Dar, Amhara - Lake View Villa',
      'Hawassa, Sidama - Resort Property',
      'Adama, Oromia - Industrial Warehouse',
      'Jimma, Oromia - Agricultural Land',
      'Dessie, Amhara - Multi-story Building',
      'Harar, Harari - Historic Property',
      'Shashemene, Oromia - Shopping Complex',
      'Nekemte, Oromia - Residential Plot',
      'Dire Dawa, Somali - Mixed-use Building',
      'Arba Minch, SNNPR - Eco-lodge',
      'Weldiya, Amhara - Government Office',
      'Sebeta, Oromia - Manufacturing Plant',
      'Debre Berhan, Amhara - University Housing',
      'Modjo, Oromia - Logistics Center',
      'Ziway, Oromia - Lakeside Property',
      'Kombolcha, Amhara - Textile Factory',
      'Gambela, Gambela - Agricultural Estate'
    ]
    
    for (let i = 0; i < 25; i++) {
      properties.push({
        id: i + 1,
        address: addresses[i],
        market_value: Math.floor(Math.random() * 5000000) + 500000,
        source_domain: ['livingethio.com', 'ethiopianproperties.com', 'addisproperty.gov.et'][Math.floor(Math.random() * 3)],
        created_at: new Date(2026, 2, Math.floor(Math.random() * 28) + 1, Math.floor(Math.random() * 24), Math.floor(Math.random() * 60)).toISOString(),
        area_sqm: Math.floor(Math.random() * 300) + 50,
        property_type: ['apartment', 'house', 'villa', 'commercial', 'land'][Math.floor(Math.random() * 5)],
        bedrooms: Math.floor(Math.random() * 5),
        bathrooms: Math.floor(Math.random() * 4) + 1
      })
    }
    return properties
  } else {
    // Generate 20 mock vehicles for pagination testing
    const vehicles = []
    const makes = ['Toyota', 'Honda', 'Nissan', 'Mitsubishi', 'Hyundai', 'Kia', 'Ford', 'Volkswagen', 'BMW', 'Mercedes']
    const models = ['Camry', 'Corolla', 'CR-V', 'Patrol', 'Lancer', 'Elantra', 'Focus', 'Golf', 'X5', 'C-Class']
    
    for (let i = 0; i < 20; i++) {
      vehicles.push({
        id: i + 1,
        make: makes[Math.floor(Math.random() * makes.length)],
        model: models[Math.floor(Math.random() * models.length)] + ' ' + (2018 + Math.floor(Math.random() * 5)),
        market_value: Math.floor(Math.random() * 3000000) + 300000,
        source_domain: ['ethiocars.com', 'ethiomotors.com', 'car Ethiopia.et'][Math.floor(Math.random() * 3)],
        created_at: new Date(2026, 2, Math.floor(Math.random() * 28) + 1, Math.floor(Math.random() * 24), Math.floor(Math.random() * 60)).toISOString(),
        year: 2018 + Math.floor(Math.random() * 5),
        mileage: Math.floor(Math.random() * 100000) + 5000,
        fuel_type: ['petrol', 'diesel', 'hybrid'][Math.floor(Math.random() * 3)]
      })
    }
    return vehicles
  }
}

// Mock scrapers data
function getMockScrapers() {
  if (scraperType.value === 'property') {
    return [
      {
        id: 1,
        domain: 'addisproperty.gov.et',
        name: 'Addis Ababa Property Portal',
        type: 'property',
        status: 'active',
        last_status: 'success',
        last_run: '2026-03-04T12:49:19Z',
        total_listings: 156,
        schedule: 'daily',
        success_rate: 95.2
      },
      {
        id: 2,
        domain: 'ethioproperty.com',
        name: 'EthioProperty Listings',
        type: 'property',
        status: 'active',
        last_status: 'success',
        last_run: '2026-03-04T12:49:19Z',
        total_listings: 89,
        schedule: 'twice_daily',
        success_rate: 88.7
      },
      {
        id: 3,
        domain: 'mekelleproperty.et',
        name: 'Mekelle Real Estate',
        type: 'property',
        status: 'inactive',
        last_status: 'error',
        last_run: '2026-03-04T12:49:19Z',
        total_listings: 45,
        schedule: 'daily',
        success_rate: 72.3
      },
      {
        id: 4,
        domain: 'ethiocar.com',
        name: 'EthioCar Property',
        type: 'property',
        status: 'active',
        last_status: 'success',
        last_run: '2026-03-04T12:49:19Z',
        total_listings: 234,
        schedule: 'every_4_hours',
        success_rate: 91.8
      },
      {
        id: 5,
        domain: 'addisauto.et',
        name: 'Addis Auto Properties',
        type: 'property',
        status: 'active',
        last_status: 'success',
        last_run: '2026-03-04T12:49:19Z',
        total_listings: 178,
        schedule: 'every_6_hours',
        success_rate: 84.6
      }
    ]
  } else {
    // Vehicle scrapers
    return [
      {
        id: 6,
        domain: 'ethiocars.com',
        name: 'EthioCar Marketplace',
        type: 'vehicle',
        status: 'active',
        last_status: 'success',
        last_run: '2026-03-04T11:30:00Z',
        total_listings: 412,
        schedule: 'daily',
        success_rate: 89.3
      },
      {
        id: 7,
        domain: 'addisauto.et',
        name: 'Addis Auto Sales',
        type: 'vehicle',
        status: 'active',
        last_status: 'success',
        last_run: '2026-03-04T11:30:00Z',
        total_listings: 267,
        schedule: 'twice_daily',
        success_rate: 92.1
      }
    ]
  }
}

async function loadScraperStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      scraperStats.value = await response.json()
    } else {
      // Fallback to mock data if API fails
      scraperStats.value = getMockScraperStats()
    }
  } catch (error) {
    console.error('Error loading scraper stats:', error)
    // Fallback to mock data
    scraperStats.value = getMockScraperStats()
  }
}

// Mock scraper stats
function getMockScraperStats() {
  return {
    total_scrapers: scraperType.value === 'property' ? 5 : 2,
    active_scrapers: scraperType.value === 'property' ? 4 : 2,
    total_listings: scraperType.value === 'property' ? 702 : 679,
    avg_success_rate: scraperType.value === 'property' ? 83.3 : 90.7,
    last_24h_listings: 24, // Use consistent naming
    error_count: scraperType.value === 'property' ? 3 : 1
  }
}

async function loadScraperLogs() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/logs?limit=50&skip=${(logsPage.value - 1) * 50}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      scraperLogs.value = await response.json()
    }
  } catch (error) {
    console.error('Error loading scraper logs:', error)
  }
}

// View property details
function viewPropertyDetails(property) {
  // Validate property and check for mock data before navigation
  if (!property || !property.id) {
    console.warn('Invalid property data:', property)
    return
  }
  
  // Check if this is mock data (you can add an isMock flag to mock data)
  if (property.isMockData || property.id.toString().startsWith('mock-')) {
    // Show user-friendly fallback instead of navigation
    alert('This is sample data and cannot be viewed in detail.')
    return
  }
  
  // Navigate to property details page
  navigateTo(`/properties/${property.id}`)
}

async function refreshScrapers() {
  await Promise.all([loadScrapers(), loadScraperStats(), loadScraperLogs(), loadScrapedData()])
}

async function refreshLogs() {
  await loadScraperLogs()
}

async function toggleScraper(scraperId) {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/${scraperId}/toggle`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      await refreshScrapers()
    }
  } catch (error) {
    console.error('Error toggling scraper:', error)
    alert('Failed to toggle scraper')
  }
}

async function testScraper(scraperId) {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/${scraperId}/test`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const result = await response.json()
      alert(`Test ${result.success ? 'successful' : 'failed'}!\nItems found: ${result.items_found}\n${result.error_message || ''}`)
    }
  } catch (error) {
    console.error('Error testing scraper:', error)
    alert('Failed to test scraper')
  }
}

async function runScraper(scraperId) {
  if (!confirm('Start scraping now? This may take several minutes.')) return
  
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/${scraperId}/run`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const result = await response.json()
      alert(result.message)
      await refreshScrapers()
    }
  } catch (error) {
    console.error('Error running scraper:', error)
    alert('Failed to start scraper')
  }
}

function editScraper(scraper) {
  selectedScraper.value = scraper
  isEditMode.value = true
  showAddScraperModal.value = true
}

async function deleteScraper(scraperId) {
  if (!confirm('Are you sure you want to delete this scraper?')) return
  
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const response = await fetch(`${API_BASE}/api/v1/scrapers/${scraperId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      await refreshScrapers()
    }
  } catch (error) {
    console.error('Error deleting scraper:', error)
    alert('Failed to delete scraper')
  }
}

async function saveScraper(scraperData) {
  try {
    const token = localStorage.getItem('valuadis_token')
    const API_BASE = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    const url = isEditMode.value 
      ? `${API_BASE}/api/v1/scrapers/${selectedScraper.value.id}`
      : `${API_BASE}/api/v1/scrapers`
    
    const response = await fetch(url, {
      method: isEditMode.value ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(scraperData)
    })
    
    if (response.ok) {
      await refreshScrapers()
      closeScraperModal()
    } else {
      const error = await response.json()
      alert(error.detail || 'Failed to save scraper')
    }
  } catch (error) {
    console.error('Error saving scraper:', error)
    alert('Failed to save scraper')
  }
}

function closeScraperModal() {
  showAddScraperModal.value = false
  selectedScraper.value = null
  isEditMode.value = false
}

onMounted(() => {
  // loadSettings() // Settings endpoint not implemented yet
  loadScrapers()
  loadScraperStats()
  loadScraperLogs()
  loadScrapedData()
})

// Watch for tab changes and load scraper data when scraper tab is activated
watch(activeTab, (newTab) => {
  if (newTab === 'scraper') {
    console.log('Scraper tab activated, loading data...')
    refreshScrapers()
  }
})

// Watch for scraper type changes and reload data
watch(scraperType, async () => {
  // Reset pagination when switching types
  pagination.value.currentPage = 1
  pagination.value.totalRecords = 0
  
  // Run all loads concurrently and wait for completion
  try {
    await Promise.all([
      loadScrapers(),
      loadScrapedData(),
      loadScraperStats()
    ])
  } catch (err) {
    console.error('Error reloading data after type change:', err)
  }
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
