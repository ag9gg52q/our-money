import { NavLink, Outlet, useNavigate } from 'react-router'

import { useAuth } from '../../auth/useAuth'
import styles from './Layout.module.css'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <NavLink to="/" className={styles.brand}>
          <span className={styles.logoMark}>OM</span>
          Our Money
        </NavLink>
        <nav className={styles.nav} aria-label="Navigare principală">
          <NavLink to="/" end>
            Acasă
          </NavLink>
          <NavLink to="/status">Status</NavLink>
        </nav>
        <div className={styles.user}>
          <span className={styles.roleBadge}>
            {user?.role === 'admin' ? 'ADMIN' : 'USER'}
          </span>
          <span className={styles.username}>{user?.username}</span>
          <button
            type="button"
            className={styles.logout}
            onClick={handleLogout}
          >
            Ieșire
          </button>
        </div>
      </header>
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  )
}
