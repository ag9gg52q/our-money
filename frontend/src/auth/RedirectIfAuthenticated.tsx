import { Navigate, Outlet, useLocation } from 'react-router'

import PageLoader from '../components/PageLoader/PageLoader'
import { useAuth } from './useAuth'

type RedirectState = {
  from?: string
} | null

export default function RedirectIfAuthenticated() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <PageLoader />
  if (user) {
    const from = (location.state as RedirectState)?.from ?? '/'
    return <Navigate to={from} replace />
  }
  return <Outlet />
}
