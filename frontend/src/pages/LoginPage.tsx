import { type SubmitEvent, useState } from 'react'
import { Link, useLocation } from 'react-router'

import { getErrorMessage } from '../api/client'
import { useAuth } from '../auth/useAuth'
import AuthLayout from '../components/AuthLayout/AuthLayout'
import Button from '../components/Button/Button'
import TextField from '../components/TextField/TextField'
import styles from './AuthPage.module.css'

type LoginLocationState = {
  username?: string
  signedUp?: boolean
} | null

export default function LoginPage() {
  const { login } = useAuth()
  const locationState = useLocation().state as LoginLocationState

  const [username, setUsername] = useState(locationState?.username ?? '')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login({ username, password })
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const formError = error
    ? (getErrorMessage(error, 'non_field_errors') ??
      getErrorMessage(error, 'detail') ??
      'Nu ne-am putut conecta la server. Încearcă din nou.')
    : undefined

  return (
    <AuthLayout
      title="Autentificare"
      subtitle="Intră în contul tău pentru a continua."
      footer={
        <>
          Nu ai cont? <Link to="/signup">Creează unul</Link>
        </>
      }
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {locationState?.signedUp && !error && (
          <p className={`${styles.alert} ${styles.success}`} role="status">
            Cont creat. Autentifică-te.
          </p>
        )}
        {formError && (
          <p className={`${styles.alert} ${styles.error}`} role="alert">
            {formError}
          </p>
        )}
        <TextField
          label="Utilizator"
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          error={getErrorMessage(error, 'username')}
        />
        <TextField
          label="Parolă"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={getErrorMessage(error, 'password')}
        />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Se verifică...' : 'Intră în cont'}
        </Button>
      </form>
    </AuthLayout>
  )
}
