import { useContext } from 'react'

import { AuthContext } from './AuthContext'

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) {
    throw new Error('useAuth trebuie folosit in interiorul <AuthProvider>')
  }
  return context
}
