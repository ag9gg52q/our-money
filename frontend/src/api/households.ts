import { apiFetch } from './client'

export type Household = {
  id: string
  name: string
  invite_code?: string
}

export type HouseholdMember = {
  id: string
  username: string
  first_name: string
  last_name: string
  role: 'admin' | 'user'
}

export type HouseholdDetails = {
  id: string
  name: string
  invite_code: string | null
  members: HouseholdMember[]
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

export function fetchCurrentHousehold(): Promise<HouseholdDetails> {
  return apiFetch<HouseholdDetails>('/api/v1/households/current/')
}

export function renameHousehold(name: string): Promise<HouseholdDetails> {
  return apiFetch<HouseholdDetails>('/api/v1/households/current/', {
    method: 'PATCH',
    body: JSON.stringify({ name }),
  })
}

export function makeAdmin(memberId: string): Promise<HouseholdMember> {
  return apiFetch<HouseholdMember>(
    `/api/v1/households/current/members/${memberId}/make-admin/`,
    {
      method: 'POST',
    },
  )
}
