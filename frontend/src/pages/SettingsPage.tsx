import { useState } from 'react'

import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import styles from './SettingsPage.module.css'

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
    <>
      <h1>Setări sistem</h1>
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Cod de invitație</h2>
        <div className={styles.codeRow}>
          <code className={styles.code}>{inviteCode}</code>
          <Button type="button" variant="secondary" onClick={handleCopy}>
            {copied ? 'Copiat' : 'Copiază'}
          </Button>
        </div>
      </section>
    </>
  )
}
