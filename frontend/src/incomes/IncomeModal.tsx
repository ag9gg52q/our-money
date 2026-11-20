import { type SubmitEvent, useEffect, useState } from 'react'

import { getErrorMessage } from '../api/client'
import { fetchIncomeSources } from '../api/income_sources'
import {
  type Income,
  type IncomeInput,
  createIncome,
  updateIncome,
} from '../api/incomes'
import { fetchCurrentHousehold } from '../api/households'
import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import Select, { type SelectOption } from '../components/Select/Select'
import TextField from '../components/TextField/TextField'
import { today } from '../utils/months'
import styles from './IncomeModal.module.css'

type IncomeModalProps = {
  income?: Income
  onClose: () => void
  onSaved: () => void
}

const FIELDS = ['date', 'person', 'income_source', 'amount', 'note']

function toDisplayAmount(value: string): string {
  return value.replace('.', ',')
}

function toApiAmount(value: string): string {
  return value.trim().replace(',', '.')
}

export default function IncomeModal({
  income,
  onClose,
  onSaved,
}: IncomeModalProps) {
  const { user } = useAuth()

  const [date, setDate] = useState(income?.date ?? today())
  const [person, setPerson] = useState(income?.person ?? user?.id ?? '')
  const [incomeSource, setIncomeSource] = useState(income?.income_source ?? '')
  const [amount, setAmount] = useState(toDisplayAmount(income?.amount ?? ''))
  const [note, setNote] = useState(income?.note ?? '')
  const [incomeSourceOptions, setIncomeSourceOptions] = useState<
    SelectOption[]
  >([])
  const [personOptions, setPersonOptions] = useState<SelectOption[]>([])
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    let ignore = false

    Promise.all([fetchIncomeSources(), fetchCurrentHousehold()])
      .then(([income_sources, household]) => {
        if (ignore) return
        setIncomeSourceOptions(
          income_sources
            .filter((c) => c.is_active || c.id === income?.income_source)
            .map((c) => ({ value: c.id, label: c.name })),
        )

        const people = household.members.map((m) => ({
          value: m.id,
          label: m.username,
        }))
        if (income && !people.some((p) => p.value === income.person)) {
          people.push({ value: income.person, label: income.person_name })
        }
        setPersonOptions(people)
      })
      .catch((caught) => {
        if (!ignore) setError(caught)
      })

    return () => {
      ignore = true
    }
  }, [income])

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    const input: IncomeInput = {
      date,
      person,
      income_source: incomeSource,
      amount: toApiAmount(amount),
      note: note.trim(),
    }

    try {
      if (income) {
        await updateIncome(income.id, input)
      } else {
        await createIncome(input)
      }
      onSaved()
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const dateError = getErrorMessage(error, 'date')
  const personError = getErrorMessage(error, 'person')
  const incomeSourceError = getErrorMessage(error, 'income_source')
  const amountError = getErrorMessage(error, 'amount')
  const noteError = getErrorMessage(error, 'note')

  const hasFieldError = FIELDS.some((field) => getErrorMessage(error, field))
  const formError =
    error && !hasFieldError
      ? (getErrorMessage(error, 'non_field_errors') ??
        getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  return (
    <Modal
      title={income ? 'Editează venitul' : 'Adaugă venit'}
      onClose={handleClose}
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}

        <TextField
          label="Data"
          type="date"
          value={date}
          onChange={(event) => setDate(event.target.value)}
          error={dateError}
        />
        <Select
          label="Sursă de venit"
          value={incomeSource}
          options={incomeSourceOptions}
          placeholder="Selectează sursa de venit"
          autoFocus
          onChange={setIncomeSource}
          error={incomeSourceError}
        />
        <Select
          label="Persoană"
          value={person}
          options={personOptions}
          placeholder="Selectează persoana"
          onChange={setPerson}
          error={personError}
        />
        <TextField
          label="Notă (opțional)"
          maxLength={255}
          value={note}
          onChange={(event) => setNote(event.target.value)}
          error={noteError}
        />
        <TextField
          label="Sumă (lei)"
          inputMode="decimal"
          placeholder="0,00"
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
