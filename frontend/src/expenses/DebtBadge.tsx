import type { ExpenseDebt } from '../api/expenses'
import { formatAmount } from '../utils/format'
import styles from './DebtBadge.module.css'

type DebtBadgeProps = {
  debts: ExpenseDebt[]
}

// Eticheta „Datorie” de lângă sumă: apare doar cât timp cineva mai datorează o parte.
export default function DebtBadge({ debts }: DebtBadgeProps) {
  const open = debts.filter((debt) => debt.status === 'open')
  if (open.length === 0) return null

  return (
    // tabIndex: eticheta se poate atinge (telefon) sau focusa cu Tab, ca să arate detaliile.
    <span className={styles.badge} tabIndex={0}>
      Datorie
      <span className={styles.tooltip}>
        <span className={styles.tooltipTitle}>Datorează</span>
        {open.map((debt) => (
          <span key={debt.id} className={styles.tooltipRow}>
            <span>{debt.debtor_label}</span>
            <span>{formatAmount(debt.amount)}</span>
          </span>
        ))}
      </span>
    </span>
  )
}
