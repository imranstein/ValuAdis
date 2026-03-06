class AuthService
{
  constructor ()
  {
    this.baseURL = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
  }

  async login ( credentials )
  {
    try
    {
      const response = await fetch( `${ this.baseURL }/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify( credentials ),
        credentials: 'include' // Important for httpOnly cookies
      } )

      if ( !response.ok )
      {
        throw new Error( `Login failed: ${ response.statusText }` )
      }

      const data = await response.json()

      // Store non-sensitive data in localStorage for UI purposes
      if ( data.user )
      {
        localStorage.setItem( 'valuadis_user', JSON.stringify( data.user ) )
      }

      return { success: true, data }
    } catch ( error )
    {
      console.error( 'Login error:', error )
      return { success: false, error: error.message }
    }
  }

  async logout ()
  {
    try
    {
      // Call backend logout to invalidate httpOnly cookie
      await fetch( `${ this.baseURL }/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      } )
    } catch ( error )
    {
      console.error( 'Logout error:', error )
    } finally
    {
      // Clear local storage
      localStorage.removeItem( 'valuadis_user' )
    }
  }

  async refreshToken ()
  {
    try
    {
      const response = await fetch( `${ this.baseURL }/api/v1/auth/refresh`, {
        method: 'POST',
        credentials: 'include'
      } )

      if ( !response.ok )
      {
        throw new Error( 'Token refresh failed' )
      }

      return await response.json()
    } catch ( error )
    {
      console.error( 'Token refresh error:', error )
      await this.logout()
      throw error
    }
  }

  getCurrentUser ()
  {
    try
    {
      const user = localStorage.getItem( 'valuadis_user' )
      return user ? JSON.parse( user ) : null
    } catch ( error )
    {
      console.error( 'Error getting current user:', error )
      return null
    }
  }

  isAuthenticated ()
  {
    return !!this.getCurrentUser()
  }

  // For backward compatibility during transition
  getLegacyToken ()
  {
    // This method provides fallback to localStorage token
    return localStorage.getItem( 'valuadis_token' )
  }

  clearLegacyTokens ()
  {
    // Remove old localStorage tokens after migration
    localStorage.removeItem( 'valuadis_token' )
  }
}

export default new AuthService()

export const authService = new AuthService()
