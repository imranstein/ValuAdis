import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

// Permission definitions for Ethiopian property valuation system
export const PERMISSIONS = {
  // Dashboard permissions
  DASHBOARD_VIEW: 'dashboard:view',
  DASHBOARD_EXPORT: 'dashboard:export',
  
  // Property permissions
  PROPERTY_VIEW: 'property:view',
  PROPERTY_CREATE: 'property:create',
  PROPERTY_UPDATE: 'property:update',
  PROPERTY_DELETE: 'property:delete',
  PROPERTY_VALUATE: 'property:valuate',
  PROPERTY_APPROVE: 'property:approve',
  
  // Valuation permissions
  VALUATION_VIEW: 'valuation:view',
  VALUATION_CREATE: 'valuation:create',
  VALUATION_UPDATE: 'valuation:update',
  VALUATION_DELETE: 'valuation:delete',
  VALUATION_APPROVE: 'valuation:approve',
  VALUATION_EXPORT: 'valuation:export',
  
  // User management permissions
  USER_VIEW: 'user:view',
  USER_CREATE: 'user:create',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
  USER_MANAGE_ROLES: 'user:manage_roles',
  USER_APPROVE: 'user:approve',
  
  // Scraper permissions
  SCRAPER_VIEW: 'scraper:view',
  SCRAPER_CREATE: 'scraper:create',
  SCRAPER_UPDATE: 'scraper:update',
  SCRAPER_DELETE: 'scraper:delete',
  SCRAPER_RUN: 'scraper:run',
  SCRAPER_CONFIGURE: 'scraper:configure',
  
  // System permissions
  SYSTEM_SETTINGS: 'system:settings',
  SYSTEM_AUDIT: 'system:audit',
  SYSTEM_BACKUP: 'system:backup',
  SYSTEM_EXPORT: 'system:export',
  
  // Report permissions
  REPORT_VIEW: 'report:view',
  REPORT_CREATE: 'report:create',
  REPORT_EXPORT: 'report:export',
  REPORT_APPROVE: 'report:approve'
}

// Role definitions with Ethiopian context
export const ROLES = {
  SYSTEM_ADMIN: {
    name: 'system_admin',
    displayName: 'System Administrator',
    description: 'Full system access and configuration',
    permissions: Object.values(PERMISSIONS)
  },
  FIRM_ADMIN: {
    name: 'firm_admin',
    displayName: 'Firm Administrator',
    description: 'Manage firm users and valuations',
    permissions: [
      PERMISSIONS.DASHBOARD_VIEW,
      PERMISSIONS.DASHBOARD_EXPORT,
      PERMISSIONS.PROPERTY_VIEW,
      PERMISSIONS.PROPERTY_CREATE,
      PERMISSIONS.PROPERTY_UPDATE,
      PERMISSIONS.VALUATION_VIEW,
      PERMISSIONS.VALUATION_CREATE,
      PERMISSIONS.VALUATION_UPDATE,
      PERMISSIONS.VALUATION_APPROVE,
      PERMISSIONS.USER_VIEW,
      PERMISSIONS.USER_CREATE,
      PERMISSIONS.USER_UPDATE,
      PERMISSIONS.USER_APPROVE,
      PERMISSIONS.SCRAPER_VIEW,
      PERMISSIONS.SCRAPER_RUN,
      PERMISSIONS.REPORT_VIEW,
      PERMISSIONS.REPORT_CREATE,
      PERMISSIONS.REPORT_EXPORT,
      PERMISSIONS.REPORT_APPROVE
    ]
  },
  SENIOR_VALUER: {
    name: 'senior_valuer',
    displayName: 'Senior Valuer',
    description: 'Experienced valuer with approval authority',
    permissions: [
      PERMISSIONS.DASHBOARD_VIEW,
      PERMISSIONS.PROPERTY_VIEW,
      PERMISSIONS.PROPERTY_CREATE,
      PERMISSIONS.PROPERTY_UPDATE,
      PERMISSIONS.PROPERTY_VALUATE,
      PERMISSIONS.PROPERTY_APPROVE,
      PERMISSIONS.VALUATION_VIEW,
      PERMISSIONS.VALUATION_CREATE,
      PERMISSIONS.VALUATION_UPDATE,
      PERMISSIONS.VALUATION_APPROVE,
      PERMISSIONS.REPORT_VIEW,
      PERMISSIONS.REPORT_CREATE,
      PERMISSIONS.REPORT_EXPORT
    ]
  },
  PROPERTY_VALUER: {
    name: 'property_valuer',
    displayName: 'Property Valuer',
    description: 'Licensed property valuer',
    permissions: [
      PERMISSIONS.DASHBOARD_VIEW,
      PERMISSIONS.PROPERTY_VIEW,
      PERMISSIONS.PROPERTY_CREATE,
      PERMISSIONS.PROPERTY_UPDATE,
      PERMISSIONS.PROPERTY_VALUATE,
      PERMISSIONS.VALUATION_VIEW,
      PERMISSIONS.VALUATION_CREATE,
      PERMISSIONS.VALUATION_UPDATE,
      PERMISSIONS.REPORT_VIEW,
      PERMISSIONS.REPORT_CREATE,
      PERMISSIONS.REPORT_EXPORT
    ]
  },
  DATA_CLERK: {
    name: 'data_clerk',
    displayName: 'Data Clerk',
    description: 'Data entry and property management',
    permissions: [
      PERMISSIONS.DASHBOARD_VIEW,
      PERMISSIONS.PROPERTY_VIEW,
      PERMISSIONS.PROPERTY_CREATE,
      PERMISSIONS.PROPERTY_UPDATE,
      PERMISSIONS.SCRAPER_VIEW,
      PERMISSIONS.SCRAPER_RUN
    ]
  },
  VIEWER: {
    name: 'viewer',
    displayName: 'Viewer',
    description: 'Read-only access to properties and valuations',
    permissions: [
      PERMISSIONS.DASHBOARD_VIEW,
      PERMISSIONS.PROPERTY_VIEW,
      PERMISSIONS.VALUATION_VIEW,
      PERMISSIONS.REPORT_VIEW
    ]
  }
}

export function usePermissions() {
  const authStore = useAuthStore()
  
  // Get user roles and permissions
  const userRoles = computed(() => {
    const roles = []
    // Roles array from backend (full user object)
    if (authStore.user?.roles?.length) {
      roles.push(...authStore.user.roles.map(role => role.name))
    }
    // Flat role string from JWT fallback (e.g. 'system_admin', 'admin')
    const flatRole = authStore.user?.role
    if (flatRole && !roles.includes(flatRole)) {
      roles.push(flatRole)
      // Map legacy 'admin' to system_admin
      if (flatRole === 'admin' && !roles.includes('system_admin')) {
        roles.push('system_admin')
      }
    }
    return roles
  })
  
  const userPermissions = computed(() => {
    if (!authStore.user?.permissions) return []
    return authStore.user.permissions.map(perm => perm.name)
  })
  
  const userRoleNames = computed(() => {
    return authStore.user?.roles?.map(role => role.display_name) || []
  })
  
  // Check if user has specific permission
  const hasPermission = (permission) => {
    return userPermissions.value.includes(permission)
  }
  
  // Check if user has any of the specified permissions
  const hasAnyPermission = (permissions) => {
    return permissions.some(perm => userPermissions.value.includes(perm))
  }
  
  // Check if user has all specified permissions
  const hasAllPermissions = (permissions) => {
    return permissions.every(perm => userPermissions.value.includes(perm))
  }
  
  // Check if user has specific role
  const hasRole = (role) => {
    return userRoles.value.includes(role)
  }
  
  // Check if user has any of the specified roles
  const hasAnyRole = (roles) => {
    return roles.some(role => userRoles.value.includes(role))
  }
  
  // Check if user is admin (system or firm)
  const isAdmin = computed(() => {
    return hasRole(ROLES.SYSTEM_ADMIN.name) || hasRole(ROLES.FIRM_ADMIN.name)
  })
  
  // Check if user is a valuer (any level)
  const isValuer = computed(() => {
    return hasAnyRole([
      ROLES.SENIOR_VALUER.name,
      ROLES.PROPERTY_VALUER.name
    ])
  })
  
  // Check if user can approve valuations
  const canApproveValuations = computed(() => {
    return hasRole(ROLES.SYSTEM_ADMIN.name) ||
           hasRole(ROLES.FIRM_ADMIN.name) ||
           hasRole(ROLES.SENIOR_VALUER.name)
  })
  
  // Check if user can manage users
  const canManageUsers = computed(() => {
    return hasRole(ROLES.SYSTEM_ADMIN.name) ||
           hasRole(ROLES.FIRM_ADMIN.name)
  })
  
  // Check if user can access admin panel
  const canAccessAdmin = computed(() => {
    return hasAnyRole([
      ROLES.SYSTEM_ADMIN.name,
      ROLES.FIRM_ADMIN.name
    ])
  })
  
  // Check if user can manage scrapers
  const canManageScrapers = computed(() => {
    return hasRole(ROLES.SYSTEM_ADMIN.name) ||
           hasRole(ROLES.FIRM_ADMIN.name) ||
           hasRole(ROLES.DATA_CLERK.name)
  })
  
  // Check if user can perform valuations
  const canPerformValuations = computed(() => {
    return hasAnyRole([
      ROLES.SENIOR_VALUER.name,
      ROLES.PROPERTY_VALUER.name
    ])
  })
  
  // Get user's primary role (highest privilege)
  const primaryRole = computed(() => {
    const roleHierarchy = [
      ROLES.SYSTEM_ADMIN.name,
      ROLES.FIRM_ADMIN.name,
      ROLES.SENIOR_VALUER.name,
      ROLES.PROPERTY_VALUER.name,
      ROLES.DATA_CLERK.name,
      ROLES.VIEWER.name
    ]
    
    for (const role of roleHierarchy) {
      if (hasRole(role)) {
        return ROLES[Object.keys(ROLES).find(key => ROLES[key].name === role)]
      }
    }
    
    return ROLES.VIEWER
  })
  
  // Get role display name
  const roleDisplayName = computed(() => {
    return primaryRole.value?.displayName || 'Unknown'
  })
  
  // Check access for specific features
  const canAccessFeature = (feature) => {
    const featurePermissions = {
      dashboard: [PERMISSIONS.DASHBOARD_VIEW],
      properties: [PERMISSIONS.PROPERTY_VIEW],
      valuations: [PERMISSIONS.VALUATION_VIEW],
      users: [PERMISSIONS.USER_VIEW],
      scrapers: [PERMISSIONS.SCRAPER_VIEW],
      settings: [PERMISSIONS.SYSTEM_SETTINGS],
      reports: [PERMISSIONS.REPORT_VIEW],
      map: [PERMISSIONS.PROPERTY_VIEW],
      analytics: [PERMISSIONS.DASHBOARD_VIEW]
    }
    
    const requiredPermissions = featurePermissions[feature]
    if (!requiredPermissions) return false
    
    return hasAnyPermission(requiredPermissions)
  }
  
  // Municipality-based access control (Ethiopian context)
  const canAccessMunicipality = (municipality) => {
    // System admins can access all municipalities
    if (hasRole(ROLES.SYSTEM_ADMIN.name)) return true
    
    // Firm admins can access their firm's municipalities
    if (hasRole(ROLES.FIRM_ADMIN.name)) {
      // This would be based on user's assigned municipalities
      return authStore.user?.municipality === municipality || 
             authStore.user?.accessible_municipalities?.includes(municipality)
    }
    
    // Other roles can only access their assigned municipality
    return authStore.user?.municipality === municipality
  }
  
  return {
    // State
    userRoles,
    userPermissions,
    userRoleNames,
    primaryRole,
    roleDisplayName,
    
    // Permission checks
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    
    // Role checks
    hasRole,
    hasAnyRole,
    isAdmin,
    isValuer,
    canApproveValuations,
    canManageUsers,
    canAccessAdmin,
    canManageScrapers,
    canPerformValuations,
    
    // Feature access
    canAccessFeature,
    canAccessMunicipality,
    
    // Constants
    PERMISSIONS,
    ROLES
  }
}
