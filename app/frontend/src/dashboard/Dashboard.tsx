import { useEffect, useState } from 'react'
import { WelcomeCard } from './WelcomeCard'
import { formatWelcomeName, getWelcomeMessage } from './utils'
import type { DashboardProps } from './types'

export function Dashboard({ welcomeName, onBackToChat, onToRajuDay, onLogout }: DashboardProps) {
  const [welcomeCardDismissed, setWelcomeCardDismissed] = useState(false)
  const [, setDashboardLang] = useState<'en' | 'hi'>('en')
  const displayName = formatWelcomeName(welcomeName)
  const welcome = displayName ? getWelcomeMessage(displayName, true) : null
  const showWelcomeCard = welcome !== null && !welcomeCardDismissed

  // Persist welcome card dismissal for this browser session so it doesn't reappear
  // when the user navigates between Dashboard and Live Alerts.
  useEffect(() => {
    if (typeof window === 'undefined') return
    const key = 'ai_sahayak_dashboard_welcome_dismissed'
    const stored = window.sessionStorage.getItem(key)
    if (stored === '1') {
      setWelcomeCardDismissed(true)
    }
  }, [])

  const handleDismissWelcome = () => {
    setWelcomeCardDismissed(true)
    if (typeof window !== 'undefined') {
      window.sessionStorage.setItem('ai_sahayak_dashboard_welcome_dismissed', '1')
    }
  }

  return (
    <main className="flex flex-1 flex-col min-h-0">
      {showWelcomeCard ? (
        <WelcomeCard
          main={welcome.main}
          onContinue={handleDismissWelcome}
          onLanguageChoice={setDashboardLang}
          onLogout={onLogout}
        />
      ) : (
        <>
          {/* Action bar — Bharat light theme */}
          <section className="flex-shrink-0 flex items-center justify-end gap-2 py-2 border-b border-slate-200 mb-3">
            <button
              type="button"
              onClick={onToRajuDay}
              className="rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-bold text-white shadow-lg hover:bg-emerald-600 transition-colors"
            >
              My day →
            </button>
            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg border-2 border-slate-300 bg-white px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-50 hover:border-slate-400 transition-colors"
            >
              Logout
            </button>
          </section>

          {/* Control Centre embed */}
          <div className="flex-1 flex flex-col min-h-0" style={{ height: 'calc(100vh - 5.5rem)' }}>
            <div className="flex-1 min-h-0 w-full rounded-2xl overflow-hidden bg-white shadow-xl border-2 border-slate-200">
              <div className="h-full w-full rounded-2xl overflow-hidden border-t-[3px] border-t-emerald-500">
                <iframe
                  title="AI Sahayak Control Centre – Pricing, KPIs, Insights"
                  src={displayName ? `/control-centre/?retailer=${encodeURIComponent(displayName.toLowerCase())}` : '/control-centre/'}
                  className="w-full h-full min-h-[600px] border-0 bg-white"
                />
              </div>
            </div>
          </div>
        </>
      )}
    </main>
  )
}
