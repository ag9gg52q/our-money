import Select, { type SelectOption } from '../components/Select/Select'
import TextField from '../components/TextField/TextField'
import { toDisplayAmount } from './amount'
import { type DebtRow, emptyDebtRow, OTHER, type RowErrors } from './debts'
import styles from './ExpenseModal.module.css'

type DebtRowsProps = {
  rows: DebtRow[]
  memberOptions: SelectOption[]
  errors: Record<string, RowErrors>
  onChange: (rows: DebtRow[]) => void
}

export default function DebtRows({
  rows,
  memberOptions,
  errors,
  onChange,
}: DebtRowsProps) {
  const options = [...memberOptions, { value: OTHER, label: 'Altcineva' }]

  function update(key: string, changes: Partial<DebtRow>) {
    onChange(
      rows.map((row) => (row.key === key ? { ...row, ...changes } : row)),
    )
  }

  function remove(key: string) {
    onChange(rows.filter((row) => row.key !== key))
  }

  return (
    <div className={styles.debts}>
      {rows.map((row, index) => {
        const rowErrors = errors[index] ?? {}
        return (
          <div key={row.key} className={styles.debtRow}>
            <div className={styles.debtPerson}>
              <Select
                label="Cine datorează"
                value={row.debtor}
                options={options}
                placeholder="Alege persoana"
                onChange={(debtor) => update(row.key, { debtor })}
                error={rowErrors.debtor}
              />
            </div>
            {row.debtor === OTHER && (
              <div className={styles.debtName}>
                <TextField
                  label="Nume"
                  maxLength={100}
                  value={row.name}
                  onChange={(event) =>
                    update(row.key, { name: event.target.value })
                  }
                  error={rowErrors.debtor_name}
                />
              </div>
            )}
            <div className={styles.debtAmount}>
              <TextField
                label="Sumă (lei)"
                inputMode="decimal"
                placeholder="0,00"
                value={row.amount}
                onChange={(event) =>
                  update(row.key, {
                    amount: toDisplayAmount(event.target.value),
                  })
                }
                error={rowErrors.amount}
              />
            </div>
            <button
              type="button"
              className={styles.removeDebt}
              onClick={() => remove(row.key)}
              aria-label={`Șterge datoria de pe rândul ${index + 1}`}
              title="Șterge"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <path d="M6 6l12 12M18 6 6 18" />
              </svg>
            </button>
          </div>
        )
      })}
      <button
        type="button"
        className={styles.addDebt}
        onClick={() => onChange([...rows, emptyDebtRow()])}
      >
        + Adaugă persoană
      </button>
    </div>
  )
}
