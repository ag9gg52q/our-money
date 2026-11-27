import { useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type OpenDebt, cancelDebt } from '../api/expenses'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import { formatAmount } from '../utils/format'
import styles from './ExpenseModal.module.css'

type CancelDebtModalProps = {
  debt: OpenDebt
  onClose: () => void
  onCanceled: () => void
}

export default function CancelDebtModal({
  debt,
  onClose,
  onCanceled,
}: CancelDebtModalProps) {
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleConfirm() {
    setError(null)
    setIsSubmitting(true)
    try {
      await cancelDebt(debt.id)
      onCanceled()
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
    <Modal title="Anulează datoria" onClose={handleClose}>
      <div className={styles.form}>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <p className={styles.text}>
          <strong>{debt.debtor_label}</strong> nu mai datorează{' '}
          <strong>{formatAmount(debt.amount)}</strong>. Cheltuiala lui{' '}
          {debt.payer_name} rămâne neschimbată.
        </p>
        <div className={styles.actions}>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Renunță
          </Button>
          <Button
            type="button"
            variant="danger"
            onClick={handleConfirm}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Se anulează...' : 'Anulează datoria'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
