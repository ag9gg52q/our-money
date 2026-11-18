import { useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type Expense, deleteExpense } from '../api/expenses'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import { formatAmount, formatDate } from '../utils/format'
import styles from './ExpenseModal.module.css'

type DeleteExpenseModalProps = {
  expense: Expense
  onClose: () => void
  onDeleted: () => void
}

export default function DeleteExpenseModal({
  expense,
  onClose,
  onDeleted,
}: DeleteExpenseModalProps) {
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleConfirm() {
    setError(null)
    setIsSubmitting(true)
    try {
      await deleteExpense(expense.id)
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
    <Modal title="Șterge cheltuiala" onClose={handleClose}>
      <div className={styles.form}>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <p className={styles.text}>
          Ștergi cheltuiala de <strong>{formatAmount(expense.amount)}</strong>{' '}
          din {formatDate(expense.date)} ({expense.category_name} /{' '}
          {expense.subcategory_name}). Acțiunea nu poate fi anulată.
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
