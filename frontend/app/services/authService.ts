import apiService from './api'
import type { LoginCredentials, RegisterData, AuthTokens, User, ApiResponse } from '~/types'

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await apiService.post<AuthTokens>('/api/v1/auth/login', credentials)
    if (response.success && response.data) {
      this.setToken(response.data.access_token)
      return response.data
    }
    throw new Error('Login failed')
  }

  async register(data: RegisterData): Promise<AuthTokens> {
    const response = await apiService.post<AuthTokens>('/api/v1/auth/register', data)
    if (response.success && response.data) {
      this.setToken(response.data.access_token)
      return response.data
    }
    throw new Error('Registration failed')
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiService.get<User>('/api/v1/auth/me')
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to get current user')
  }

  async refreshToken(): Promise<AuthTokens> {
    const response = await apiService.post<AuthTokens>('/api/v1/auth/refresh')
    if (response.success && response.data) {
      this.setToken(response.data.access_token)
      return response.data
    }
    throw new Error('Token refresh failed')
  }

  setToken(token: string): void {
    if (process.client) {
      localStorage.setItem('valuadis_token', token)
    }
  }

  getToken(): string | null {
    if (process.client) {
      return localStorage.getItem('valuadis_token')
    }
    return null
  }

  removeToken(): void {
    if (process.client) {
      localStorage.removeItem('valuadis_token')
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  logout(): void {
    this.removeToken()
  }
}

export const authService = new AuthService()
export default authService
