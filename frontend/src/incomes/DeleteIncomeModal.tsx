import { useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type Income, deleteIncome } from '../api/incomes'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import { formatAmount, formatDate } from '../utils/format'
import styles from './IncomeModal.module.css'

type DeleteIncomeModalProps = {
  income: Income
  onClose: () => void
  onDeleted: () => void
}

export default function DeleteIncomeModal({
  income,
  onClose,
  onDeleted,
}: DeleteIncomeModalProps) {
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleConfirm() {
    setError(null)
    setIsSubmitting(true)
    try {
      await deleteIncome(income.id)
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

  return (
    <Modal title="Șterge venitul" onClose={handleClose}>
      <div className={styles.form}>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <p className={styles.text}>
          Ștergi venitul de <strong>{formatAmount(income.amount)}</strong> din{' '}
          {formatDate(income.date)} ({income.income_source_name}). Acțiunea nu
          poate fi anulată.
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
