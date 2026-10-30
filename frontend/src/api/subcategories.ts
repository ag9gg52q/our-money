import { apiFetch } from './client'

export type Subcategory = {
  id: string
  name: string
  is_active: boolean
}

export type SubcategoryChanges = Partial<
  Pick<Subcategory, 'name' | 'is_active'>
>

export function fetchSubcategories(id: string): Promise<Subcategory[]> {
  return apiFetch<Subcategory[]>(`/api/v1/categories/${id}/subcategories/`)
}

export function createSubcategory(
  id: string,
  name: string,
): Promise<Subcategory> {
  return apiFetch<Subcategory>(`/api/v1/categories/${id}/subcategories/`, {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function updateSubcategory(
  id: string,
  changes: SubcategoryChanges,
): Promise<Subcategory> {
  return apiFetch<Subcategory>(`/api/v1/subcategories/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}
