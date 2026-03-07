/**
 * Dashboard module: login, welcome card, and main Growth Command Center.
 * Re-export utils so App can use them for RajuDay (Live Alerts) welcome message.
 */

export { Dashboard } from './Dashboard'
export { DashboardLoginCard } from './DashboardLoginCard'
export { WelcomeCard } from './WelcomeCard'
export { formatWelcomeName, getWelcomeMessage } from './utils'
export type { DashboardProps, DashboardLoginCardProps, WelcomeCardProps } from './types'
