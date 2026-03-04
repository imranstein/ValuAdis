import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type { ApiResponse, ApiError } from '~/types'

class ApiService {
  private api: AxiosInstance

  constructor() {
    const config = useRuntimeConfig()
    
    this.api = axios.create({
      baseURL: config.public.apiBaseUrl as string,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Request interceptor - add auth token
    this.api.interceptors.request.use(
      (config) => {
        if (process.client) {
          const token = localStorage.getItem('valuadis_token')
          if (token) {
            config.headers.Authorization = `Bearer ${token}`
          }
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle errors
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          if (process.client) {
            localStorage.removeItem('valuadis_token')
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  getApi(): AxiosInstance {
    return this.api
  }

  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await this.api.get<ApiResponse<T>>(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.post<ApiResponse<T>>(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.put<ApiResponse<T>>(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.api.delete<ApiResponse<T>>(url)
    return response.data
  }
}

export const apiService = new ApiService()
export default apiService
