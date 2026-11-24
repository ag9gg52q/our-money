import { type SubmitEvent, useEffect, useId, useState } from 'react'

import { getErrorMessage } from '../api/client'
import { fetchCurrentHousehold } from '../api/households'
import {
  type SavingsEntry,
  type SavingsEntryInput,
  createSavingsEntry,
  updateSavingsEntry,
} from '../api/savings'
import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import Select, { type SelectOption } from '../components/Select/Select'
import TextField from '../components/TextField/TextField'
import { today } from '../utils/months'
import { absoluteAmount, isWithdrawal } from './amount'
import styles from './SavingsModal.module.css'

type Kind = 'deposit' | 'withdrawal'

const KINDS: { value: Kind; label: string }[] = [
  { value: 'deposit', label: 'Depunere' },
  { value: 'withdrawal', label: 'Retragere' },
]
const FIELDS = ['date', 'person', 'amount', 'note']

type SavingsEntryModalProps = {
  entry?: SavingsEntry
  onClose: () => void
  onSaved: () => void
}

function toDisplayAmount(value: string): string {
  return absoluteAmount(value).replace('.', ',')
}

function toApiAmount(value: string, kind: Kind): string {
  const amount = value.trim().replace(',', '.')
  return kind === 'withdrawal' && amount ? `-${amount}` : amount
}

export default function SavingsEntryModal({
  entry,
  onClose,
  onSaved,
}: SavingsEntryModalProps) {
  const { user } = useAuth()
  const kindName = useId()

  const [kind, setKind] = useState<Kind>(
    entry && isWithdrawal(entry.amount) ? 'withdrawal' : 'deposit',
  )
  const [amount, setAmount] = useState(toDisplayAmount(entry?.amount ?? ''))
  const [date, setDate] = useState(entry?.date ?? today())
  const [person, setPerson] = useState(entry?.person ?? user?.id ?? '')
  const [note, setNote] = useState(entry?.note ?? '')
  const [personOptions, setPersonOptions] = useState<SelectOption[]>([])
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    let ignore = false

    fetchCurrentHousehold().then((household) => {
      if (ignore) return
      const people = household.members.map((m) => ({
        value: m.id,
        label: m.username,
      }))

      if (entry && !people.some((p) => p.value === entry.person_name)) {
        people.push({ value: entry.person, label: entry.person_name })
      }
      setPersonOptions(people)
    })

    return () => {
      ignore = true
    }
  }, [entry])

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    const input: SavingsEntryInput = {
      date,
      person,
      amount: toApiAmount(amount, kind),
      note: note.trim(),
    }

    try {
      if (entry) {
        await updateSavingsEntry(entry.id, input)
      } else {
        await createSavingsEntry(input)
      }
      onSaved()
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const amountError = getErrorMessage(error, 'amount')
  const dateError = getErrorMessage(error, 'date')
  const personError = getErrorMessage(error, 'person')
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
      title={entry ? 'Editează operațiunea' : 'Operațiune nouă'}
      onClose={handleClose}
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}

        <fieldset className={styles.kinds}>
          <legend className={styles.kindsLegend}>Tip</legend>
          <div className={styles.kindOptions}>
            {KINDS.map((option) => (
              <label key={option.value} className={styles.kind}>
                <input
                  type="radio"
                  className={styles.kindInput}
                  name={kindName}
                  value={option.value}
                  checked={kind === option.value}
                  onChange={() => setKind(option.value)}
                />
                {option.label}
              </label>
            ))}
          </div>
        </fieldset>

        <div className={styles.row2}>
          <TextField
            label="Sumă (lei)"
            inputMode="decimal"
            placeholder="0,00"
            value={amount}
            data-autofocus
            onChange={(event) => setAmount(toDisplayAmount(event.target.value))}
            error={amountError}
          />
          <TextField
            label="Data"
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            error={dateError}
          />
        </div>
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
            {isSubmitting ? 'Se salvează...' : 'Salvează operațiunea'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
