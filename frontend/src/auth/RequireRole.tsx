import { Navigate, Outlet } from 'react-router'

import { useAuth } from './useAuth'

// Folosit sub RequireAuth: userul e logat, verificăm doar dacă are rol.
export default function RequireRole() {
  const { user } = useAuth()

  if (!user?.role) return <Navigate to="/start" replace />
  return <Outlet />
}
