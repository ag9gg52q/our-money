import { type ReactNode, useEffect, useState } from 'react'

import * as authApi from '../api/auth'
import { AuthContext } from './AuthContext'

type AuthProviderProps = {
  children: ReactNode
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<authApi.User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let ignore = false

    authApi
      .fetchCsrfCookie()
      .then(() => authApi.fetchCurrentUser())
      .then((currentUser) => {
        if (!ignore) setUser(currentUser)
      })
      .catch(() => {
        if (!ignore) setUser(null)
      })
      .finally(() => {
        if (!ignore) setIsLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [])

  async function login(credentials: authApi.Credentials) {
    const loggedInUser = await authApi.login(credentials)
    setUser(loggedInUser)
  }

  async function logout() {
    await authApi.logout()
    setUser(null)
  }

  async function refreshUser() {
    const currentUser = await authApi.fetchCurrentUser()
    setUser(currentUser)
  }

  return (
    <AuthContext value={{ user, isLoading, login, logout, refreshUser }}>
      {children}
    </AuthContext>
  )
}
