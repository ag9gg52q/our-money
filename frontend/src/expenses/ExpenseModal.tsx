import { type SubmitEvent, useEffect, useState } from 'react'

import { fetchCategories } from '../api/categories'
import { getErrorMessage } from '../api/client'
import {
  type Expense,
  type ExpenseInput,
  createExpense,
  updateExpense,
} from '../api/expenses'
import { fetchCurrentHousehold } from '../api/households'
import { fetchSubcategories } from '../api/subcategories'
import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import Select, { type SelectOption } from '../components/Select/Select'
import TextField from '../components/TextField/TextField'
import { today } from '../utils/months'
import styles from './ExpenseModal.module.css'

type ExpenseModalProps = {
  expense?: Expense
  onClose: () => void
  onSaved: () => void
}

const FIELDS = ['date', 'person', 'category', 'subcategory', 'amount', 'note']

// În formular suma se scrie cu virgulă (10,59); API-ul lucrează cu punct (10.59).
function toDisplayAmount(value: string): string {
  return value.replace('.', ',')
}

function toApiAmount(value: string): string {
  return value.trim().replace(',', '.')
}

export default function ExpenseModal({
  expense,
  onClose,
  onSaved,
}: ExpenseModalProps) {
  const { user } = useAuth()

  const [date, setDate] = useState(expense?.date ?? today())
  const [person, setPerson] = useState(expense?.person ?? user?.id ?? '')
  const [category, setCategory] = useState(expense?.category ?? '')
  const [subcategory, setSubcategory] = useState(expense?.subcategory ?? '')
  const [amount, setAmount] = useState(toDisplayAmount(expense?.amount ?? ''))
  const [note, setNote] = useState(expense?.note ?? '')
  const [categoryOptions, setCategoryOptions] = useState<SelectOption[]>([])
  const [subcategoryOptions, setSubcategoryOptions] = useState<SelectOption[]>(
    [],
  )
  const [personOptions, setPersonOptions] = useState<SelectOption[]>([])
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Categoriile și persoanele: doar cele active, plus valoarea curentă a cheltuielii editate.
  useEffect(() => {
    let ignore = false

    Promise.all([fetchCategories(), fetchCurrentHousehold()])
      .then(([categories, household]) => {
        if (ignore) return
        setCategoryOptions(
          categories
            .filter((c) => c.is_active || c.id === expense?.category)
            .map((c) => ({ value: c.id, label: c.name })),
        )

        const people = household.members.map((m) => ({
          value: m.id,
          label: m.username,
        }))
        // Autorul unei cheltuieli vechi poate să fi plecat din gospodărie.
        if (expense && !people.some((p) => p.value === expense.person)) {
          people.push({ value: expense.person, label: expense.person_name })
        }
        setPersonOptions(people)
      })
      .catch((caught) => {
        if (!ignore) setError(caught)
      })

    return () => {
      ignore = true
    }
  }, [expense])

  // Subcategoriile se reîncarcă la fiecare schimbare a categoriei.
  useEffect(() => {
    if (!category) return
    let ignore = false

    fetchSubcategories(category)
      .then((subcategories) => {
        if (ignore) return
        setSubcategoryOptions(
          subcategories
            .filter((s) => s.is_active || s.id === expense?.subcategory)
            .map((s) => ({ value: s.id, label: s.name })),
        )
      })
      .catch((caught) => {
        if (!ignore) setError(caught)
      })

    return () => {
      ignore = true
    }
  }, [category, expense])

  function handleCategoryChange(value: string) {
    setCategory(value)
    setSubcategory('')
    setSubcategoryOptions([])
  }

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    const input: ExpenseInput = {
      date,
      person,
      category,
      subcategory,
      amount: toApiAmount(amount),
      note: note.trim(),
    }

    try {
      if (expense) {
        await updateExpense(expense.id, input)
      } else {
        await createExpense(input)
      }
      onSaved()
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const dateError = getErrorMessage(error, 'date')
  const personError = getErrorMessage(error, 'person')
  const categoryError = getErrorMessage(error, 'category')
  const subcategoryError = getErrorMessage(error, 'subcategory')
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
      title={expense ? 'Editează cheltuiala' : 'Adaugă cheltuială'}
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
          label="Categorie"
          value={category}
          options={categoryOptions}
          placeholder="Selectează categoria"
          autoFocus
          onChange={handleCategoryChange}
          error={categoryError}
        />
        <Select
          label="Subcategorie"
          value={subcategory}
          options={subcategoryOptions}
          placeholder={
            category ? 'Selectează subcategoria' : 'Selectează întâi categoria'
          }
          onChange={setSubcategory}
          error={subcategoryError}
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
