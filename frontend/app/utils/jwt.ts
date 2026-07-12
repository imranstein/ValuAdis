export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null

    const normalized = `${parts[1].replace(/-/g, '+').replace(/_/g, '/')}${
      '='.repeat((4 - (parts[1].length % 4)) % 4)
    }`

    let payloadJson: string
    if (typeof atob === 'function') {
      const bytes = atob(normalized).split('').map((char) => {
        const code = char.charCodeAt(0)
        return `%${code.toString(16).padStart(2, '0')}`
      }).join('')
      payloadJson = decodeURIComponent(bytes)
    } else if (typeof Buffer !== 'undefined') {
      payloadJson = Buffer.from(normalized, 'base64').toString('utf-8')
    } else {
      return null
    }

    return JSON.parse(payloadJson) as Record<string, unknown>
  } catch {
    return null
  }
}

export function getJwtExpiryMs(token: string): number | null {
  const payload = decodeJwtPayload(token)
  if (!payload || typeof payload.exp !== 'number') return null
  return payload.exp * 1000
}

export function isJwtExpired(token: string): boolean {
  const expiryMs = getJwtExpiryMs(token)
  if (expiryMs === null) return true
  return expiryMs <= Date.now()
}

export function isJwtValid(token: string): boolean {
  return !isJwtExpired(token)
}
