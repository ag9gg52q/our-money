import { type SubmitEvent, useState } from 'react'

import { getErrorMessage } from '../api/client'
import { createHousehold } from '../api/households'
import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import TextField from '../components/TextField/TextField'
import styles from './HouseholdForm.module.css'

type CreateHouseholdModalProps = {
  onClose: () => void
}

export default function CreateHouseholdModal({
  onClose,
}: CreateHouseholdModalProps) {
  const { refreshUser } = useAuth()
  const [name, setName] = useState('')
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
      await createHousehold(name)
      await refreshUser()
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const nameError = getErrorMessage(error, 'name')
  const formError =
    error && !nameError
      ? (getErrorMessage(error, 'non_field_errors') ??
        getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  return (
    <Modal title="Creează o gospodărie" onClose={handleClose}>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <TextField
          label="Numele gospodăriei"
          maxLength={100}
          autoFocus
          value={name}
          onChange={(event) => setName(event.target.value)}
          error={nameError}
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
            {isSubmitting ? 'Se creează...' : 'Creează'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
