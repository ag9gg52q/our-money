export function toDisplayAmount(value: string): string {
  return value.replace('.', ',')
}

export function toApiAmount(value: string): string {
  return value.trim().replace(',', '.')
}
