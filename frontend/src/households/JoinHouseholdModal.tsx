import { type SubmitEvent, useState } from 'react'

import { getErrorMessage } from '../api/client'
import { joinHousehold } from '../api/households'
import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import TextField from '../components/TextField/TextField'
import styles from './HouseholdForm.module.css'

type JoinHouseholdModalProps = {
  onClose: () => void
}

export default function JoinHouseholdModal({
  onClose,
}: JoinHouseholdModalProps) {
  const { refreshUser } = useAuth()
  const [inviteCode, setInviteCode] = useState('')
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await joinHousehold(inviteCode)
      await refreshUser()
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const inviteCodeError = getErrorMessage(error, 'invite_code')
  const formError =
    error && !inviteCodeError
      ? (getErrorMessage(error, 'non_field_errors') ??
        getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  return (
    <Modal title="Alătură-te unei gospodării" onClose={handleClose}>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <TextField
          label="Cod de invitație"
          maxLength={20}
          autoComplete="off"
          autoFocus
          value={inviteCode}
          onChange={(event) => setInviteCode(event.target.value.toUpperCase())}
          error={inviteCodeError}
        />
        <div className={styles.actions}>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Anulează
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Se alătură...' : 'Alătură-te'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
