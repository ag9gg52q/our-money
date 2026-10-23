import { Navigate, Outlet } from 'react-router'

import { useAuth } from './useAuth'

// Pagina de început e doar pentru cei fără rol; cine are deja rol merge pe Acasă.
export default function RequireNoRole() {
  const { user } = useAuth()

  if (user?.role) return <Navigate to="/" replace />
  return <Outlet />
}
