import {
  clearAuthTokens,
  getAccessToken,
  removeAccessToken,
  setAccessToken
} from '~/utils/authToken'

class AuthService
{
  getBaseURL ()
  {
    const config = useRuntimeConfig()
    return config.public.apiBaseUrl
  }

  async login ( credentials )
  {
    try
    {
      const baseURL = this.getBaseURL()
      const response = await fetch( `${ baseURL }/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify( credentials )
      } )

  if ( !response.ok )
  {
      throw new Error( `Login failed: ${ response.statusText }` )
  }

      const data = await response.json()

      // Store token and user data for authentication
      const token = data.access_token || data.data?.access_token
      if ( token )
      {
        setAccessToken( token )
      }

      return { success: true, data }
    } catch ( error )
    {
      console.error( 'Login error:', error )
      throw error
    }
  }

  async logout ()
  {
    try
    {
      // Call backend logout to invalidate httpOnly cookie
      await fetch( `${ this.getBaseURL() }/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      } )
    } catch ( error )
    {
      console.error( 'Logout error:', error )
    } finally
    {
      clearAuthTokens()
    }
  }

  async refreshToken ()
  {
    try
    {
      const response = await fetch( `${ this.getBaseURL() }/api/v1/auth/refresh`, {
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

  async getCurrentUser ()
  {
    const baseURL = this.getBaseURL()
    const token = getAccessToken()
    if ( !token ) throw new Error( 'Missing authentication token' )

    const response = await fetch( `${ baseURL }/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${ token }` }
    } )

    if ( !response.ok )
    {
      throw new Error( 'Failed to get current user' )
    }

    return response.json()
  }

  isAuthenticated ()
  {
    return !!getAccessToken()
  }

  getLegacyToken ()
  {
    return getAccessToken()
  }

  clearLegacyTokens ()
  {
    removeAccessToken()
  }
}

export default new AuthService()

export const authService = new AuthService()
