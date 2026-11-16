const amountFormat = new Intl.NumberFormat('ro-RO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const dateFormat = new Intl.DateTimeFormat('ro-RO', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})

export function formatAmount(amount: string): string {
  return `${amountFormat.format(amount as Intl.StringNumericLiteral)} lei`
}

export function formatDate(date: string): string {
  return dateFormat.format(new Date(date))
}
