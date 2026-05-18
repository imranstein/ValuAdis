let memoryAccessToken: string | null = null
let memoryRefreshToken: string | null = null
const accessTokenKey = 'valuadis_token'
const refreshTokenKey = 'valuadis_refresh_token'
const userKey = 'valuadis_user'

function getStorage(): Storage | null {
  try {
    if (!process.client || typeof window === 'undefined' || !window.localStorage) return null
    return window.localStorage
  } catch {
    return null
  }
}

function setCookie(key: string, value: string): void {
  try {
    if (!process.client || typeof document === 'undefined') return
    document.cookie = `${key}=${encodeURIComponent(value)}; path=/; max-age=86400; SameSite=Lax`
  } catch {
    // Some embedded browser contexts expose storage as read-only. Memory storage still covers SPA navigation.
  }
}

function getCookie(key: string): string | null {
  try {
    if (!process.client || typeof document === 'undefined') return null
    const match = document.cookie.match(new RegExp(`(?:^|; )${key}=([^;]*)`))
    return match ? decodeURIComponent(match[1]) : null
  } catch {
    return null
  }
}

function removeCookie(key: string): void {
  try {
    if (!process.client || typeof document === 'undefined') return
    document.cookie = `${key}=; path=/; max-age=0; SameSite=Lax`
  } catch {
    // Ignore storage-restricted browser contexts.
  }
}

export function setAccessToken(token: string): void {
  memoryAccessToken = token
  getStorage()?.setItem(accessTokenKey, token)
  setCookie(accessTokenKey, token)
}

export function getAccessToken(): string | null {
  return getStorage()?.getItem(accessTokenKey) || memoryAccessToken || getCookie(accessTokenKey)
}

export function removeAccessToken(): void {
  memoryAccessToken = null
  getStorage()?.removeItem(accessTokenKey)
  removeCookie(accessTokenKey)
}

export function setRefreshTokenValue(token: string): void {
  memoryRefreshToken = token
  getStorage()?.setItem(refreshTokenKey, token)
  setCookie(refreshTokenKey, token)
}

export function getRefreshTokenValue(): string | null {
  return getStorage()?.getItem(refreshTokenKey) || memoryRefreshToken || getCookie(refreshTokenKey)
}

export function clearAuthTokens(): void {
  memoryAccessToken = null
  memoryRefreshToken = null
  getStorage()?.removeItem(accessTokenKey)
  getStorage()?.removeItem(refreshTokenKey)
  getStorage()?.removeItem(userKey)
  removeCookie(accessTokenKey)
  removeCookie(refreshTokenKey)
}
