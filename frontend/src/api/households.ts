import { apiFetch } from './client'

export type Household = {
  id: string
  name: string
  invite_code?: string
}

export function createHousehold(name: string): Promise<Household> {
  return apiFetch<Household>('/api/v1/households/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function joinHousehold(inviteCode: string): Promise<Household> {
  return apiFetch<Household>('/api/v1/households/join/', {
    method: 'POST',
    body: JSON.stringify({ invite_code: inviteCode }),
  })
}
