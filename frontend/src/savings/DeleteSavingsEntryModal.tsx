import { useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type SavingsEntry, deleteSavingsEntry } from '../api/savings'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import { formatAmount, formatDate } from '../utils/format'
import { absoluteAmount, isWithdrawal } from './amount'
import styles from './SavingsModal.module.css'

type DeleteSavingsEntryModalProps = {
  entry: SavingsEntry
  onClose: () => void
  onDeleted: () => void
}

export default function DeleteSavingsEntryModal({
  entry,
  onClose,
  onDeleted,
}: DeleteSavingsEntryModalProps) {
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleConfirm() {
    setError(null)
    setIsSubmitting(true)
    try {
      await deleteSavingsEntry(entry.id)
      onDeleted()
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

  const kindLabel = isWithdrawal(entry.amount) ? 'retragerea' : 'depunerea'

  return (
    <Modal title="Șterge operațiunea" onClose={handleClose}>
      <div className={styles.form}>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <p className={styles.text}>
          Ștergi {kindLabel} de{' '}
          <strong>{formatAmount(absoluteAmount(entry.amount))}</strong> din{' '}
          {formatDate(entry.date)}. Acțiunea nu poate fi anulată.
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
          <Button
            type="button"
            variant="danger"
            onClick={handleConfirm}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Se șterge...' : 'Șterge'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
