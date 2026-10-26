import { useNavigate } from 'react-router'

import { useAuth } from '../auth/useAuth'
import AuthLayout from '../components/AuthLayout/AuthLayout'
import Button from '../components/Button/Button'
import styles from './StartPage.module.css'

// Schiță: crearea și alăturarea la o gospodărie vor fi implementate ulterior.
export default function StartPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

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
        <Button type="button" disabled>
          Creează o gospodărie
        </Button>
        <Button type="button" variant="secondary" disabled>
          Alătură-te unei gospodării
        </Button>
        <p className={styles.note}>Disponibil în curând.</p>
      </div>
    </AuthLayout>
  )
}
