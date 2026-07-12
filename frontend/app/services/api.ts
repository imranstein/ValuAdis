import axios, { type AxiosInstance, type AxiosError, type AxiosRequestConfig } from 'axios'
import type { ApiResponse, ApiError } from '~/types'
import { getAccessToken, removeAccessToken } from '~/utils/authToken'

type RetryableAxiosConfig = AxiosRequestConfig & {
  _retryCount?: number
}

const RETRY_ATTEMPTS = 2

function sleep (ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function isRetryable (status: number | undefined): boolean {
  if (!status) return true
  return status >= 500 && status < 600
}

function shouldRetryCall (error: AxiosError<ApiError>): boolean {
  if (!error.config) return false
  const status = error.response?.status
  return isRetryable(status)
}

function nextRetryDelay (attempt: number): number {
  return Math.min(1500, 200 * Math.pow(2, attempt))
}

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
          const token = getAccessToken()
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
        const config = error.config as RetryableAxiosConfig | undefined
        const attempt = Number(config?._retryCount || 0)
        const canRetry = shouldRetryCall(error) && attempt < RETRY_ATTEMPTS
        if (canRetry && config) {
          config._retryCount = attempt + 1
          await sleep(nextRetryDelay(attempt))
          return this.api.request(config)
        }

        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          if (process.client) {
            removeAccessToken()
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
