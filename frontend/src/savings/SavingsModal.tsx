import { useEffect, useState } from 'react'

import {
  type SavingsEntry,
  type SavingsEntryList,
  fetchSavingsEntries,
} from '../api/savings'
import Avatar from '../components/Avatar/Avatar'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import { formatAmount, formatDate } from '../utils/format'
import { absoluteAmount, isWithdrawal } from './amount'
import DeleteSavingsEntryModal from './DeleteSavingsEntryModal'
import SavingsEntryModal from './SavingsEntryModal'
import styles from './SavingsModal.module.css'

type LoadState = 'loading' | 'ready' | 'error'

type SavingsModalProps = {
  onClose: () => void
}

function formatSignedAmount(amount: string): string {
  const sign = isWithdrawal(amount) ? '−' : '+'
  return `${sign}${formatAmount(absoluteAmount(amount))}`
}

export default function SavingsModal({ onClose }: SavingsModalProps) {
  const [data, setData] = useState<SavingsEntryList | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [editing, setEditing] = useState<SavingsEntry | 'new' | null>(null)
  const [deleting, setDeleting] = useState<SavingsEntry | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [openNoteId, setOpenNoteId] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false

    fetchSavingsEntries()
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
  }, [reloadKey])

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
    <Modal title="Economii" size="wide" onClose={onClose}>
      <div className={styles.content}>
        {loadState === 'loading' && (
          <p className={styles.message}>Se încarcă...</p>
        )}

        {loadState === 'error' && (
          <p className={styles.alert} role="alert">
            Nu am putut încărca economiile. Încearcă din nou.
          </p>
        )}

        {loadState === 'ready' && data && (
          <>
            <div className={styles.balance}>
              <span className={styles.balanceLabel}>Sold economii</span>
              <strong className={styles.balanceValue}>
                {formatAmount(data.balance)}
              </strong>
              <span className={styles.balanceSummary}>
                Depuneri {formatAmount(data.deposits)} · Retrageri{' '}
                {formatAmount(absoluteAmount(data.withdrawals))}
              </span>
            </div>

            <div className={styles.listHeader}>
              <h3 className={styles.listTitle}>Operațiuni</h3>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setEditing('new')}
              >
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
                Adaugă operațiune
              </Button>
            </div>

            {data.savings_entries.length === 0 ? (
              <p className={styles.empty}>Nu există încă nicio operațiune.</p>
            ) : (
              <ul className={styles.list}>
                {data.savings_entries.map((entry) => (
                  <li key={entry.id} className={styles.item}>
                    <div className={styles.row}>
                      <Avatar name={entry.person_name} />
                      <div className={styles.rowText}>
                        <span className={styles.rowKind}>
                          {isWithdrawal(entry.amount)
                            ? 'Retragere'
                            : 'Depunere'}
                        </span>
                        <span className={styles.rowDate}>
                          {formatDate(entry.date)}
                        </span>
                      </div>
                      <span
                        className={`${styles.rowAmount} ${
                          isWithdrawal(entry.amount)
                            ? styles.negative
                            : styles.positive
                        }`}
                      >
                        {formatSignedAmount(entry.amount)}
                      </span>
                      {entry.note ? (
                        <button
                          type="button"
                          className={styles.iconButton}
                          aria-label={
                            openNoteId === entry.id
                              ? 'Ascunde nota'
                              : 'Arată nota'
                          }
                          aria-expanded={openNoteId === entry.id}
                          aria-controls={`savings-note-${entry.id}`}
                          onClick={() => toggleNote(entry.id)}
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
                        aria-label={`Editează operațiunea din ${formatDate(entry.date)}`}
                        onClick={() => setEditing(entry)}
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
                        aria-label={`Șterge operațiunea din ${formatDate(entry.date)}`}
                        onClick={() => setDeleting(entry)}
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
                    </div>
                    {openNoteId === entry.id && (
                      <p
                        id={`savings-note-${entry.id}`}
                        className={styles.noteText}
                      >
                        {entry.note}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        <div className={styles.actions}>
          <Button type="button" variant="secondary" onClick={onClose}>
            Închide
          </Button>
        </div>
      </div>

      {editing !== null && (
        <SavingsEntryModal
          entry={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
          onSaved={handleSaved}
        />
      )}

      {deleting && (
        <DeleteSavingsEntryModal
          entry={deleting}
          onClose={() => setDeleting(null)}
          onDeleted={handleDeleted}
        />
      )}
    </Modal>
  )
}
