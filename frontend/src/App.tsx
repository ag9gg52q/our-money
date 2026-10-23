import { BrowserRouter, Route, Routes } from 'react-router'

import AuthProvider from './auth/AuthProvider'
import RedirectIfAuthenticated from './auth/RedirectIfAuthenticated'
import RequireAuth from './auth/RequireAuth'
import RequireNoRole from './auth/RequireNoRole'
import RequireRole from './auth/RequireRole'
import Layout from './components/Layout/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import SignupPage from './pages/SignupPage'
import StartPage from './pages/StartPage'
import StatusPage from './pages/StatusPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<RedirectIfAuthenticated />}>
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />
          </Route>
          <Route element={<RequireAuth />}>
            <Route element={<RequireNoRole />}>
              <Route path="start" element={<StartPage />} />
            </Route>
            <Route element={<RequireRole />}>
              <Route element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="status" element={<StatusPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
