import { type SubmitEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { signup } from '../api/auth'
import { getErrorMessage } from '../api/client'
import AuthLayout from '../components/AuthLayout/AuthLayout'
import Button from '../components/Button/Button'
import TextField from '../components/TextField/TextField'
import styles from './AuthPage.module.css'

export default function SignupPage() {
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [confirmError, setConfirmError] = useState<string>()
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (password !== passwordConfirm) {
      setConfirmError('Parolele nu coincid.')
      return
    }
    setConfirmError(undefined)

    setIsSubmitting(true)
    try {
      await signup({ username, password })
      navigate('/login', { replace: true, state: { username, signedUp: true } })
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const formError =
    error &&
    !getErrorMessage(error, 'username') &&
    !getErrorMessage(error, 'password')
      ? (getErrorMessage(error, 'non_field_errors') ??
        getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  return (
    <AuthLayout
      title="Creează cont"
      subtitle="Alege un nume de utilizator și o parolă."
      footer={
        <>
          Ai deja cont? <Link to="/login">Autentifică-te</Link>
        </>
      }
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
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
          autoComplete="new-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={getErrorMessage(error, 'password')}
        />
        <TextField
          label="Confirmă parola"
          type="password"
          autoComplete="new-password"
          value={passwordConfirm}
          onChange={(event) => setPasswordConfirm(event.target.value)}
          error={confirmError}
        />
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Se creează contul...' : 'Creează cont'}
        </Button>
      </form>
    </AuthLayout>
  )
}
