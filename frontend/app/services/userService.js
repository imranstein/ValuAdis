import { apiService } from './apiService.js'

class UserService
{
  constructor ()
  {
    this.endpoints = {
      users: '/api/v1/users/',
      auth: '/api/v1/auth/'
    }
  }

  getAuthHeaders ()
  {
    // Get JWT token from localStorage
    const token = localStorage.getItem( 'valuadis_token' )
    return token ? { 'Authorization': `Bearer ${ token }` } : {}
  }

  getAuthCredentials ()
  {
    // Include credentials for API calls
    return { credentials: 'include' }
  }

  async handleApiCall ( call, fallbackData = null )
  {
    try
    {
      const result = await call()
      return { success: true, data: result }
    } catch ( error )
    {
      console.error( 'API call failed:', error )
      return {
        success: false,
        error: error.message,
        data: fallbackData
      }
    }
  }

  async getCurrentUser ()
  {
    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.users }me`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async getUsers ( options = {} )
  {
    const {
      skip = 0,
      limit = 100,
      municipality = null,
      is_active = null,
      role = null
    } = options

    const params = new URLSearchParams( {
      skip: skip.toString(),
      limit: limit.toString()
    } )

    if ( municipality ) params.append( 'municipality', municipality )
    if ( is_active !== null ) params.append( 'is_active', is_active.toString() )
    if ( role ) params.append( 'role', role )

    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.users }?${ params }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async getUserById ( userId )
  {
    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.users }${ userId }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async createUser ( userData )
  {
    return this.handleApiCall(
      () => apiService.post( this.endpoints.users, userData, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async updateUser ( userId, userData )
  {
    return this.handleApiCall(
      () => apiService.put( `${ this.endpoints.users }${ userId }`, userData, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async deleteUser ( userId )
  {
    return this.handleApiCall(
      () => apiService.delete( `${ this.endpoints.users }${ userId }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async toggleUserStatus ( userId, isActive )
  {
    return this.handleApiCall(
      () => apiService.patch( `${ this.endpoints.users }${ userId }/status`, { is_active: isActive }, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async resetUserPassword ( userId, newPassword )
  {
    return this.handleApiCall(
      () => apiService.post( `${ this.endpoints.users }${ userId }/reset-password`, { password: newPassword }, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async getUserRoles ()
  {
    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.users }roles`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async assignUserRole ( userId, roleId )
  {
    return this.handleApiCall(
      () => apiService.post( `${ this.endpoints.users }${ userId }/roles`, { role_id: roleId }, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async removeUserRole ( userId, roleId )
  {
    return this.handleApiCall(
      () => apiService.delete( `${ this.endpoints.users }${ userId }/roles/${ roleId }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async searchUsers ( query, options = {} )
  {
    const { limit = 20 } = options

    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.users }search?q=${ encodeURIComponent( query ) }&limit=${ limit }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async exportUsers ( options = {} )
  {
    const { format = 'csv', municipality = null, role = null } = options

    const params = new URLSearchParams( { format } )
    if ( municipality ) params.append( 'municipality', municipality )
    if ( role ) params.append( 'role', role )

    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.users }export?${ params }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  // Helper methods for Ethiopian compliance
  getEthiopianMunicipalities ()
  {
    return [
      { value: 'addis_ababa', label: 'Addis Ababa' },
      { value: 'dire_dawa', label: 'Dire Dawa' },
      { value: 'mekelle', label: 'Mekelle' },
      { value: 'gondar', label: 'Gondar' },
      { value: 'bahir_dar', label: 'Bahir Dar' },
      { value: 'hawassa', label: 'Hawassa' },
      { value: 'adama', label: 'Adama' },
      { value: 'jimma', label: 'Jimma' },
      { value: 'dessie', label: 'Dessie' },
      { value: 'harar', label: 'Harar' }
    ]
  }

  getRoleOptions ()
  {
    return [
      { value: 'admin', label: 'Administrator', description: 'Full system access' },
      { value: 'assessor', label: 'Property Assessor', description: 'Can perform valuations' },
      { value: 'supervisor', label: 'Supervisor', description: 'Can review valuations' },
      { value: 'clerk', label: 'Data Clerk', description: 'Can manage property data' },
      { value: 'viewer', label: 'Viewer', description: 'Read-only access' }
    ]
  }

  validateEthiopianPhone ( phone )
  {
    // Ethiopian phone format: +251 9X XXX XXXX or 09XX XXX XXXX
    const ethiopianPhoneRegex = /^(\+251\s?|0)[9]\d{2}\s?\d{3}\s?\d{4}$/
    return ethiopianPhoneRegex.test( phone.replace( /\s/g, '' ) )
  }

  validateLicenseNumber ( licenseNumber )
  {
    // Basic validation for Ethiopian license numbers
    return licenseNumber && licenseNumber.length >= 6 && licenseNumber.length <= 20
  }

  formatUserData ( userData )
  {
    // Format user data for API submission
    return {
      ...userData,
      phone: userData.phone ? userData.phone.replace( /\s/g, '' ) : null,
      municipality: userData.municipality || null,
      license_number: userData.license_number || null
    }
  }
}

export const userService = new UserService()
