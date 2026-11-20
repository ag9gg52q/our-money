import { apiFetch } from './client'

export type Expense = {
  id: string
  date: string
  amount: string
  store: string
  note: string
  person: string
  person_name: string
  category: string
  category_name: string
  subcategory: string
  subcategory_name: string
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
  'date' | 'person' | 'category' | 'subcategory' | 'amount' | 'store' | 'note'
>

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
