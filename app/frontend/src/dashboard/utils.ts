/**
 * Dashboard welcome formatting helpers.
 * Used by Dashboard and RajuDay (Live Alerts).
 */

export function formatWelcomeName(username: string | null | undefined): string {
  if (!username) return ''
  return username
    .split(/[\s_-]+/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ')
}

/** Dashboard welcome: main greeting; language choice (English/Hindi) is on the card. */
export function getWelcomeMessage(
  displayName: string,
  _isDashboard: boolean
): { main: string; sub: string } {
  return {
    main: `Namaste, ${displayName}!`,
    sub: '',
  }
}
