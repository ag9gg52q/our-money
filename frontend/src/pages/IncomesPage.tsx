import { Fragment, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'

import { type Income, type IncomeList, fetchIncomes } from '../api/incomes'
import { fetchCurrentHousehold } from '../api/households'
import Avatar from '../components/Avatar/Avatar'
import Button from '../components/Button/Button'
import Select, { type SelectOption } from '../components/Select/Select'
import DeleteIncomeModal from '../incomes/DeleteIncomeModal'
import IncomeModal from '../incomes/IncomeModal'
import { formatAmount, formatDate } from '../utils/format'
import {
  currentMonth,
  formatMonth,
  isValidMonth,
  monthRange,
  shiftMonth,
} from '../utils/months'
import styles from './IncomesPage.module.css'

type LoadState = 'loading' | 'ready' | 'error'

const ALL_PEOPLE: SelectOption = { value: '', label: 'Toate persoanele' }

export default function IncomesPage() {
  const [data, setData] = useState<IncomeList | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [personOptions, setPersonOptions] = useState([ALL_PEOPLE])
  const [editing, setEditing] = useState<Income | 'new' | null>(null)
  const [deleting, setDeleting] = useState<Income | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [openNoteId, setOpenNoteId] = useState<string | null>(null)

  // Filtrele stau în URL (?month=2026-11&person=...), nu în state.
  const [searchParams, setSearchParams] = useSearchParams()
  const monthParam = searchParams.get('month')
  const month =
    monthParam && isValidMonth(monthParam) ? monthParam : currentMonth()
  const person = searchParams.get('person') ?? ''

  useEffect(() => {
    let ignore = false

    fetchIncomes({ ...monthRange(month), person })
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
  }, [month, person, reloadKey])

  useEffect(() => {
    let ignore = false

    fetchCurrentHousehold()
      .then((household) => {
        if (ignore) return
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

  function handleSaved() {
    setEditing(null)
    setReloadKey((key) => key + 1)
  }

  function handleDeleted() {
    setDeleting(null)
    setReloadKey((key) => key + 1)
  }

  function toggleNote(id: string) {
    setOpenNoteId((current) => (current === id ? null : id))
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Venituri</h1>
          <p className={styles.description}>
            Toate veniturile gospodăriei, de la toți membrii.
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
          Adaugă venit
        </Button>
      </div>

      <section className={styles.card} aria-label="Lista veniturilor">
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
            Nu am putut încărca veniturile. Reîncarcă pagina.
          </p>
        )}

        {loadState === 'ready' && data?.incomes.length === 0 && (
          <p className={styles.empty}>
            Nu există venituri pentru filtrele alese.
          </p>
        )}

        {loadState === 'ready' && data && data.incomes.length > 0 && (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <colgroup>
                <col className={styles.colPerson} />
                <col className={styles.colDate} />
                <col />
                <col className={styles.colAmount} />
                <col className={styles.colActions} />
              </colgroup>
              <thead>
                <tr>
                  <th scope="col">
                    <span className={styles.srOnly}>Persoană</span>
                  </th>
                  <th scope="col">Data</th>
                  <th scope="col">Sursă de venit</th>
                  <th scope="col" className={styles.amount}>
                    Sumă
                  </th>
                  <th scope="col">
                    <span className={styles.srOnly}>Acțiuni</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.incomes.map((income) => (
                  <Fragment key={income.id}>
                    <tr
                      className={
                        openNoteId === income.id ? styles.rowOpen : undefined
                      }
                    >
                      <td>
                        <Avatar name={income.person_name} />
                      </td>
                      <td className={styles.date}>{formatDate(income.date)}</td>
                      <td>
                        <span className={styles.category}>
                          {income.income_source_name}
                        </span>
                      </td>
                      <td className={styles.amount}>
                        {formatAmount(income.amount)}
                      </td>
                      <td className={styles.actionsCell}>
                        {income.note ? (
                          <button
                            type="button"
                            className={styles.iconButton}
                            aria-label={
                              openNoteId === income.id
                                ? 'Ascunde nota'
                                : 'Arată nota'
                            }
                            aria-expanded={openNoteId === income.id}
                            aria-controls={`note-${income.id}`}
                            onClick={() => toggleNote(income.id)}
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
                              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z" />
                              <path d="M8 9h8M8 13h5" />
                            </svg>
                          </button>
                        ) : (
                          <span
                            className={styles.iconPlaceholder}
                            aria-hidden="true"
                          />
                        )}
                        <button
                          type="button"
                          className={styles.iconButton}
                          aria-label={`Editează venitul din ${formatDate(income.date)}`}
                          onClick={() => setEditing(income)}
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
                          aria-label={`Șterge venitul din ${formatDate(income.date)}`}
                          onClick={() => setDeleting(income)}
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
                    {openNoteId === income.id && (
                      <tr id={`note-${income.id}`} className={styles.noteRow}>
                        <td colSpan={5}>
                          <p className={styles.noteText}>{income.note}</p>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <th scope="row" colSpan={3}>
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
        <IncomeModal
          income={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
          onSaved={handleSaved}
        />
      )}

      {deleting && (
        <DeleteIncomeModal
          income={deleting}
          onClose={() => setDeleting(null)}
          onDeleted={handleDeleted}
        />
      )}
    </div>
  )
}
