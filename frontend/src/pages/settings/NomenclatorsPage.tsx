import { NavLink, Outlet } from 'react-router'

import { NOMENCLATORS } from './nomenclators'
import styles from './NomenclatorsPage.module.css'

export default function NomenclatorsPage() {
  return (
    <div className={styles.layout}>
      <nav className={styles.side} aria-label="Nomenclatoare">
        {NOMENCLATORS.map((item) => (
          <NavLink key={item.path} to={item.path}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className={styles.content}>
        <Outlet />
      </div>
    </div>
  )
}
