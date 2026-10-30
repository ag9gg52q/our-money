import { apiFetch } from './client'

export type Category = {
  id: string
  name: string
  is_active: boolean
}

export type CategoryChanges = Partial<Pick<Category, 'name' | 'is_active'>>

export function fetchCategories(): Promise<Category[]> {
  return apiFetch<Category[]>('/api/v1/categories/')
}

export function createCategory(name: string): Promise<Category> {
  return apiFetch<Category>('/api/v1/categories/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function updateCategory(
  id: string,
  changes: CategoryChanges,
): Promise<Category> {
  return apiFetch<Category>(`/api/v1/categories/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}
