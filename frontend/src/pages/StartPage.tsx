import { useState } from 'react'
import { useNavigate } from 'react-router'

import { useAuth } from '../auth/useAuth'
import AuthLayout from '../components/AuthLayout/AuthLayout'
import Button from '../components/Button/Button'
import CreateHouseholdModal from '../households/CreateHouseholdModal'
import JoinHouseholdModal from '../households/JoinHouseholdModal'
import styles from './StartPage.module.css'

export default function StartPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isJoinOpen, setIsJoinOpen] = useState(false)

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <AuthLayout
      title={`Bine ai venit, ${user?.username}!`}
      subtitle="Ca să începi, creează o gospodărie sau alătură-te uneia existente."
      footer={
        <>
          Nu ești tu?{' '}
          <button
            type="button"
            className={styles.linkButton}
            onClick={handleLogout}
          >
            Ieșire
          </button>
        </>
      }
    >
      <div className={styles.actions}>
        <Button type="button" onClick={() => setIsCreateOpen(true)}>
          Creează o gospodărie
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => setIsJoinOpen(true)}
        >
          Alătură-te unei gospodării
        </Button>
      </div>
      {isCreateOpen && (
        <CreateHouseholdModal onClose={() => setIsCreateOpen(false)} />
      )}
      {isJoinOpen && (
        <JoinHouseholdModal onClose={() => setIsJoinOpen(false)} />
      )}
    </AuthLayout>
  )
}
