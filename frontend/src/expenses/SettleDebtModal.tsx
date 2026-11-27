import { type SubmitEvent, useState } from 'react'

import { getErrorMessage } from '../api/client'
import { type OpenDebt, settleDebt } from '../api/expenses'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import TextField from '../components/TextField/TextField'
import { formatAmount } from '../utils/format'
import { toApiAmount, toDisplayAmount } from './amount'
import styles from './ExpenseModal.module.css'

type SettleDebtModalProps = {
  debt: OpenDebt
  onClose: () => void
  onSettled: () => void
}

export default function SettleDebtModal({
  debt,
  onClose,
  onSettled,
}: SettleDebtModalProps) {
  const [amount, setAmount] = useState(toDisplayAmount(debt.amount))
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
      await settleDebt(debt.id, toApiAmount(amount))
      onSettled()
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const amountError = getErrorMessage(error, 'amount')
  const formError =
    error && !amountError
      ? (getErrorMessage(error, 'non_field_errors') ??
        getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  const effect = debt.debtor
    ? `Suma trece pe numele lui ${debt.debtor_label}, ca o cheltuială a lui, iar cheltuiala lui ${debt.payer_name} scade cu atât.`
    : `Cheltuiala lui ${debt.payer_name} scade cu suma întoarsă.`

  return (
    <Modal title="Datorie întoarsă" onClose={handleClose}>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <p className={styles.text}>
          <strong>{debt.debtor_label}</strong> datorează{' '}
          <strong>{formatAmount(debt.amount)}</strong>. {effect} Dacă a întors
          doar o parte, restul rămâne datorie deschisă.
        </p>
        <TextField
          label="Suma întoarsă (lei)"
          inputMode="decimal"
          placeholder="0,00"
          data-autofocus
          value={amount}
          onChange={(event) => setAmount(toDisplayAmount(event.target.value))}
          error={amountError}
        />
        <div className={styles.actions}>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Renunță
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Se salvează...' : 'Confirmă'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
