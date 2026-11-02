import { apiFetch } from './client'

export type IncomeSource = {
  id: string
  name: string
  is_active: boolean
}

export type IncomeSourceChanges = Partial<
  Pick<IncomeSource, 'name' | 'is_active'>
>

export function fetchIncomeSources(): Promise<IncomeSource[]> {
  return apiFetch<IncomeSource[]>('/api/v1/income-sources/')
}

export function createIncomeSource(name: string): Promise<IncomeSource> {
  return apiFetch<IncomeSource>('/api/v1/income-sources/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function updateIncomeSource(
  id: string,
  changes: IncomeSourceChanges,
): Promise<IncomeSource> {
  return apiFetch<IncomeSource>(`/api/v1/income-sources/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}
