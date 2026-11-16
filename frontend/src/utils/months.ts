// O lună este reprezentată ca text 'YYYY-MM', de exemplu '2026-11'.

const monthFormat = new Intl.DateTimeFormat('ro-RO', {
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
})

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function parseMonth(month: string): [number, number] {
  const [year, monthNumber] = month.split('-').map(Number)
  return [year, monthNumber]
}

export function currentMonth(): string {
  const today = new Date()
  return `${today.getFullYear()}-${pad(today.getMonth() + 1)}`
}

export function today(): string {
  const today = new Date()
  return `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`
}

export function isValidMonth(value: string): boolean {
  return /^\d{4}-(0[1-9]|1[0-2])$/.test(value)
}

export function shiftMonth(month: string, delta: number): string {
  const [year, monthNumber] = parseMonth(month)
  const date = new Date(Date.UTC(year, monthNumber - 1 + delta, 1))
  return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}`
}

export function monthRange(month: string): {
  date_from: string
  date_to: string
} {
  const [year, monthNumber] = parseMonth(month)
  // Ziua 0 a lunii următoare este ultima zi a lunii curente.
  const lastDay = new Date(Date.UTC(year, monthNumber, 0)).getUTCDate()
  return { date_from: `${month}-01`, date_to: `${month}-${pad(lastDay)}` }
}

export function formatMonth(month: string): string {
  return monthFormat.format(new Date(`${month}-01`))
}
