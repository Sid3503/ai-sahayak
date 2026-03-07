import { useEffect, useState } from 'react'
import { RajuDay } from '../components/RajuDay'
import { WelcomeCard } from './WelcomeCard'
import { formatWelcomeName, getWelcomeMessage } from './utils'
import type { DashboardProps } from './types'

const PANEL_WIDTH = 420

type ModelStatus = {
  bedrock_ready: boolean
  forecast_primary: string
  dnn_loaded: boolean
  deepar_endpoint_configured: boolean
}

const defaultModelStatus: ModelStatus = {
  bedrock_ready: false,
  forecast_primary: 'DeepAR (SageMaker)',
  dnn_loaded: true,
  deepar_endpoint_configured: true,
}

export function Dashboard({ welcomeName, onBackToChat, onLogout }: DashboardProps) {
  const [welcomeCardDismissed, setWelcomeCardDismissed] = useState(false)
  const [panelOpen, setPanelOpen] = useState(false)
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null)

  const displayName = formatWelcomeName(welcomeName)
  const welcome = displayName ? getWelcomeMessage(displayName, true) : null
  const showWelcomeCard = welcome !== null && !welcomeCardDismissed

  useEffect(() => {
    if (typeof window === 'undefined') return
    const stored = window.sessionStorage.getItem('ai_sahayak_dashboard_welcome_dismissed')
    if (stored === '1') setWelcomeCardDismissed(true)
  }, [])

  useEffect(() => {
    const datasetKey = displayName?.toLowerCase() || 'raju'
    fetch(`/api/model-status?dataset_key=${encodeURIComponent(datasetKey)}`)
      .then((res) => res.ok ? res.json() : Promise.reject(new Error(res.statusText)))
      .then((data: ModelStatus) => setModelStatus(data))
      .catch(() => setModelStatus(defaultModelStatus))
  }, [displayName])

  const handleDismissWelcome = () => {
    setWelcomeCardDismissed(true)
    if (typeof window !== 'undefined')
      window.sessionStorage.setItem('ai_sahayak_dashboard_welcome_dismissed', '1')
  }

  return (
    <main
      className="flex flex-col w-full min-w-0 flex-1"
      style={{
        height: '100%',
        minHeight: 0,
        overflow: 'hidden',
        position: 'relative',
        width: '100%',
      }}
    >
      {showWelcomeCard ? (
        <WelcomeCard main={welcome.main} onContinue={handleDismissWelcome} onLogout={onLogout} />
      ) : (
        <div className="flex flex-1 min-h-0 min-w-0 relative w-full" style={{ overflow: 'hidden' }}>
          {/* ── LEFT: Dashboard card (full width; panel overlays so no resize = no flash) ── */}
          <div
            className="flex flex-col min-h-0 flex-1 min-w-0 w-full"
            style={{
              overflow: 'hidden',
              background: '#fafaf9',
              backgroundImage: 'radial-gradient(ellipse 120% 80% at 0% 0%, rgba(34, 197, 94, 0.06) 0, transparent 50%), radial-gradient(ellipse 100% 70% at 100% 100%, rgba(251, 191, 36, 0.05) 0, transparent 50%)',
              boxSizing: 'border-box',
            }}
          >
            <div
              className="flex flex-col flex-1 min-h-0 overflow-hidden"
              style={{
                margin: '6px 10px 10px',
                borderRadius: 18,
                background: '#fff',
                boxShadow: '0 1px 3px rgba(0,0,0,0.06), 0 8px 32px rgba(16, 185, 129, 0.08)',
                border: '1px solid rgba(34, 197, 94, 0.15)',
                borderTop: '4px solid #10b981',
                boxSizing: 'border-box',
                minWidth: 0,
              }}
            >
              {/* Header row: Command centre | Model Status | Live Alerts / Logout */}
              <div
                className="flex flex-shrink-0 items-center justify-between gap-3"
                style={{
                  padding: '12px 20px',
                  borderBottom: '1px solid #e5e7eb',
                  background: 'linear-gradient(180deg, #f8faf8 0%, #f0fdf4 100%)',
                  borderRadius: '22px 22px 0 0',
                }}
              >
                <div className="flex items-center gap-3">
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 12,
                      background: 'linear-gradient(135deg,#10b981,#059669)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 2px 8px rgba(16, 185, 129, 0.35)',
                    }}
                  >
                    <span style={{ color: '#fff', fontSize: '0.8rem', fontWeight: 800 }}>AI</span>
                  </div>
                  <div>
                    <p style={{ margin: 0, fontSize: '0.7rem', fontWeight: 700, color: '#059669', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Command centre</p>
                    <p style={{ margin: 0, fontSize: '1rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.03em' }}>Control Centre</p>
                  </div>
                </div>

                {/* Model Status – compact bar, no stretch; centered in navbar */}
                <div className="flex-1 flex justify-center items-center min-w-0">
                  <div
                    className="flex items-center flex-shrink-0"
                    style={{
                      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
                      borderRadius: 12,
                      padding: '8px 10px 10px 12px',
                      boxShadow: '0 2px 8px rgba(15, 23, 42, 0.25)',
                      border: '1px solid rgba(255,255,255,0.06)',
                      gap: 0,
                    }}
                  >
                    <div className="flex items-center gap-1.5 flex-shrink-0" style={{ marginRight: 10 }}>
                      <span style={{ fontSize: '0.65rem', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Model Status</span>
                      <span style={{ fontSize: '0.6rem', fontWeight: 600, color: '#10b981', background: 'rgba(16,185,129,0.15)', padding: '2px 6px', borderRadius: 6 }}>AWS Stack</span>
                    </div>
                    <div className="flex items-center">
                      {(() => {
                        const s = modelStatus ?? defaultModelStatus
                        return [
                          { name: 'Bedrock', value: s.bedrock_ready ? 'Connected' : 'Not Ready', ok: s.bedrock_ready },
                          { name: 'Forecast', value: s.forecast_primary || 'DeepAR (SageMaker)', ok: true },
                          { name: 'DNN', value: s.dnn_loaded ? 'Loaded' : 'Fallback', ok: s.dnn_loaded },
                          { name: 'DeepAR', value: s.deepar_endpoint_configured ? 'Endpoint Active' : 'Local Proxy', ok: s.deepar_endpoint_configured },
                        ]
                      })().map((item, i) => (
                        <div
                          key={item.name}
                          className="flex items-center gap-1.5 flex-shrink-0"
                          style={{
                            padding: '4px 8px 4px 10px',
                            borderLeft: i > 0 ? '1px solid rgba(255,255,255,0.08)' : 'none',
                          }}
                        >
                          <span
                            style={{
                              width: 6,
                              height: 6,
                              borderRadius: '50%',
                              background: item.ok ? '#22c55e' : '#f59e0b',
                              flexShrink: 0,
                            }}
                          />
                          <div>
                            <div style={{ fontSize: '0.6rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600, lineHeight: 1.2 }}>{item.name}</div>
                            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#fff', lineHeight: 1.2 }}>{item.value}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    type="button"
                    onClick={() => setPanelOpen((o) => !o)}
                    className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-white text-sm font-bold transition-all duration-200 hover:opacity-95 active:scale-[0.98]"
                    style={{
                      background: panelOpen ? '#64748b' : 'linear-gradient(135deg,#f59e0b,#ea580c)',
                      boxShadow: panelOpen ? 'none' : '0 4px 14px rgba(245, 158, 11, 0.4)',
                    }}
                    aria-label={panelOpen ? 'Close Live Alerts' : 'Open Live Alerts'}
                  >
                    <svg width={16} height={16} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                    {panelOpen ? 'Close' : 'Live Alerts'}
                  </button>
                  <button
                    type="button"
                    onClick={onLogout}
                    className="rounded-xl border-2 border-slate-200 bg-white px-4 py-2.5 text-sm font-bold text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50"
                  >
                    Logout
                  </button>
                </div>
              </div>
              <iframe
                title="AI Sahayak Control Centre"
                src={displayName ? `/control-centre/?retailer=${encodeURIComponent(displayName.toLowerCase())}` : '/control-centre/'}
                style={{ width: '100%', flex: 1, minHeight: 0, border: 'none', display: 'block' }}
              />
            </div>
          </div>

          {/* ── RIGHT: Live Alerts panel as overlay; hidden on first load / when closed ── */}
          <div
            role="dialog"
            aria-label="Live Alerts"
            aria-hidden={!panelOpen}
            style={{
              position: 'absolute',
              top: 0,
              right: 0,
              bottom: 0,
              width: PANEL_WIDTH,
              transform: panelOpen ? 'translateX(0)' : 'translateX(100%)',
              transition: 'transform 280ms cubic-bezier(0.32, 0.72, 0, 1)',
              visibility: panelOpen ? 'visible' : 'hidden',
              willChange: 'transform',
              flexShrink: 0,
              display: 'flex',
              flexDirection: 'column',
              background: '#fff',
              boxShadow: '-8px 0 32px rgba(0,0,0,0.12)',
              zIndex: 40,
              overflow: 'hidden',
              pointerEvents: panelOpen ? 'auto' : 'none',
            }}
          >
            <div
              style={{
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                borderBottom: '1px solid #e5e7eb',
                background: 'linear-gradient(135deg,#075e54,#0d9488)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <svg width={18} height={18} fill="none" stroke="#fff" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#fff' }}>Live Alerts</span>
                <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>— My day</span>
              </div>
              <button
                type="button"
                onClick={() => setPanelOpen(false)}
                aria-label="Close"
                className="rounded-lg p-2 text-white/90 hover:bg-white/20 transition-colors"
              >
                <svg width={18} height={18} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
              <RajuDay welcomeName={welcomeName} onClose={() => setPanelOpen(false)} />
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
