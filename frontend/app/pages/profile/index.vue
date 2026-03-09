<template>
  <div class="profile-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>My Profile</h1>
        <p>Manage your account settings and personal information</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportProfileData">
          <i class="pi pi-download"></i>
          Export Data
        </button>
      </div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content">
      <div class="profile-grid">
        <!-- Profile Card -->
        <div class="profile-card">
          <div class="profile-header">
            <div class="profile-avatar">
              <div class="avatar-circle">
                {{ userInitials }}
              </div>
              <div class="avatar-info">
                <h2>{{ authStore.user?.full_name || 'User' }}</h2>
                <p class="role-badge">{{ roleDisplayName }}</p>
              </div>
            </div>
            <div class="profile-actions">
              <button class="btn-secondary" @click="showEditModal = true">
                <i class="pi pi-pencil"></i>
                Edit Profile
              </button>
            </div>
          </div>

          <div class="profile-details">
            <div class="detail-section">
              <h3>Contact Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Email</label>
                  <p>{{ authStore.user?.email || 'Not provided' }}</p>
                </div>
                <div class="detail-item">
                  <label>Phone</label>
                  <p>{{ formatPhone(authStore.user?.phone) || 'Not provided' }}</p>
                </div>
                <div class="detail-item">
                  <label>Municipality</label>
                  <p>{{ getMunicipalityLabel(authStore.user?.municipality) || 'Not assigned' }}</p>
                </div>
                <div class="detail-item">
                  <label>License Number</label>
                  <p>{{ authStore.user?.license_number || 'Not provided' }}</p>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Account Status</h3>
              <div class="status-grid">
                <div class="status-item">
                  <label>Account Status</label>
                  <span class="status-badge" :class="authStore.user?.is_active ? 'active' : 'inactive'">
                    {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div class="status-item">
                  <label>Verification Status</label>
                  <span class="status-badge" :class="authStore.user?.is_verified ? 'verified' : 'unverified'">
                    {{ authStore.user?.is_verified ? 'Verified' : 'Unverified' }}
                  </span>
                </div>
                <div class="status-item">
                  <label>Member Since</label>
                  <p>{{ formatDate(authStore.user?.created_at) }}</p>
                </div>
                <div class="status-item">
                  <label>Last Updated</label>
                  <p>{{ formatDate(authStore.user?.updated_at) }}</p>
                </div>
              </div>
            </div>

            <div class="detail-section" v-if="userPermissions.length > 0">
              <h3>Permissions</h3>
              <div class="permissions-list">
                <span v-for="permission in userPermissions.slice(0, 10)" :key="permission" class="permission-tag">
                  {{ formatPermissionName(permission) }}
                </span>
                <span v-if="userPermissions.length > 10" class="permission-more">
                  +{{ userPermissions.length - 10 }} more
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="security-card">
          <div class="card-header">
            <h3>🔐 Security Settings</h3>
          </div>
          <div class="security-actions">
            <button class="security-btn" @click="showPasswordModal = true">
              <i class="pi pi-key"></i>
              Change Password
            </button>
            <button class="security-btn" @click="show2FAModal = true">
              <i class="pi pi-shield"></i>
              Two-Factor Authentication
            </button>
            <button class="security-btn" @click="showSessionsModal = true">
              <i class="pi pi-history"></i>
              Active Sessions
            </button>
          </div>
        </div>

        <!-- Activity Summary -->
        <div class="activity-card">
          <div class="card-header">
            <h3>📊 Activity Summary</h3>
          </div>
          <div class="activity-stats">
            <div class="stat-item">
              <div class="stat-number">{{ totalValuations }}</div>
              <div class="stat-label">Valuations Completed</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ totalProperties }}</div>
              <div class="stat-label">Properties Assessed</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ avgCompletionTime }}</div>
              <div class="stat-label">Avg. Completion Time</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Edit Profile</h2>
          <button class="close-btn" @click="showEditModal = false">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-grid">
            <div class="form-field">
              <label>Full Name</label>
              <input type="text" v-model="profileForm.full_name" required />
            </div>
            <div class="form-field">
              <label>Email</label>
              <input type="email" v-model="profileForm.email" required />
            </div>
            <div class="form-field">
              <label>Phone</label>
              <input type="tel" v-model="profileForm.phone" placeholder="+251 9XX XXX XXX" />
            </div>
            <div class="form-field">
              <label>Municipality</label>
              <select v-model="profileForm.municipality">
                <option value="">Select municipality</option>
                <option v-for="muni in municipalities" :key="muni.value" :value="muni.value">
                  {{ muni.label }}
                </option>
              </select>
            </div>
            <div class="form-field">
              <label>License Number</label>
              <input type="text" v-model="profileForm.license_number" />
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="showEditModal = false">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="isUpdating">
              {{ isUpdating ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Change Password</h2>
          <button class="close-btn" @click="showPasswordModal = false">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-field">
            <label>Current Password</label>
            <input type="password" v-model="passwordForm.current_password" required />
          </div>
          <div class="form-field">
            <label>New Password</label>
            <input type="password" v-model="passwordForm.new_password" required />
          </div>
          <div class="form-field">
            <label>Confirm New Password</label>
            <input type="password" v-model="passwordForm.confirm_password" required />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="showPasswordModal = false">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="isUpdatingPassword">
              {{ isUpdatingPassword ? 'Updating...' : 'Update Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { usePermissions } from '~/composables/usePermissions.js'
import { userService } from '~/services/userService.js'
import { useNotifications } from '~/composables/useNotifications.js'

// Page metadata
definePageMeta({
  title: 'My Profile - ValuAdis',
  description: 'Manage your ValuAdis profile and account settings'
})

// Store and composables
const authStore = useAuthStore()
const { userPermissions, roleDisplayName } = usePermissions()
const { success, error, warning, info } = useNotifications()

// Modal states
const showEditModal = ref(false)
const showPasswordModal = ref(false)
const show2FAModal = ref(false)
const showSessionsModal = ref(false)

// Loading states
const isUpdating = ref(false)
const isUpdatingPassword = ref(false)

// Profile form
const profileForm = ref({
  full_name: '',
  email: '',
  phone: '',
  municipality: '',
  license_number: ''
})

// Password form
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// Activity stats (mock data - would come from API)
const totalValuations = ref(127)
const totalProperties = ref(89)
const avgCompletionTime = ref('2.5 days')

// Ethiopian municipalities
const municipalities = userService.getEthiopianMunicipalities()

// Computed properties
const userInitials = computed(() => {
  const name = authStore.user?.full_name || 'User'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

// Methods
function formatPhone(phone) {
  if (!phone) return ''
  // Format Ethiopian phone number
  const cleaned = phone.replace(/\s/g, '')
  if (cleaned.startsWith('+251')) {
    return cleaned.replace(/(\+251)(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4')
  } else if (cleaned.startsWith('0')) {
    return cleaned.replace(/(0)(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4')
  }
  return phone
}

function getMunicipalityLabel(municipality) {
  const muni = municipalities.find(m => m.value === municipality)
  return muni ? muni.label : municipality
}

function formatDate(dateString) {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-ET', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatPermissionName(permission) {
  return permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

async function updateProfile() {
  isUpdating.value = true
  try {
    const result = await userService.updateUser(authStore.user.id, profileForm.value)
    if (result.success) {
      // Update local user data
      await authStore.fetchCurrentUser()
      showEditModal.value = false
      success('Profile updated successfully!')
    } else {
      error(result.error || 'Failed to update profile')
    }
  } catch (err) {
    error('Network error. Please try again.')
  } finally {
    isUpdating.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    error('Passwords do not match')
    return
  }

  if (passwordForm.value.new_password.length < 8) {
    error('Password must be at least 8 characters long')
    return
  }

  isUpdatingPassword.value = true
  try {
    const result = await userService.resetUserPassword(authStore.user.id, passwordForm.value.new_password)
    if (result.success) {
      showPasswordModal.value = false
      passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
      success('Password changed successfully!')
    } else {
      error(result.error || 'Failed to change password')
    }
  } catch (err) {
    error('Network error. Please try again.')
  } finally {
    isUpdatingPassword.value = false
  }
}

function exportProfileData() {
  info('Exporting profile data...')
  // Implement profile data export
}

// Initialize form with current user data
onMounted(() => {
  if (authStore.user) {
    profileForm.value = {
      full_name: authStore.user.full_name || '',
      email: authStore.user.email || '',
      phone: authStore.user.phone || '',
      municipality: authStore.user.municipality || '',
      license_number: authStore.user.license_number || ''
    }
  }
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
}

.header-content p {
  margin: 0;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.profile-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.profile-card, .security-card, .activity-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.profile-avatar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: 700;
}

.avatar-info h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.role-badge {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.profile-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary, .btn-primary {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.detail-grid, .status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item, .status-item {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.detail-item label, .status-item label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.detail-item p, .status-item p {
  margin: 0;
  font-size: 14px;
  color: #1f2937;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.verified {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.unverified {
  background: #fef3c7;
  color: #92400e;
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-tag {
  padding: 4px 8px;
  background: #e5e7eb;
  color: #374151;
  border-radius: 4px;
  font-size: 12px;
}

.permission-more {
  padding: 4px 8px;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 4px;
  font-size: 12px;
  font-style: italic;
}

.card-header {
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.security-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.security-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  color: #374151;
}

.security-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.activity-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #059669;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
}

.profile-form, .password-form {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.form-field label {
  margin-bottom: 6px;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.form-field input,
.form-field select {
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: #059669;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .profile-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .activity-stats {
    grid-template-columns: 1fr;
  }
}
</style>
