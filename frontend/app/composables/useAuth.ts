import { useRouter, useState } from '#app'
import { readonly } from 'vue'
import { isJwtValid, decodeJwtPayload } from '~/utils/jwt'

export const useAuth = () => {
  const router = useRouter()
  const token = useState('auth.token', () => null as string | null)
  const user = useState('auth.user', () => null as any)

  const isTokenValid = (jwtToken?: string): boolean => {
    const tokenToCheck = jwtToken || token.value

    if (!tokenToCheck) return false
    return isJwtValid(tokenToCheck)
  }

  const getTokenPayload = (jwtToken?: string): any => {
    const tokenToCheck = jwtToken || token.value

    if (!tokenToCheck) return null
    return decodeJwtPayload(tokenToCheck)
  }

  const validateAndRefresh = async (): Promise<boolean> => {
    if (!isTokenValid()) {
      token.value = null
      user.value = null
      await router.push('/login?reason=token-expired')
      return false
    }
    return true
  }

  const setAuth = (newToken: string, newUser?: any) => {
    token.value = newToken
    if (newUser) user.value = newUser
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
  }

  return {
    token: readonly(token),
    user: readonly(user),
    isTokenValid,
    getTokenPayload,
    validateAndRefresh,
    setAuth,
    clearAuth,
  }
}
