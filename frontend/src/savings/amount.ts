export function isWithdrawal(amount: string): boolean {
  return amount.startsWith('-')
}

export function absoluteAmount(amount: string): string {
  return amount.replace('-', '')
}
