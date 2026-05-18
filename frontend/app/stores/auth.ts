import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '~/services/authService'
import type { User, LoginCredentials, RegisterData } from '~/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const activeSession = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => activeSession.value || !!user.value)
  const userRole = computed(() => user.value?.role)
  const userName = computed(() => user.value?.full_name)

  // Actions
  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null
    try {
      await authService.login(credentials)
      activeSession.value = true
      // Try to fetch current user, but don't let it fail the login
      try {
        await fetchCurrentUser()
      } catch (userErr) {
        console.warn('Failed to fetch current user after login, but login succeeded:', userErr)
        // Set a basic user object to prevent UI issues
        user.value = {
          id: 0,
          email: credentials.email,
          full_name: 'User',
          role: 'valuer',
          phone: '',
          is_admin: false,
          roles: [],
          created_at: new Date().toISOString()
        }
      }
      return true
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(data: RegisterData) {
    loading.value = true
    error.value = null
    try {
      await authService.register(data)
      await fetchCurrentUser()
      return true
    } catch (err: any) {
      error.value = err.message || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    loading.value = true
    error.value = null
    try {
      user.value = await authService.getCurrentUser()
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch user'
      throw err
    } finally {
      loading.value = false
    }
  }

  function logout() {
    authService.logout()
    activeSession.value = false
    user.value = null
  }

  async function initialize() {
    if (authService.isAuthenticated()) {
      activeSession.value = true
      try {
        await fetchCurrentUser()
      } catch (err) {
        logout()
      }
    }
  }

  return {
    // State
    user,
    activeSession,
    loading,
    error,
    // Getters
    isAuthenticated,
    userRole,
    userName,
    // Actions
    login,
    register,
    fetchCurrentUser,
    logout,
    initialize
  }
})
