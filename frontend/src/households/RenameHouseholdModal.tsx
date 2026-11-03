import { type SubmitEvent, useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type HouseholdDetails, renameHousehold } from '../api/households'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import TextField from '../components/TextField/TextField'
import styles from './HouseholdForm.module.css'

type RenameHouseholdModalProps = {
  household: HouseholdDetails
  onClose: () => void
  onSaved: (household: HouseholdDetails) => void
}

export default function RenameHouseholdModal({
  household,
  onClose,
  onSaved,
}: RenameHouseholdModalProps) {
  const [name, setName] = useState(household.name)
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
      onSaved(await renameHousehold(name))
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const nameError = getErrorMessage(error, 'name')
  const formError =
    error && !nameError
      ? (getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  return (
    <Modal title="Redenumește gospodăria" onClose={handleClose}>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <TextField
          label="Denumire"
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
            {isSubmitting ? 'Se salvează...' : 'Salvează'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
