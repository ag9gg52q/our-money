import { ApiError } from '../api/client'
import type { ExpenseDebt, ExpenseDebtInput } from '../api/expenses'
import { toApiAmount, toDisplayAmount } from './amount'

// Valoarea din select pentru o persoană din afara gospodăriei.
export const OTHER = 'other'

export type DebtRow = {
  key: string
  id?: string
  debtor: string
  name: string
  amount: string
}

export type RowErrors = Partial<
  Record<'debtor' | 'debtor_name' | 'amount', string>
>

export type DebtErrors = {
  list?: string
  rows: Record<string, RowErrors>
}

export function emptyDebtRow(): DebtRow {
  return { key: crypto.randomUUID(), debtor: '', name: '', amount: '' }
}

export function toDebtRow(debt: ExpenseDebt): DebtRow {
  return {
    key: debt.id,
    id: debt.id,
    debtor: debt.debtor ?? OTHER,
    name: debt.debtor_name,
    amount: toDisplayAmount(debt.amount),
  }
}

export function toDebtInput(row: DebtRow): ExpenseDebtInput {
  const isOther = row.debtor === OTHER
  return {
    id: row.id,
    debtor: isOther || !row.debtor ? null : row.debtor,
    debtor_name: isOther ? row.name.trim() : '',
    amount: toApiAmount(row.amount),
  }
}

// Erorile datoriilor vin fie pentru toată lista ({debts: ["..."]}),
// fie pe rânduri, după index ({debts: {"0": {amount: ["..."]}}}).
export function getDebtErrors(error: unknown): DebtErrors {
  if (!(error instanceof ApiError)) return { rows: {} }
  const value: unknown = error.data.debts
  if (Array.isArray(value)) return { list: value.join(' '), rows: {} }
  if (!value || typeof value !== 'object') return { rows: {} }

  const rows: Record<string, RowErrors> = {}
  for (const [index, fields] of Object.entries(
    value as Record<string, Record<string, string[]>>,
  )) {
    rows[index] = Object.fromEntries(
      Object.entries(fields).map(([field, messages]) => [
        field,
        messages.join(' '),
      ]),
    )
  }
  return { rows }
}
