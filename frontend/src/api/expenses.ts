import { apiFetch } from './client'

export type Expense = {
  id: string
  date: string
  amount: string
  store: string
  note: string
  link: string
  person: string
  person_name: string
  category: string
  category_name: string
  subcategory: string
  subcategory_name: string
  debts: ExpenseDebt[]
}

export type ExpenseList = {
  expenses: Expense[]
  total: string
}

export type ExpenseFilters = {
  date_from?: string
  date_to?: string
  category?: string
  subcategory?: string
  person?: string
}

export type ExpenseInput = Pick<
  Expense,
  | 'date'
  | 'person'
  | 'category'
  | 'subcategory'
  | 'amount'
  | 'store'
  | 'note'
  | 'link'
> & { debts?: ExpenseDebtInput[] }

export type DebtStatus = 'open' | 'settled' | 'canceled'

export type ExpenseDebt = {
  id: string
  debtor: string | null
  debtor_name: string
  debtor_label: string
  amount: string
  status: DebtStatus
  settled_at: string | null
}

export type OpenDebt = ExpenseDebt & {
  expense: string
  expense_date: string
  expense_store: string
  expense_amount: string
  payer_name: string
}

export type OpenDebtList = {
  debts: OpenDebt[]
}

export type ExpenseDebtInput = {
  id?: string
  debtor: string | null
  debtor_name: string
  amount: string
}

export function fetchExpenses(filters: ExpenseFilters): Promise<ExpenseList> {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value)
  }
  const query = params.toString()
  const path = query ? `/api/v1/expenses/?${query}` : '/api/v1/expenses/'
  return apiFetch<ExpenseList>(path)
}

export function createExpense(input: ExpenseInput): Promise<Expense> {
  return apiFetch<Expense>('/api/v1/expenses/', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateExpense(
  id: string,
  changes: Partial<ExpenseInput>,
): Promise<Expense> {
  return apiFetch<Expense>(`/api/v1/expenses/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}

export function deleteExpense(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/expenses/${id}/`, {
    method: 'DELETE',
  })
}

export function fetchOpenDebts(): Promise<OpenDebtList> {
  return apiFetch<OpenDebtList>('/api/v1/expenses/debts/')
}

export function settleDebt(id: string, amount: string): Promise<void> {
  return apiFetch<void>(`/api/v1/expenses/debts/${id}/settle/`, {
    method: 'POST',
    body: JSON.stringify({ amount }),
  })
}

export function cancelDebt(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/expenses/debts/${id}/cancel/`, {
    method: 'POST',
  })
}
