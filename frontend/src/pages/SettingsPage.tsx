import { useState } from 'react'
import { NavLink, Outlet } from 'react-router'

import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import styles from './SettingsPage.module.css'

const TABS = [
  { to: 'nomenclatoare', label: 'Nomenclatoare' },
  { to: 'template-uri', label: 'Template-uri' },
  { to: 'rapoarte', label: 'Rapoarte' },
]

export default function SettingsPage() {
  const { user } = useAuth()
  const [copied, setCopied] = useState(false)
  const inviteCode = user?.household?.invite_code

  async function handleCopy() {
    if (!inviteCode) return
    await navigator.clipboard.writeText(inviteCode)
    setCopied(true)
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Setări sistem</h1>

      {/* Temporar aici: se mută în Nomenclatoare → Gospodărie. */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Cod de invitație</h2>
        <div className={styles.codeRow}>
          <code className={styles.code}>{inviteCode}</code>
          <Button type="button" variant="secondary" onClick={handleCopy}>
            {copied ? 'Copiat' : 'Copiază'}
          </Button>
        </div>
      </section>

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
