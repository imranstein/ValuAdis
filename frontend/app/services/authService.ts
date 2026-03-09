import type { AxiosInstance } from 'axios'
import type { LoginCredentials, RegisterData, AuthTokens, User } from '~/types'

// The backend returns token data directly (not wrapped in ApiResponse).
// Use the raw Axios instance to avoid the ApiResponse unwrapping layer.
function getRawApi(): AxiosInstance {
  const config = useRuntimeConfig()
  const { default: apiService } = useNuxtApp().$apiService as any
  // Fall back to a direct axios instance keyed to apiBaseUrl
  return (apiService as any)?.getApi?.() ?? (() => {
    const axios = (window as any).__axios__
    if (axios) return axios
    throw new Error('Axios instance unavailable')
  })()
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBaseUrl as string
    // Use fetch directly so we avoid the ApiResponse wrapper assumption
    const res = await fetch(`${baseURL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Login failed')
    }
    const tokens: AuthTokens = await res.json()
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
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Registration failed')
    }
    const tokens: AuthTokens = await res.json()
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
    const refreshTok = this.getRefreshToken()
    if (!refreshTok) {
      throw new Error('No refresh token available')
    }
    const res = await fetch(`${baseURL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${refreshTok}`,
      },
    })
    if (!res.ok) {
      throw new Error(`Token refresh failed: ${res.status} ${res.statusText}`)
    }
    const tokens: AuthTokens = await res.json()
    this.setToken(tokens.access_token)
    // Persist the rotated refresh token returned by the server
    if (tokens.refresh_token) this.setRefreshToken(tokens.refresh_token)
    return tokens
  }

  setToken(token: string): void {
    if (process.client || typeof window !== 'undefined') localStorage.setItem('valuadis_token', token)
  }

  getToken(): string | null {
    if (process.client) return localStorage.getItem('valuadis_token')
    return null
  }

  removeToken(): void {
    if (process.client) localStorage.removeItem('valuadis_token')
  }

  setRefreshToken(token: string): void {
    if (process.client || typeof window !== 'undefined') localStorage.setItem('valuadis_refresh_token', token)
  }

  getRefreshToken(): string | null {
    if (process.client) return localStorage.getItem('valuadis_refresh_token')
    return null
  }

  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  logout(): void {
    if (process.client) {
      localStorage.removeItem('valuadis_token')
      localStorage.removeItem('valuadis_refresh_token')
    }
  }
}

export const authService = new AuthService()
export default authService
