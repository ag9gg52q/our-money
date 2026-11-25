import { apiFetch } from './client'

export type SavingsEntry = {
  id: string
  date: string
  amount: string
  note: string
  person: string
  person_name: string
}

export type SavingsEntryList = {
  savings_entries: SavingsEntry[]
  balance: string
  deposits: string
  withdrawals: string
}

export type SavingsEntryInput = Pick<
  SavingsEntry,
  'date' | 'person' | 'amount' | 'note'
>

export function fetchSavingsEntries(): Promise<SavingsEntryList> {
  return apiFetch<SavingsEntryList>('/api/v1/savings/')
}

export function createSavingsEntry(
  input: SavingsEntryInput,
): Promise<SavingsEntry> {
  return apiFetch<SavingsEntry>('/api/v1/savings/', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateSavingsEntry(
  id: string,
  changes: Partial<SavingsEntryInput>,
): Promise<SavingsEntry> {
  return apiFetch<SavingsEntry>(`/api/v1/savings/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}

export function deleteSavingsEntry(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/savings/${id}/`, {
    method: 'DELETE',
  })
}
