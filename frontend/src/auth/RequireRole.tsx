import { Navigate, Outlet } from 'react-router'

import { useAuth } from './useAuth'

type RequireRoleProps = {
  role?: 'admin' | 'user'
}

// Folosit sub RequireAuth: fără rol → /start; cu alt rol decât cel cerut → /.
export default function RequireRole({ role }: RequireRoleProps) {
  const { user } = useAuth()

  if (!user?.role) return <Navigate to="/start" replace />
  if (role && user.role !== role) return <Navigate to="/" replace />
  return <Outlet />
}
