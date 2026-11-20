import { apiFetch } from './client'

export type Income = {
  id: string
  date: string
  amount: string
  note: string
  person: string
  person_name: string
  income_source: string
  income_source_name: string
}

export type IncomeList = {
  incomes: Income[]
  total: string
}

export type IncomeFilters = {
  date_from?: string
  date_to?: string
  person?: string
}

export type IncomeInput = Pick<
  Income,
  'date' | 'person' | 'income_source' | 'amount' | 'note'
>

export function fetchIncomes(filters: IncomeFilters): Promise<IncomeList> {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value)
  }
  const query = params.toString()
  const path = query ? `/api/v1/incomes/?${query}` : '/api/v1/incomes/'
  return apiFetch<IncomeList>(path)
}

export function createIncome(input: IncomeInput): Promise<Income> {
  return apiFetch<Income>('/api/v1/incomes/', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateIncome(
  id: string,
  changes: Partial<IncomeInput>,
): Promise<Income> {
  return apiFetch<Income>(`/api/v1/incomes/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}

export function deleteIncome(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/incomes/${id}/`, {
    method: 'DELETE',
  })
}
