<template>
  <div class="users-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Users</h1>
        <p>Manage user accounts, roles, and permissions for the ValuAdis platform</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportUsers">
          <i class="pi pi-download"></i>
          Export
        </button>
        <button class="action-button primary" @click="showCreateModal = true">
          <i class="pi pi-plus"></i>
          Add User
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="search-filters">
      <div class="search-section">
        <div class="search-bar">
          <i class="pi pi-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search users by name, email, or ID..."
          />
        </div>
      </div>
      
      <div class="filter-section">
        <select v-model="selectedRole" class="filter-dropdown">
          <option value="">All Roles</option>
          <option value="admin">Administrator</option>
          <option value="assessor">Property Assessor</option>
          <option value="supervisor">Supervisor</option>
          <option value="clerk">Data Clerk</option>
          <option value="viewer">Viewer</option>
        </select>
        
        <select v-model="selectedStatus" class="filter-dropdown">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
          <option value="pending">Pending</option>
        </select>
        
        <select v-model="selectedMunicipality" class="filter-dropdown">
          <option value="">All Municipalities</option>
          <option value="addis_ababa">Addis Ababa</option>
          <option value="dire_dawa">Dire Dawa</option>
          <option value="mekelle">Mekelle</option>
          <option value="gondar">Gondar</option>
          <option value="bahir_dar">Bahir Dar</option>
          <option value="hawassa">Hawassa</option>
          <option value="adama">Adama</option>
          <option value="jimma">Jimma</option>
          <option value="dessie">Dessie</option>
          <option value="harar">Harar</option>
        </select>
        
        <button class="reset-button" @click="resetFilters">
          <i class="pi pi-refresh"></i>
          Reset
        </button>
      </div>
    </div>

    <!-- User Statistics -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalUsers }}</h3>
          <p>Total Users</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>+8% from last month</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-user-check"></i>
        </div>
        <div class="stat-content">
          <h3>{{ activeUsers }}</h3>
          <p>Active Users</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>+12% from last month</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-user-plus"></i>
        </div>
        <div class="stat-content">
          <h3>{{ newUsers }}</h3>
          <p>New This Month</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>+25% from last month</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ pendingUsers }}</h3>
          <p>Pending Approval</p>
          <div class="stat-trend neutral">
            <i class="pi pi-minus"></i>
            <span>No change</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="users-table-container">
      <div class="table-header">
        <h2>User Management</h2>
        <div class="table-info">
          <span>{{ filteredUsers.length }} users</span>
          <div class="view-toggle">
            <button 
              class="view-btn" 
              :class="{ active: viewMode === 'table' }"
              @click="viewMode = 'table'"
            >
              <i class="pi pi-table"></i>
            </button>
            <button 
              class="view-btn" 
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="pi pi-th-large"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th @click="sortBy('id')">
                ID
                <i class="pi" :class="getSortIcon('id')"></i>
              </th>
              <th @click="sortBy('name')">
                Name
                <i class="pi" :class="getSortIcon('name')"></i>
              </th>
              <th @click="sortBy('email')">
                Email
                <i class="pi" :class="getSortIcon('email')"></i>
              </th>
              <th @click="sortBy('role')">
                Role
                <i class="pi" :class="getSortIcon('role')"></i>
              </th>
              <th @click="sortBy('municipality')">
                Municipality
                <i class="pi" :class="getSortIcon('municipality')"></i>
              </th>
              <th @click="sortBy('status')">
                Status
                <i class="pi" :class="getSortIcon('status')"></i>
              </th>
              <th @click="sortBy('last_login')">
                Last Login
                <i class="pi" :class="getSortIcon('last_login')"></i>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td>
                <span class="user-id">#{{ user.id }}</span>
              </td>
              <td>
                <div class="user-info">
                  <div class="user-avatar">{{ getInitials(user.name) }}</div>
                  <div class="user-details">
                    <span class="user-name">{{ user.name }}</span>
                    <span class="user-phone">{{ user.phone }}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="user-email">{{ user.email }}</span>
              </td>
              <td>
                <span class="role-badge" :class="user.role">{{ getRoleLabel(user.role) }}</span>
              </td>
              <td>
                <span class="municipality-badge">{{ getMunicipalityLabel(user.municipality) }}</span>
              </td>
              <td>
                <span class="status-badge" :class="user.status">{{ getStatusLabel(user.status) }}</span>
              </td>
              <td>
                <span class="last-login">{{ formatDate(user.last_login) }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button v-if="user.is_approved === false" class="action-btn approve" @click="approveUser(user)" title="Approve">
                    <i class="pi pi-check-circle"></i>
                  </button>
                  <button class="action-btn view" @click="viewUser(user)" title="View">
                    <i class="pi pi-eye"></i>
                  </button>
                  <button class="action-btn edit" @click="editUser(user)" title="Edit">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button 
                    v-if="user.is_approved !== false"
                    class="action-btn" 
                    :class="user.status === 'active' ? 'deactivate' : 'activate'"
                    @click="toggleUserStatus(user)" 
                    :title="user.status === 'active' ? 'Deactivate' : 'Activate'"
                  >
                    <i :class="user.status === 'active' ? 'pi pi-ban' : 'pi pi-check'"></i>
                  </button>
                  <button class="action-btn delete" @click="deleteUser(user)" title="Delete">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Grid View -->
      <div v-else class="grid-container">
        <div v-for="user in paginatedUsers" :key="user.id" class="user-card">
          <div class="card-header">
            <div class="user-avatar-large">{{ getInitials(user.name) }}</div>
            <div class="user-info">
              <h4>{{ user.name }}</h4>
              <span class="role-badge" :class="user.role">{{ getRoleLabel(user.role) }}</span>
            </div>
            <div class="card-actions">
              <button class="action-btn view" @click="viewUser(user)">
                <i class="pi pi-eye"></i>
              </button>
            </div>
          </div>
          
          <div class="card-content">
            <div class="user-details">
              <div class="detail-item">
                <i class="pi pi-envelope"></i>
                <span>{{ user.email }}</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-phone"></i>
                <span>{{ user.phone }}</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-map-marker"></i>
                <span>{{ getMunicipalityLabel(user.municipality) }}</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-clock"></i>
                <span>Last login: {{ formatDate(user.last_login) }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <span class="status-badge" :class="user.status">{{ getStatusLabel(user.status) }}</span>
            <div class="card-actions">
              <button v-if="user.is_approved === false" class="action-btn approve" @click="approveUser(user)" title="Approve">
                <i class="pi pi-check-circle"></i>
              </button>
              <button class="action-btn edit" @click="editUser(user)">
                <i class="pi pi-pencil"></i>
              </button>
              <button 
                v-if="user.is_approved !== false"
                class="action-btn" 
                :class="user.status === 'active' ? 'deactivate' : 'activate'"
                @click="toggleUserStatus(user)"
              >
                <i :class="user.status === 'active' ? 'pi pi-ban' : 'pi pi-check'"></i>
              </button>
              <button class="action-btn delete" @click="deleteUser(user)">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredUsers.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="pi pi-users"></i>
        </div>
        <h3>No users found</h3>
        <p>Create your first user account to get started</p>
        <button class="action-button primary" @click="showCreateModal = true">
          <i class="pi pi-plus"></i>
          Add User
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filteredUsers.length > itemsPerPage" class="pagination">
      <div class="pagination-info">
        <span>Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredUsers.length) }} of {{ filteredUsers.length }} users</span>
      </div>
      <div class="pagination-controls">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <i class="pi pi-chevron-left"></i>
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <i class="pi pi-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Edit User' : 'Create New User' }}</h3>
          <button class="modal-close" @click="closeModal">
            <i class="pi pi-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveUser" class="user-form">
          <div class="form-grid">
            <div class="form-field">
              <label>First Name *</label>
              <input 
                type="text" 
                v-model="userForm.first_name" 
                required
                placeholder="Enter first name"
              />
            </div>
            
            <div class="form-field">
              <label>Last Name *</label>
              <input 
                type="text" 
                v-model="userForm.last_name" 
                required
                placeholder="Enter last name"
              />
            </div>
            
            <div class="form-field">
              <label>Email Address *</label>
              <input 
                type="email" 
                v-model="userForm.email" 
                required
                placeholder="Enter email address"
              />
            </div>
            
            <div class="form-field">
              <label>Phone Number *</label>
              <input 
                type="tel" 
                v-model="userForm.phone" 
                required
                placeholder="+251 9XX XXX XXX"
              />
            </div>
            
            <div class="form-field">
              <label>Role *</label>
              <select v-model="userForm.role" required>
                <option value="">Select role</option>
                <option value="admin">Administrator</option>
                <option value="assessor">Property Assessor</option>
                <option value="supervisor">Supervisor</option>
                <option value="clerk">Data Clerk</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            
            <div class="form-field">
              <label>Municipality</label>
              <select v-model="userForm.municipality">
                <option value="">Select municipality</option>
                <option value="addis_ababa">Addis Ababa</option>
                <option value="dire_dawa">Dire Dawa</option>
                <option value="mekelle">Mekelle</option>
                <option value="gondar">Gondar</option>
                <option value="bahir_dar">Bahir Dar</option>
                <option value="hawassa">Hawassa</option>
                <option value="adama">Adama</option>
                <option value="jimma">Jimma</option>
                <option value="dessie">Dessie</option>
                <option value="harar">Harar</option>
              </select>
            </div>
            
            <div class="form-field">
              <label>Password *</label>
              <input 
                type="password" 
                v-model="userForm.password" 
                :required="!showEditModal"
                placeholder="Enter password"
              />
            </div>
            
            <div class="form-field">
              <label>Confirm Password *</label>
              <input 
                type="password" 
                v-model="userForm.confirm_password" 
                :required="!showEditModal"
                placeholder="Confirm password"
              />
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="action-button secondary" @click="closeModal">
              Cancel
            </button>
            <button type="submit" class="action-button primary" :disabled="isSubmitting">
              <i v-if="isSubmitting" class="pi pi-spin pi-spinner"></i>
              {{ showEditModal ? 'Update User' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ middleware: ['admin'] })
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const config = useRuntimeConfig()
const apiBase = config.public?.apiBaseUrl || 'http://localhost:8020'

// Reactive data
const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')
const selectedMunicipality = ref('')
const viewMode = ref('table')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const sortField = ref('id')
const sortDirection = ref('desc')

// Modal states
const showCreateModal = ref(false)
const showEditModal = ref(false)
const isSubmitting = ref(false)
const editingUser = ref(null)

// User form
const userForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  role: '',
  municipality: '',
  password: '',
  confirm_password: ''
})

// Real users data from API
const users = ref([])

// Computed properties
const filteredUsers = computed(() => {
  let filtered = users.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.id.toString().includes(query)
    )
  }

  if (selectedRole.value) {
    filtered = filtered.filter(user => user.role === selectedRole.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(user => user.status === selectedStatus.value)
  }

  if (selectedMunicipality.value) {
    filtered = filtered.filter(user => user.municipality === selectedMunicipality.value)
  }

  // Sort
  filtered.sort((a, b) => {
    let aVal = a[sortField.value]
    let bVal = b[sortField.value]
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  return filtered
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredUsers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value)
})

const totalUsers = computed(() => users.value.length)
const activeUsers = computed(() => users.value.filter(u => u.status === 'active').length)
const newUsers = computed(() => users.value.filter(u => {
  const createdDate = new Date(u.created_at)
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  return createdDate >= thirtyDaysAgo
}).length)
const pendingUsers = computed(() => users.value.filter(u => u.status === 'pending').length)

// Methods
function sortBy(field) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

function getSortIcon(field) {
  if (sortField.value !== field) return 'pi-sort'
  return sortDirection.value === 'asc' ? 'pi-sort-up' : 'pi-sort-down'
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function getRoleLabel(role) {
  const labels = {
    admin: 'Administrator',
    assessor: 'Property Assessor',
    supervisor: 'Supervisor',
    clerk: 'Data Clerk',
    viewer: 'Viewer'
  }
  return labels[role] || role
}

function getStatusLabel(status) {
  const labels = {
    active: 'Active',
    inactive: 'Inactive',
    suspended: 'Suspended',
    pending: 'Pending Approval'
  }
  return labels[status] || status
}

function getMunicipalityLabel(municipality) {
  const labels = {
    addis_ababa: 'Addis Ababa',
    dire_dawa: 'Dire Dawa',
    mekelle: 'Mekelle',
    gondar: 'Gondar',
    bahir_dar: 'Bahir Dar',
    hawassa: 'Hawassa',
    adama: 'Adama',
    jimma: 'Jimma',
    dessie: 'Dessie',
    harar: 'Harar'
  }
  return labels[municipality] || municipality
}

function formatDate(dateString) {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-ET', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function resetFilters() {
  searchQuery.value = ''
  selectedRole.value = ''
  selectedStatus.value = ''
  selectedMunicipality.value = ''
  currentPage.value = 1
}

function closeModal() {
  showCreateModal.value = false
  showEditModal.value = false
  editingUser.value = null
  resetUserForm()
}

function resetUserForm() {
  userForm.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    role: '',
    municipality: '',
    password: '',
    confirm_password: ''
  }
}

function viewUser(user) {
  console.log('View user:', user)
  // Navigate to user details page or show modal
}

function editUser(user) {
  editingUser.value = user
  userForm.value = {
    first_name: user.name.split(' ')[0],
    last_name: user.name.split(' ').slice(1).join(' '),
    email: user.email,
    phone: user.phone,
    role: user.role,
    municipality: user.municipality,
    password: '',
    confirm_password: ''
  }
  showEditModal.value = true
}

async function saveUser() {
  if (userForm.value.password !== userForm.value.confirm_password) {
    alert('Passwords do not match')
    return
  }

  isSubmitting.value = true

  try {
    const token = localStorage.getItem('valuadis_token')
    const userData = {
      first_name: userForm.value.first_name,
      last_name: userForm.value.last_name,
      email: userForm.value.email,
      phone: userForm.value.phone,
      role: userForm.value.role,
      municipality: userForm.value.municipality,
      ...(userForm.value.password && { password: userForm.value.password })
    }

    let response
    if (showEditModal.value && editingUser.value) {
      // Update existing user
      response = await fetch(`${apiBase}/api/v1/users/${editingUser.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData)
      })
    } else {
      // Create new user
      response = await fetch(`${apiBase}/api/v1/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData)
      })
    }

    if (response.ok) {
      const data = await response.json()
      
      if (showEditModal.value) {
        // Update user in local array
        const index = users.value.findIndex(u => u.id === editingUser.value.id)
        if (index > -1) {
          users.value[index] = { ...users.value[index], ...data.data }
        }
      } else {
        // Add new user to local array
        users.value.push(data.data)
      }
      
      closeModal()
      alert(showEditModal.value ? 'User updated successfully!' : 'User created successfully!')
    } else {
      const error = await response.json()
      alert(error.detail || 'Failed to save user')
    }
  } catch (error) {
    console.error('Error saving user:', error)
    alert('Network error. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

async function approveUser(user) {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/users/${user.id}/approve?approved=true`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      user.is_approved = true
      user.status = 'active'
      alert('User approved successfully!')
    } else {
      const err = await response.json()
      alert(err.detail || 'Failed to approve user')
    }
  } catch (e) {
    console.error('Approve failed:', e)
    alert('Network error. Please try again.')
  }
}

async function toggleUserStatus(user) {
  const newStatus = user.status === 'active' ? 'inactive' : 'active'
  
  if (!confirm(`Are you sure you want to ${newStatus === 'active' ? 'activate' : 'deactivate'} this user?`)) {
    return
  }

  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/users/${user.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status: newStatus })
    })

    if (response.ok) {
      user.status = newStatus
      alert(`User ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully!`)
    } else {
      const error = await response.json()
      alert(error.detail || 'Failed to update user status')
    }
  } catch (error) {
    console.error('Error updating user status:', error)
    alert('Network error. Please try again.')
  }
}

async function deleteUser(user) {
  if (!confirm(`Are you sure you want to delete user "${user.name}"? This action cannot be undone.`)) {
    return
  }

  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/users/${user.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const index = users.value.findIndex(u => u.id === user.id)
      if (index > -1) {
        users.value.splice(index, 1)
      }
      alert('User deleted successfully!')
    } else {
      const error = await response.json()
      alert(error.detail || 'Failed to delete user')
    }
  } catch (error) {
    console.error('Error deleting user:', error)
    alert('Network error. Please try again.')
  }
}

function exportUsers() {
  console.log('Exporting users...')
  // Implement export functionality
}

onMounted(async () => {
  // Load users from API
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/users`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      const raw = data.data || []
      users.value = raw.map(u => ({
        ...u,
        name: u.full_name || u.name || `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.email,
        status: u.is_approved === false ? 'pending' : (u.is_active === false ? 'inactive' : (u.status || 'active')),
        is_approved: u.is_approved !== false,
        role: u.roles?.[0]?.name || u.role || 'viewer',
        last_login: u.last_login || u.updated_at
      }))
    } else {
      console.error('Failed to load users from API')
      users.value = []
    }
  } catch (error) {
    console.error('Error loading users:', error)
    users.value = []
  }
})
</script>

<style scoped>
/* Users Container */
.users-container {
  max-width: 1400px;
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
}

/* Search and Filters */
.search-filters {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
}

.search-bar i {
  color: #64748b;
}

.search-bar input {
  flex: 1;
  border: none;
  background: none;
  outline: none;
  font-size: 0.875rem;
}

.filter-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-dropdown {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 0.875rem;
  min-width: 150px;
}

.reset-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-button:hover {
  background: #f8fafc;
  border-color: #059669;
  color: #059669;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #059669, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.stat-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.neutral {
  color: #6b7280;
}

.stat-trend.negative {
  color: #ef4444;
}

/* Users Table */
.users-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #f1f5f9;
}

.table-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.table-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.table-info span {
  color: #64748b;
  font-size: 0.875rem;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn.active {
  background: #059669;
  color: white;
  border-color: #059669;
}

/* Table Styles */
.table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  user-select: none;
}

.users-table th:hover {
  background: #f1f5f9;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.user-id {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #059669;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #059669;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
}

.user-phone {
  font-size: 0.75rem;
  color: #64748b;
}

.user-email {
  color: #374151;
  font-size: 0.875rem;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge.admin {
  background: #dcfce7;
  color: #059669;
}

.role-badge.assessor {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.supervisor {
  background: #fef3c7;
  color: #d97706;
}

.role-badge.clerk {
  background: #e0f2fe;
  color: #0369a1;
}

.role-badge.viewer {
  background: #f3f4f6;
  color: #6b7280;
}

.municipality-badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: #bbf7d0;
  color: #059669;
}

.status-badge.inactive {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.suspended {
  background: #fecaca;
  color: #dc2626;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.last-login {
  color: #64748b;
  font-size: 0.875rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #1e40af;
  color: white;
}

.action-btn.edit {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.edit:hover {
  background: #6b7280;
  color: white;
}

.action-btn.approve {
  background: #dcfce7;
  color: #059669;
}
.action-btn.approve:hover {
  background: #059669;
  color: white;
}
.action-btn.activate {
  background: #dcfce7;
  color: #059669;
}

.action-btn.activate:hover {
  background: #059669;
  color: white;
}

.action-btn.deactivate {
  background: #fef3c7;
  color: #d97706;
}

.action-btn.deactivate:hover {
  background: #d97706;
  color: white;
}

.action-btn.delete {
  background: #fecaca;
  color: #dc2626;
}

.action-btn.delete:hover {
  background: #dc2626;
  color: white;
}

/* Grid View */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.user-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.user-avatar-large {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #059669;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
}

.user-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.card-content {
  padding: 1.5rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #64748b;
  font-size: 0.875rem;
}

.detail-item i {
  color: #059669;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: #f8fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 2rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin: 0 0 2rem 0;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: white;
  border-top: 1px solid #f1f5f9;
}

.pagination-info {
  color: #64748b;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8fafc;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Modal */
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e5e7eb;
}

.user-form {
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-field input,
.form-field select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
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
  
  .filter-section {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .grid-container {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
