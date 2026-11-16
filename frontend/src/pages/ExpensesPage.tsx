import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'

import { fetchCategories } from '../api/categories'
import { type Expense, type ExpenseList, fetchExpenses } from '../api/expenses'
import { fetchCurrentHousehold } from '../api/households'
import Button from '../components/Button/Button'
import Select, { type SelectOption } from '../components/Select/Select'
import DeleteExpenseModal from '../expenses/DeleteExpenseModal'
import ExpenseModal from '../expenses/ExpenseModal'
import { formatAmount, formatDate } from '../utils/format'
import {
  currentMonth,
  formatMonth,
  isValidMonth,
  monthRange,
  shiftMonth,
} from '../utils/months'
import styles from './ExpensesPage.module.css'

type LoadState = 'loading' | 'ready' | 'error'

const ALL_CATEGORIES: SelectOption = { value: '', label: 'Toate categoriile' }
const ALL_PEOPLE: SelectOption = { value: '', label: 'Toate persoanele' }

export default function ExpensesPage() {
  const [data, setData] = useState<ExpenseList | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [categoryOptions, setCategoryOptions] = useState([ALL_CATEGORIES])
  const [personOptions, setPersonOptions] = useState([ALL_PEOPLE])
  const [editing, setEditing] = useState<Expense | 'new' | null>(null)
  const [deleting, setDeleting] = useState<Expense | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  // Filtrele stau în URL (?month=2026-11&category=...&person=...), nu în state.
  const [searchParams, setSearchParams] = useSearchParams()
  const monthParam = searchParams.get('month')
  const month =
    monthParam && isValidMonth(monthParam) ? monthParam : currentMonth()
  const category = searchParams.get('category') ?? ''
  const person = searchParams.get('person') ?? ''

  useEffect(() => {
    let ignore = false

    fetchExpenses({ ...monthRange(month), category, person })
      .then((list) => {
        if (ignore) return
        setData(list)
        setLoadState('ready')
      })
      .catch(() => {
        if (!ignore) setLoadState('error')
      })

    return () => {
      ignore = true
    }
  }, [month, category, person, reloadKey])

  useEffect(() => {
    let ignore = false

    Promise.all([fetchCategories(), fetchCurrentHousehold()])
      .then(([categories, household]) => {
        if (ignore) return
        setCategoryOptions([
          ALL_CATEGORIES,
          ...categories.map((c) => ({ value: c.id, label: c.name })),
        ])
        setPersonOptions([
          ALL_PEOPLE,
          ...household.members.map((m) => ({ value: m.id, label: m.username })),
        ])
      })
      .catch(() => {})

    return () => {
      ignore = true
    }
  }, [])

  function updateFilter(key: string, value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value) next.set(key, value)
      else next.delete(key)
      return next
    })
  }

  // Totalul se calculează pe server, iar cheltuiala salvată poate să nu mai
  // corespundă filtrelor, așa că cerem lista din nou în loc s-o modificăm local.
  function handleSaved() {
    setEditing(null)
    setReloadKey((key) => key + 1)
  }

  function handleDeleted() {
    setDeleting(null)
    setReloadKey((key) => key + 1)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Cheltuieli</h1>
          <p className={styles.description}>
            Toate cheltuielile gospodăriei, de la toți membrii.
          </p>
        </div>
        <Button type="button" onClick={() => setEditing('new')}>
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M12 5v14M5 12h14" />
          </svg>
          Adaugă cheltuială
        </Button>
      </div>

      <section className={styles.card} aria-label="Lista cheltuielilor">
        <div className={styles.filters}>
          <div className={styles.month}>
            <button
              type="button"
              className={styles.monthButton}
              aria-label="Luna anterioară"
              onClick={() => updateFilter('month', shiftMonth(month, -1))}
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="m15 18-6-6 6-6" />
              </svg>
            </button>
            <span className={styles.monthLabel} aria-live="polite">
              {formatMonth(month)}
            </span>
            <button
              type="button"
              className={styles.monthButton}
              aria-label="Luna următoare"
              onClick={() => updateFilter('month', shiftMonth(month, 1))}
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="m9 18 6-6-6-6" />
              </svg>
            </button>
          </div>

          <div className={styles.selects}>
            <Select
              label="Categorie"
              value={category}
              options={categoryOptions}
              onChange={(value) => updateFilter('category', value)}
            />
            <Select
              label="Persoană"
              value={person}
              options={personOptions}
              onChange={(value) => updateFilter('person', value)}
            />
          </div>
        </div>

        {loadState === 'loading' && (
          <p className={styles.message}>Se încarcă...</p>
        )}

        {loadState === 'error' && (
          <p className={styles.alert} role="alert">
            Nu am putut încărca cheltuielile. Reîncarcă pagina.
          </p>
        )}

        {loadState === 'ready' && data?.expenses.length === 0 && (
          <p className={styles.empty}>
            Nu există cheltuieli pentru filtrele alese.
          </p>
        )}

        {loadState === 'ready' && data && data.expenses.length > 0 && (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th scope="col">Data</th>
                  <th scope="col">Categorie</th>
                  <th scope="col">Notă</th>
                  <th scope="col">Persoană</th>
                  <th scope="col" className={styles.amount}>
                    Sumă
                  </th>
                  <th scope="col">
                    <span className={styles.srOnly}>Acțiuni</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.expenses.map((expense) => (
                  <tr key={expense.id}>
                    <td className={styles.date}>{formatDate(expense.date)}</td>
                    <td>
                      <span className={styles.category}>
                        {expense.category_name}
                      </span>
                      <span className={styles.subcategory}>
                        {expense.subcategory_name}
                      </span>
                    </td>
                    <td className={styles.note}>{expense.note}</td>
                    <td>{expense.person_name}</td>
                    <td className={styles.amount}>
                      {formatAmount(expense.amount)}
                    </td>
                    <td className={styles.actionsCell}>
                      <button
                        type="button"
                        className={styles.iconButton}
                        aria-label={`Editează cheltuiala din ${formatDate(expense.date)}`}
                        onClick={() => setEditing(expense)}
                      >
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          aria-hidden="true"
                        >
                          <path d="M4 20h4L19 9l-4-4L4 16z" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        className={`${styles.iconButton} ${styles.iconDanger}`}
                        aria-label={`Șterge cheltuiala din ${formatDate(expense.date)}`}
                        onClick={() => setDeleting(expense)}
                      >
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          aria-hidden="true"
                        >
                          <path d="M4 7h16M10 11v6M14 11v6M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-12M9 7V4h6v3" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <th scope="row" colSpan={4}>
                    Total
                  </th>
                  <td className={styles.amount}>{formatAmount(data.total)}</td>
                  <td />
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </section>

      {editing !== null && (
        <ExpenseModal
          expense={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
          onSaved={handleSaved}
        />
      )}

      {deleting && (
        <DeleteExpenseModal
          expense={deleting}
          onClose={() => setDeleting(null)}
          onDeleted={handleDeleted}
        />
      )}
    </div>
  )
}
