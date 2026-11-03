import { useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type HouseholdMember, makeAdmin } from '../api/households'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import styles from './HouseholdForm.module.css'

type MakeAdminModalProps = {
  member: HouseholdMember
  onClose: () => void
  onSaved: (member: HouseholdMember) => void
}

export default function MakeAdminModal({
  member,
  onClose,
  onSaved,
}: MakeAdminModalProps) {
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleConfirm() {
    setError(null)
    setIsSubmitting(true)
    try {
      onSaved(await makeAdmin(member.id))
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
    <Modal title="Fă administrator" onClose={handleClose}>
      <div className={styles.form}>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <p className={styles.text}>
          <strong>{member.username}</strong> va putea modifica setările
          gospodăriei. Rolul de administrator nu mai poate fi retras.
        </p>
        <div className={styles.actions}>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Anulează
          </Button>
          <Button type="button" onClick={handleConfirm} disabled={isSubmitting}>
            {isSubmitting ? 'Se salvează...' : 'Fă administrator'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
