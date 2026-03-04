import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '~/services/authService'
import type { User, LoginCredentials, RegisterData } from '~/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const userRole = computed(() => user.value?.role)
  const userName = computed(() => user.value?.full_name)

  // Actions
  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null
    try {
      await authService.login(credentials)
      await fetchCurrentUser()
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
    user.value = null
  }

  async function initialize() {
    if (authService.isAuthenticated()) {
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
