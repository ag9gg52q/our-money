import { NavLink, Outlet } from 'react-router'

import styles from './SettingsPage.module.css'

const TABS = [
  { to: 'nomenclatoare', label: 'Nomenclatoare' },
  { to: 'template-uri', label: 'Template-uri' },
  { to: 'rapoarte', label: 'Rapoarte' },
]

export default function SettingsPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Setări sistem</h1>
      <nav className={styles.tabs} aria-label="Secțiuni setări">
        {TABS.map((tab) => (
          <NavLink key={tab.to} to={tab.to}>
            {tab.label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
