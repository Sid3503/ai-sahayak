/**
 * Dashboard component props and shared types.
 */

export type DashboardProps = {
  welcomeName?: string | null
  onBackToChat: () => void
  onLogout: () => void
}

export type WelcomeCardProps = {
  main: string
  onContinue: () => void
  onLogout?: () => void
}

export type DemoUser = {
  name: string
  username: string
  password: string
  shopCategory: string
}

export type DashboardLoginCardProps = {
  title: string
  subtitle: string
  onSuccess: (signedInUsername?: string, displayNameFromDemo?: string) => void
  demoUsers?: DemoUser[]
}
