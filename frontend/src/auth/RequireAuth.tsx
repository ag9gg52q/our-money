import { Navigate, Outlet, useLocation } from 'react-router'

import PageLoader from '../components/PageLoader/PageLoader'
import { useAuth } from './useAuth'

export default function RequireAuth() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <PageLoader />
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}
