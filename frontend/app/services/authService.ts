import type { LoginCredentials, RegisterData, AuthTokens, User } from '~/types'
import {
  clearAuthTokens,
  getAccessToken,
  getRefreshTokenValue,
  removeAccessToken,
  setAccessToken,
  setRefreshTokenValue
} from '~/utils/authToken'

function unwrapTokens(response: AuthTokens | { data?: AuthTokens }): AuthTokens {
  return 'access_token' in response ? response : response.data as AuthTokens
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBaseUrl as string
    // Use fetch directly so we avoid the ApiResponse wrapper assumption
    const res = await fetch(`${baseURL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(credentials),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.message || err.detail || 'Login failed')
    }
    const tokens = unwrapTokens(await res.json())
    this.setToken(tokens.access_token)
    if (tokens.refresh_token) this.setRefreshToken(tokens.refresh_token)
    return tokens
  }

  async register(data: RegisterData): Promise<AuthTokens> {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBaseUrl as string
    const res = await fetch(`${baseURL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.message || err.detail || 'Registration failed')
    }
    const tokens = unwrapTokens(await res.json())
    this.setToken(tokens.access_token)
    if (tokens.refresh_token) this.setRefreshToken(tokens.refresh_token)
    return tokens
  }

  async getCurrentUser(): Promise<User> {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBaseUrl as string
    const token = this.getToken()
    const res = await fetch(`${baseURL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      if (res.status === 401) {
        this.logout()
        if (process.client) window.location.href = '/login'
      }
      throw new Error('Failed to get current user')
    }
    return res.json() as Promise<User>
  }

  async refreshToken(): Promise<AuthTokens> {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBaseUrl as string
    // Bearer header when an in-memory refresh token exists; otherwise rely on
    // the httpOnly valuadis_refresh cookie (browser session restore on reload).
    const refreshTok = this.getRefreshToken()
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (refreshTok) headers.Authorization = `Bearer ${refreshTok}`
    const res = await fetch(`${baseURL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers,
      credentials: 'include',
    })
    if (!res.ok) {
      throw new Error(`Token refresh failed: ${res.status} ${res.statusText}`)
    }
    const tokens = unwrapTokens(await res.json())
    this.setToken(tokens.access_token)
    // Persist the rotated refresh token returned by the server
    if (tokens.refresh_token) this.setRefreshToken(tokens.refresh_token)
    return tokens
  }

  setToken(token: string): void {
    setAccessToken(token)
  }

  getToken(): string | null {
    return getAccessToken()
  }

  removeToken(): void {
    removeAccessToken()
  }

  setRefreshToken(token: string): void {
    setRefreshTokenValue(token)
  }

  getRefreshToken(): string | null {
    return getRefreshTokenValue()
  }

  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  logout(): void {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBaseUrl as string
    // Clear the httpOnly refresh cookie server-side; local state clears regardless
    fetch(`${baseURL}/api/v1/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    }).catch(() => {})
    clearAuthTokens()
  }
}

export const authService = new AuthService()
export default authService
