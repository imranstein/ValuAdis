let memoryAccessToken: string | null = null
let memoryRefreshToken: string | null = null
const accessTokenKey = 'valuadis_token'
const refreshTokenKey = 'valuadis_refresh_token'
const userKey = 'valuadis_user'

function getStorage (): Storage | null {
  try {
    if (!process.client || typeof window === 'undefined' || !window.localStorage) return null
    return window.localStorage
  } catch {
    return null
  }
}

function consumeLegacyStorageToken (storage: Storage, key: string): string | null {
  const token = storage.getItem(key)
  if (!token) return null

  storage.removeItem(key)
  return token
}

export function setAccessToken (token: string): void {
  memoryAccessToken = token
}

export function getAccessToken (): string | null {
  if (memoryAccessToken) return memoryAccessToken

  const storage = getStorage()
  if (!storage) return null

  const legacyToken = consumeLegacyStorageToken(storage, accessTokenKey)
  if (legacyToken) {
    memoryAccessToken = legacyToken
    return legacyToken
  }

  return null
}

export function removeAccessToken (): void {
  memoryAccessToken = null
}

export function setRefreshTokenValue (token: string): void {
  memoryRefreshToken = token
}

export function getRefreshTokenValue (): string | null {
  if (memoryRefreshToken) return memoryRefreshToken

  const storage = getStorage()
  if (!storage) return null

  const legacyToken = consumeLegacyStorageToken(storage, refreshTokenKey)
  if (legacyToken) {
    memoryRefreshToken = legacyToken
    return legacyToken
  }

  return null
}

export function clearAuthTokens (): void {
  memoryAccessToken = null
  memoryRefreshToken = null
  getStorage()?.removeItem(accessTokenKey)
  getStorage()?.removeItem(refreshTokenKey)
  getStorage()?.removeItem(userKey)
}
