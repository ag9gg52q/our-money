import { BrowserRouter, Navigate, Route, Routes } from 'react-router'

import AuthProvider from './auth/AuthProvider'
import RedirectIfAuthenticated from './auth/RedirectIfAuthenticated'
import RequireAuth from './auth/RequireAuth'
import RequireNoRole from './auth/RequireNoRole'
import RequireRole from './auth/RequireRole'
import Layout from './components/Layout/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import SettingsPage from './pages/SettingsPage'
import ComingSoonSection from './pages/settings/ComingSoonSection'
import { NOMENCLATORS } from './pages/settings/nomenclators'
import NomenclatorsPage from './pages/settings/NomenclatorsPage'
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
                <Route element={<RequireRole role="admin" />}>
                  <Route path="settings" element={<SettingsPage />}>
                    <Route
                      index
                      element={<Navigate to="nomenclatoare" replace />}
                    />
                    <Route path="nomenclatoare" element={<NomenclatorsPage />}>
                      <Route
                        index
                        element={<Navigate to="categorii" replace />}
                      />
                      {NOMENCLATORS.map((item) => (
                        <Route
                          key={item.path}
                          path={item.path}
                          element={
                            <ComingSoonSection
                              title={item.label}
                              description={item.description}
                            />
                          }
                        />
                      ))}
                    </Route>
                    <Route
                      path="template-uri"
                      element={
                        <ComingSoonSection
                          title="Template-uri"
                          description="Un template precompletează formularul de cheltuială."
                        />
                      }
                    />
                    <Route
                      path="rapoarte"
                      element={
                        <ComingSoonSection
                          title="Rapoarte"
                          description="Rapoarte personalizate, afișate pe pagina de start."
                        />
                      }
                    />
                  </Route>
                </Route>
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
