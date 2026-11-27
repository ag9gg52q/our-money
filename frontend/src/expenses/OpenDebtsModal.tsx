import { useEffect, useState } from 'react'

import { type OpenDebt, fetchOpenDebts } from '../api/expenses'
import Avatar from '../components/Avatar/Avatar'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import { formatAmount, formatDate } from '../utils/format'
import CancelDebtModal from './CancelDebtModal'
import styles from './OpenDebtsModal.module.css'
import SettleDebtModal from './SettleDebtModal'

type LoadState = 'loading' | 'ready' | 'error'

type OpenDebtsModalProps = {
  onClose: () => void
  onChanged: () => void
}

export default function OpenDebtsModal({
  onClose,
  onChanged,
}: OpenDebtsModalProps) {
  const [debts, setDebts] = useState<OpenDebt[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [settling, setSettling] = useState<OpenDebt | null>(null)
  const [canceling, setCanceling] = useState<OpenDebt | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let ignore = false

    fetchOpenDebts()
      .then((list) => {
        if (ignore) return
        setDebts(list.debts)
        setLoadState('ready')
      })
      .catch(() => {
        if (!ignore) setLoadState('error')
      })

    return () => {
      ignore = true
    }
  }, [reloadKey])

  function handleDone() {
    setSettling(null)
    setCanceling(null)
    setReloadKey((key) => key + 1)
    onChanged()
  }

  return (
    <Modal title="Datorii deschise" size="wide" onClose={onClose}>
      <div className={styles.content}>
        {loadState === 'loading' && (
          <p className={styles.message}>Se încarcă...</p>
        )}

        {loadState === 'error' && (
          <p className={styles.alert} role="alert">
            Nu am putut încărca datoriile. Încearcă din nou.
          </p>
        )}
        {loadState === 'ready' &&
          (debts.length === 0 ? (
            <p className={styles.empty}>Nimeni nu datorează nimic.</p>
          ) : (
            <ul className={styles.list}>
              {debts.map((debt) => (
                <li key={debt.id} className={styles.row}>
                  <Avatar name={debt.debtor_label} />
                  <div className={styles.rowText}>
                    <span className={styles.rowTitle}>
                      {debt.debtor_label}{' '}
                      <span className={styles.rowTo}>
                        îi datorează lui {debt.payer_name}
                      </span>
                    </span>
                    <span className={styles.rowMeta}>
                      {formatDate(debt.expense_date)}
                      {debt.expense_store && ` · ${debt.expense_store}`} · din{' '}
                      {formatAmount(debt.expense_amount)}
                    </span>
                  </div>
                  <span className={styles.rowAmount}>
                    {formatAmount(debt.amount)}
                  </span>
                  <Button
                    type="button"
                    variant="secondary"
                    className={styles.settleButton}
                    onClick={() => setSettling(debt)}
                  >
                    Întoarsă
                  </Button>
                  <button
                    type="button"
                    className={styles.iconButton}
                    aria-label={`Anulează datoria lui ${debt.debtor_label}`}
                    title="Anulează datoria"
                    onClick={() => setCanceling(debt)}
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
                      <path d="M6 6l12 12M18 6 6 18" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>
          ))}
        <div className={styles.actions}>
          <Button type="button" variant="secondary" onClick={onClose}>
            Închide
          </Button>
        </div>
      </div>

      {settling && (
        <SettleDebtModal
          debt={settling}
          onClose={() => setSettling(null)}
          onSettled={handleDone}
        />
      )}
      {canceling && (
        <CancelDebtModal
          debt={canceling}
          onClose={() => setCanceling(null)}
          onCanceled={handleDone}
        />
      )}
    </Modal>
  )
}
