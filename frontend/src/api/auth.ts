import { ApiError, apiFetch } from './client'

export type User = {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'user'
}

export type Credentials = {
  username: string
  password: string
}

export function fetchCsrfCookie(): Promise<void> {
  return apiFetch<void>('/api/v1/auth/csrf/')
}

export function signup(credentials: Credentials): Promise<User> {
  return apiFetch<User>('/api/v1/auth/signup/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function login(credentials: Credentials): Promise<User> {
  return apiFetch<User>('/api/v1/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function logout(): Promise<void> {
  return apiFetch<void>('/api/v1/auth/logout/', { method: 'POST' })
}

export async function fetchCurrentUser(): Promise<User | null> {
  try {
    return await apiFetch<User>('/api/v1/auth/me/')
  } catch (error) {
    if (error instanceof ApiError && error.status === 403) return null
    throw error
  }
}
