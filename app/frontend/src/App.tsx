import { useEffect, useRef, useState } from 'react'
import './App.css'
import { useAuth } from './authContext'
import { SplashScreen, wasSplashAlreadySeen } from './SplashScreen'
import { signOut, getCurrentUser, fetchUserAttributes } from 'aws-amplify/auth'
import { isCognitoConfigured } from './cognitoConfig'
import { Dashboard, DashboardLoginCard, formatWelcomeName, getWelcomeMessage } from './dashboard'
import type { DemoUser } from './dashboard/types'

const DEMO_USERS: DemoUser[] = [
  { name: 'Raju', username: '9004755498', password: 'Raju_5498!', shopCategory: 'Grocery retail' },
  { name: 'Ramesh', username: '9878815498', password: 'Ramesh_5498!', shopCategory: 'Pharmacy' },
  { name: 'Suresh', username: '7400415498', password: 'Suresh_5498!', shopCategory: 'Building Materials' },
  { name: 'Kanta', username: '8146655498', password: 'Kanta_5498!', shopCategory: 'Textile' },
  { name: 'Lakshmi', username: '7710015498', password: 'Lakshmi_5498!', shopCategory: 'Electronics Accessories' },
]

function useScrollProgress() {
  const [progress, setProgress] = useState(0)
  useEffect(() => {
    const onScroll = () => {
      const el = document.documentElement
      const scrolled = el.scrollTop
      const total = el.scrollHeight - el.clientHeight
      setProgress(total > 0 ? Math.min(100, (scrolled / total) * 100) : 0)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])
  return progress
}

function useLiveClock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return time
}

/** Today's date for WP UI date pill — same format in Onboarding and Live Alerts */
function getTodayDatePill(): string {
  return new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }).toUpperCase()
}

/** IST time string for message/status bar — e.g. "2:45 PM" */
function formatISTTime(date: Date): string {
  return new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
    .toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true })
}

/** IST time for status bar — e.g. "14:45" */
function formatISTStatusTime(date: Date): string {
  const ist = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
  return `${ist.getHours().toString().padStart(2, '0')}:${ist.getMinutes().toString().padStart(2, '0')}`
}

function useInView(threshold = 0.12) {
  const ref = useRef<HTMLDivElement>(null)
  const [, setInView] = useState(false)
  const [hasSeen, setHasSeen] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) setHasSeen(true)
        setInView(e.isIntersecting)
      },
      { threshold }
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [threshold])
  return [ref, hasSeen] as const
}

type View = 'landing' | 'chat' | 'dashboard' | 'day'

function LiveClock() {
  const time = useLiveClock()
  const istTime = new Date(time.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
  const h = istTime.getHours().toString().padStart(2, '0')
  const m = istTime.getMinutes().toString().padStart(2, '0')
  const s = istTime.getSeconds().toString().padStart(2, '0')
  const isNearTrigger = istTime.getHours() === 9 && istTime.getMinutes() < 5
  return (
    <div className="shrink-0 flex items-center gap-2">
      <div className="flex items-center gap-2.5">
        <span className={`h-1.5 w-1.5 rounded-full flex-shrink-0 ${isNearTrigger ? 'bg-emerald-500 animate-ping' : 'bg-emerald-500'}`} />
        <span className={`font-mono text-sm font-bold tracking-widest ${isNearTrigger ? 'text-emerald-600' : 'text-slate-600'}`}>{h}:{m}:{s}</span>
        <span className="text-[0.6rem] text-slate-500 uppercase tracking-wider">IST</span>
      </div>
      <div className="hidden lg:block h-4 w-px bg-slate-300 mx-1" />
      <span className="hidden lg:block text-[0.6rem] font-bold tracking-[0.15em] text-slate-500 uppercase">AWS Hackathon</span>
    </div>
  )
}

const SESSION_STORAGE_KEY = 'ai_sahayak_session_id'

function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') return 'web-demo-session'
  let sid = localStorage.getItem(SESSION_STORAGE_KEY)
  if (!sid) {
    sid = `web_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
    localStorage.setItem(SESSION_STORAGE_KEY, sid)
  }
  return sid
}

function getOrCreateUserId(): string {
  const USER_ID_KEY = 'ai_sahayak_user_id'
  if (typeof window === 'undefined') return 'web_user_temp'
  let uid = localStorage.getItem(USER_ID_KEY)
  if (!uid) {
    uid = `web_${Math.random().toString(36).slice(2, 11)}`
    localStorage.setItem(USER_ID_KEY, uid)
  }
  return uid
}

function App() {
  const auth = useAuth()
  const [showSplash, setShowSplash] = useState(() => !wasSplashAlreadySeen())
  const [view, setView] = useState<View>('landing')
  const [dashboardLoggedIn, setDashboardLoggedIn] = useState(false)
  const [currentUsername, setCurrentUsername] = useState<string | null>(null)
  const [currentDisplayName, setCurrentDisplayName] = useState<string | null>(null)
  const VIEW_ORDER: View[] = ['landing', 'chat', 'dashboard', 'day']
  const currentStep = VIEW_ORDER.indexOf(view) + 1
  const scrollProgress = useScrollProgress()

  // Start with a fresh onboarding session when user opens the chat view (so bot doesn't greet "Raju" from a previous run)
  useEffect(() => {
    if (view === 'chat' && typeof window !== 'undefined') {
      localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }, [view])

  // Resolve display name for "Namaste, {full name}!": from Cognito name attribute, else from backend profile API
  const resolveDisplayName = async (username: string): Promise<string> => {
    try {
      const attrs = await fetchUserAttributes()
      const cognitoName = (attrs && (attrs as Record<string, string>).name) ? String((attrs as Record<string, string>).name).trim() : ''
      if (cognitoName) return cognitoName
    } catch {
      /* ignore */
    }
    try {
      const base = (import.meta as any).env?.VITE_AGENT_API_BASE || 'http://localhost:8000'
      const res = await fetch(`${base}/v1/profile?user_id=${encodeURIComponent(username)}`)
      const data = (await res.json()) as { name?: string | null }
      const name = data?.name && String(data.name).trim()
      if (name) return name
    } catch {
      /* ignore */
    }
    return username
  }

  // On full page reload: clear Cognito session so user must sign in again (reload = logout)
  useEffect(() => {
    if (!isCognitoConfigured) return
    signOut()
      .then(() => {
        setDashboardLoggedIn(false)
        setCurrentUsername(null)
        setCurrentDisplayName(null)
      })
      .catch(() => {})
  }, [])

  const isAuthenticatedForDashboard = auth.isAuthenticated || dashboardLoggedIn

  // Backend agent webhook (LangGraph chatbot). Base URL via Vite env VITE_AGENT_API_BASE.
  const agentApiBase =
    (import.meta as any).env?.VITE_AGENT_API_BASE || 'http://localhost:8000'

  const handleOnboardingBotReply: OnboardingBotReply = async (userMessage: string) => {
    const sessionId = getOrCreateSessionId()
    const userId = getOrCreateUserId()
    try {
      const response = await fetch(`${agentApiBase}/v1/webhook/incoming`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          text: userMessage,
          platform: 'web',
          phone_number: '0000000000',
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        console.error('Agent API error status', response.status)
        return { reply: 'Bot is unavailable right now. Please try again.', suggestedActions: [] }
      }

      const data = await response.json()
      const reply = data.reply || data.message || 'No reply from bot.'
      const suggestedActions = Array.isArray(data.suggested_actions) ? data.suggested_actions : []
      return { reply, suggestedActions }
    } catch (error) {
      console.error('Error calling agent API', error)
      return { reply: 'Unable to reach the bot. Please check the server.', suggestedActions: [] }
    }
  }

  const handleOnboardingImageUpload: OnboardingImageUpload = async (base64: string, mimeType: string) => {
    const sessionId = getOrCreateSessionId()
    const userId = getOrCreateUserId()
    try {
      const response = await fetch(`${agentApiBase}/v1/webhook/incoming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          text: 'Photo attached',
          image: base64,
          image_media_type: mimeType,
          platform: 'web',
          phone_number: '0000000000',
          session_id: sessionId,
        }),
      })
      if (!response.ok) return 'Photo received. You can send more or type a message.'
      const data = await response.json()
      return data.reply || data.message || 'Photo received.'
    } catch {
      return 'Could not upload photo. Please try again.'
    }
  }

  const handleOnboardingVoiceMessage: OnboardingVoiceMessage = async (audioBase64: string, mimeType: string) => {
    const sessionId = getOrCreateSessionId()
    const userId = getOrCreateUserId()
    try {
      const response = await fetch(`${agentApiBase}/v1/webhook/incoming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          text: 'Voice message',
          platform: 'web',
          phone_number: '0000000000',
          session_id: sessionId,
          metadata: { voice_language: 'hi' },
          audio: audioBase64,
          audio_media_type: mimeType || 'audio/webm',
        }),
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        return { reply: err.detail || 'Voice not available. Please type your message.', transcribed_text: undefined }
      }
      const data = await response.json()
      return { reply: data.reply || '', transcribed_text: data.transcribed_text }
    } catch (e) {
      console.error('Voice webhook error', e)
      return { reply: 'Unable to reach the bot. Please try again.', transcribed_text: undefined }
    }
  }

  const NAV_STEPS = [
    { id: 'landing'   as const, num: 1, label: 'Home',        sub: 'Start here'      },
    { id: 'chat'      as const, num: 2, label: 'Onboarding',  sub: 'Setup via chat'  },
    { id: 'dashboard' as const, num: 3, label: 'Dashboard',   sub: 'Command center'  },
    { id: 'day'       as const, num: 4, label: 'Live Alerts',  sub: 'Real-time view'  },
  ]

  return (
    <div className="min-h-screen text-slate-800 relative bg-[#fefbf5]">
      {showSplash && <SplashScreen onDismiss={() => setShowSplash(false)} />}

      {/* Tricolor strip — Bharat (top) */}
      <div className="fixed top-0 left-0 right-0 z-[51] flex h-1.5">
        <div className="flex-1 bg-[#f59e0b]" />
        <div className="flex-1 bg-white" />
        <div className="flex-1 bg-[#16a34a]" />
      </div>

      {/* ═══════════════════════════════════════════════════
          BHARAT BACKGROUND — jaw-drop version
          Layer 1: Deep saffron → cream → India-green gradient
          Layer 2: Animated Ashok Chakra SVG watermark (center)
          Layer 3: Diya glow orbs (floating saffron + green light)
          Layer 4: Subtle paisley dot halo (bottom-right corner)
      ═══════════════════════════════════════════════════ */}

      {/* Layer 1 — tricolor gradient base (stronger bands so it pops) */}
      <div className="pointer-events-none fixed inset-0" style={{ zIndex: 0, background: 'linear-gradient(165deg, #fed7aa 0%, #fff7ed 18%, #ffffff 38%, #f0fdf4 65%, #dcfce7 100%)' }} />

      {/* Layer 2 — Ashok Chakra: more visible (opacity + thicker strokes) */}
      <div className="pointer-events-none fixed inset-0 flex items-center justify-center" style={{ zIndex: 0 }}>
        <svg
          viewBox="0 0 200 200"
          className="animate-chakra-spin opacity-[0.12]"
          style={{ width: 'min(90vw,90vh)', height: 'min(90vw,90vh)' }}
          aria-hidden="true"
        >
          <circle cx="100" cy="100" r="96" fill="none" stroke="#1e40af" strokeWidth="4" />
          <circle cx="100" cy="100" r="88" fill="none" stroke="#1e40af" strokeWidth="2" />
          {Array.from({ length: 24 }).map((_, i) => {
            const angle = (i * 360) / 24
            const rad = (angle * Math.PI) / 180
            const x1 = 100 + 12 * Math.sin(rad)
            const y1 = 100 - 12 * Math.cos(rad)
            const x2 = 100 + 88 * Math.sin(rad)
            const y2 = 100 - 88 * Math.cos(rad)
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#1e40af" strokeWidth="2.5" />
          })}
          <circle cx="100" cy="100" r="12" fill="none" stroke="#1e40af" strokeWidth="3" />
          <circle cx="100" cy="100" r="5" fill="#1e40af" />
        </svg>
      </div>

      {/* Layer 3 — Diya orbs: stronger so they pop */}
      <div className="pointer-events-none fixed inset-0" style={{ zIndex: 0, background: 'radial-gradient(ellipse 60% 45% at 92% 5%, rgba(249,115,22,0.35) 0%, rgba(251,191,36,0.22) 40%, transparent 70%)' }} />
      <div className="pointer-events-none fixed inset-0" style={{ zIndex: 0, background: 'radial-gradient(ellipse 55% 45% at 5% 95%, rgba(22,163,74,0.32) 0%, rgba(34,197,94,0.18) 45%, transparent 72%)' }} />
      <div className="pointer-events-none fixed inset-0" style={{ zIndex: 0, background: 'radial-gradient(ellipse 75% 55% at 50% 45%, rgba(255,247,237,0.85) 0%, rgba(255,237,213,0.4) 50%, transparent 70%)' }} />

      {/* Layer 4 — Marigold corner (bottom-right): more visible */}
      <div className="pointer-events-none fixed bottom-0 right-0" style={{ zIndex: 0, width: 400, height: 400, opacity: 0.16 }}>
        <svg viewBox="0 0 200 200" width="400" height="400" aria-hidden="true">
          {[0,45,90,135,180,225,270,315].map((deg, i) => (
            <g key={i} transform={`rotate(${deg} 100 100)`}>
              <ellipse cx="100" cy="44" rx="12" ry="30" fill="none" stroke="#ea580c" strokeWidth="2.5" />
              <ellipse cx="100" cy="44" rx="6" ry="16" fill="#f59e0b" opacity="0.6" />
              <circle cx="100" cy="20" r="4" fill="#f59e0b" />
            </g>
          ))}
          <circle cx="100" cy="100" r="14" fill="#f59e0b" opacity="0.8" />
          {[0,30,60,90,120,150,180,210,240,270,300,330].map((deg, i) => (
            <circle key={i} cx={100 + 22 * Math.sin((deg * Math.PI) / 180)} cy={100 - 22 * Math.cos((deg * Math.PI) / 180)} r="3.5" fill="#16a34a" opacity="0.9" />
          ))}
        </svg>
      </div>

      {/* Layer 5 — Top-left green marigold: more visible */}
      <div className="pointer-events-none fixed top-0 left-0" style={{ zIndex: 0, width: 280, height: 280, opacity: 0.14 }}>
        <svg viewBox="0 0 200 200" width="280" height="280" aria-hidden="true">
          {[0,60,120,180,240,300].map((deg, i) => (
            <g key={i} transform={`rotate(${deg} 100 100)`}>
              <ellipse cx="100" cy="40" rx="10" ry="28" fill="none" stroke="#16a34a" strokeWidth="2.5" />
              <ellipse cx="100" cy="40" rx="5" ry="14" fill="#22c55e" opacity="0.6" />
            </g>
          ))}
          <circle cx="100" cy="100" r="12" fill="#16a34a" opacity="0.8" />
        </svg>
      </div>

      {/* Scroll progress */}
      <div className="fixed top-1.5 left-0 right-0 z-[60] h-0.5 bg-white/90">
        <div className="h-full bg-gradient-to-r from-emerald-500 via-sahayak-amber to-emerald-500 transition-all duration-150" style={{ width: `${scrollProgress}%` }} />
      </div>

      {/* Navbar — light, clean */}
      <header className="fixed top-1.5 left-0 right-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur-xl shadow-sm">
        <div className="flex h-14 w-full items-center justify-between gap-4 px-4 md:px-8 lg:px-14">
          <div className="flex shrink-0 items-center gap-2">
            <button type="button" onClick={() => setView('landing')} className="flex items-center gap-2.5 group" aria-label="Go to Home">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-xl border-2 border-emerald-500/50 bg-white shadow-md transition group-hover:border-emerald-500">
                <img src="/Generated_image.png" alt="AI Sahayak" className="h-full w-full object-contain" />
              </div>
              <div className="leading-none hidden sm:block">
                <p className="text-sm font-bold tracking-tight text-slate-800">AI Sahayak</p>
                <p className="mt-0.5 text-[0.6rem] font-medium text-emerald-600">by GenGurus</p>
              </div>
            </button>
          </div>
          <nav className="flex flex-1 items-center justify-center" aria-label="Journey steps">
            <div className="flex items-center gap-1 p-1">
              {NAV_STEPS.map((step, i) => {
                const isActive = view === step.id
                const isDone = currentStep > step.num
                const isLast = i === NAV_STEPS.length - 1
                return (
                  <div key={step.id} className="flex items-center">
                    <button type="button" onClick={() => setView(step.id)} className={`group flex items-center gap-2 rounded-xl px-3 py-2 transition-all duration-200 ${isActive ? 'bg-emerald-500/15 border border-emerald-500/40 shadow-sm' : 'border border-transparent hover:bg-slate-100'}`}>
                      <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${isActive ? 'bg-emerald-500 text-white' : isDone ? 'bg-emerald-100 text-emerald-600 border border-emerald-200' : 'bg-slate-100 text-slate-500 border border-slate-200 group-hover:text-slate-700'}`}>
                        {isDone && !isActive ? <svg className="h-3 w-3" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg> : step.num}
                      </span>
                      <span className="whitespace-nowrap text-left hidden md:block">
                        <span className={`block text-xs font-semibold leading-tight ${isActive ? 'text-slate-900' : isDone ? 'text-emerald-700' : 'text-slate-500 group-hover:text-slate-700'}`}>{step.label}</span>
                        <span className={`block text-[0.6rem] leading-tight mt-0.5 ${isActive ? 'text-emerald-600' : 'text-slate-400'}`}>{step.sub}</span>
                      </span>
                    </button>
                    {!isLast && <div className={`w-1.5 h-1.5 rounded-full mx-0.5 shrink-0 ${isDone ? 'bg-emerald-300' : 'bg-slate-300'}`} aria-hidden />}
                  </div>
                )
              })}
            </div>
          </nav>
          <div className="flex items-center gap-3">
            <LiveClock />
          </div>
        </div>
        <div className="h-0.5 w-full bg-gradient-to-r from-sahayak-amber via-emerald-500 to-sahayak-green" />
      </header>

      {/* Content area – above background layers so iframe is fully visible */}
      <div className="relative flex flex-1 flex-col" style={{ zIndex: 10 }}>
        {view === 'landing' && (
          <Landing
            onStart={() => setView('chat')}
            onSkipToDashboard={() => setView('dashboard')}
            onSkipToDay={() => setView('day')}
          />
        )}
        {view === 'chat' && (
          <div className="flex flex-1 flex-col w-full min-h-screen" style={{ paddingTop: '4rem', minHeight: '100vh' }}>
            {/* Bharat theme: let global gradient show; tricolor strip under header */}
            <div className="h-1 w-full shrink-0 bg-gradient-to-r from-sahayak-amber via-emerald-500 to-sahayak-green" />
            <ChatOnboarding
              onContinue={() => setView('dashboard')}
              onBotReply={handleOnboardingBotReply}
              onImageUpload={handleOnboardingImageUpload}
              onVoiceMessage={handleOnboardingVoiceMessage}
            />
          </div>
        )}
        {view === 'dashboard' && (
          <div className={`flex flex-1 flex-col w-full min-h-screen ${isAuthenticatedForDashboard ? 'px-4 md:px-8 lg:px-14' : 'mx-auto max-w-7xl px-4 md:px-8'} pt-[5rem] pb-6 md:pt-[5rem] md:pb-8`}>
            {isAuthenticatedForDashboard ? (
              <Dashboard
                key={currentUsername ?? 'anon'}
                welcomeName={currentDisplayName ?? currentUsername}
                onBackToChat={() => setView('chat')}
                onToRajuDay={() => setView('day')}
                onLogout={async () => {
                  try {
                    await signOut()
                  } catch {
                    /* ignore */
                  }
                  setDashboardLoggedIn(false)
                  setCurrentUsername(null)
                  setCurrentDisplayName(null)
                }}
              />
            ) : (
              <DashboardLoginCard
                title="Sign in"
                subtitle="Use the ID + password from your onboarding chat."
                demoUsers={DEMO_USERS}
                onSuccess={async (signedInUsername?: string, displayNameFromDemo?: string) => {
                  try {
                    const user = await getCurrentUser().catch(() => null)
                    const username = user?.username ?? signedInUsername ?? null
                    setCurrentUsername(username ?? null)
                    const displayName =
                      displayNameFromDemo ??
                      (username ? DEMO_USERS.find((u) => u.username === username)?.name : undefined) ??
                      (username ? await resolveDisplayName(username) : undefined)
                    setCurrentDisplayName(displayName ?? null)
                    setDashboardLoggedIn(true)
                  } catch {
                    setCurrentDisplayName(displayNameFromDemo ?? null)
                    setCurrentUsername(signedInUsername ?? null)
                    setDashboardLoggedIn(true)
                  }
                }}
              />
            )}
          </div>
        )}
        {view === 'day' && (
          <div className="flex flex-1 flex-col w-full min-h-screen" style={{ paddingTop: '4rem' }}>
            <RajuDay welcomeName={currentDisplayName ?? currentUsername} onBackToDashboard={() => setView('dashboard')} />
          </div>
        )}
      </div>
    </div>
  )
}

function Landing(props: { onStart: () => void; onSkipToDashboard: () => void; onSkipToDay: () => void }) {
  const { onStart, onSkipToDashboard, onSkipToDay } = props
  const [storyRef, storySeen] = useInView(0.08)
  const [statsRef, statsSeen] = useInView(0.08)
  const [diffRef, diffSeen] = useInView(0.08)
  const [techRef, techSeen] = useInView(0.08)
  const [ctaRef, ctaSeen] = useInView(0.1)

  return (
    <main className="relative z-10 flex flex-1 flex-col overflow-x-hidden pt-[4rem]">

      {/* ══ HERO ══ */}
      <section className="relative z-10 min-h-screen flex flex-col justify-center overflow-hidden">
        <div className="relative z-10 mx-auto max-w-7xl w-full px-4 py-16 md:py-20 md:px-8">

          {/* Badge */}
          <div className="flex justify-center mb-8">
            <span className="inline-flex items-center gap-2 rounded-full border-2 border-emerald-500/40 bg-white px-5 py-2.5 text-xs font-bold tracking-[0.15em] text-emerald-700 uppercase shadow-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              AWS AI for Bharat Hackathon · Professional Track
            </span>
          </div>

          <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-20">

            {/* Left: Copy — dark text on light */}
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center gap-2 rounded-full border-2 border-amber-400 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800 mb-5">
                The problem: kirana stores lose ₹15,000+ every festive season
              </div>
              <h1 className="text-4xl font-black leading-[1.1] tracking-tight text-slate-900 md:text-5xl xl:text-6xl">
                <span className="block text-slate-400 line-through decoration-rose-400 decoration-2 text-2xl md:text-3xl mb-2">Reactive chatbot</span>
                <span className="block bg-gradient-to-r from-emerald-600 via-emerald-500 to-sahayak-amber bg-clip-text text-transparent pb-1">Proactive</span>
                <span className="block text-slate-900">Intelligence</span>
              </h1>
              <p className="mt-5 text-base font-medium leading-relaxed text-slate-700 md:text-lg max-w-lg mx-auto lg:mx-0">
                AI Sahayak warns <strong className="text-slate-900">your store</strong> — <strong className="text-slate-900">when you want</strong>: you choose how many days before and at what time. Before the festival, before the wedding season, before the demand spike. Not after shelves go empty.
              </p>

              <div className="mt-6 flex flex-wrap gap-2 justify-center lg:justify-start">
                {[
                  'Alerts at a time you set',
                  '92% demand confidence',
                  'Vernacular alerts',
                  'Dukaan news only — prices, GST, FMCG',
                  'Festival calendar',
                ].map(text => (
                  <span key={text} className="inline-flex items-center gap-1.5 rounded-full border-2 border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-800 shadow-sm">
                    {text}
                  </span>
                ))}
              </div>

              <div className="mt-8 flex flex-wrap gap-3 justify-center lg:justify-start">
                <button type="button" onClick={onStart}
                  className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-7 py-3.5 text-sm font-black text-white shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-600 hover:scale-[1.02] active:scale-[0.98]">
                  Start the Demo →
                </button>
                <button type="button" onClick={onSkipToDashboard}
                  className="rounded-full border-2 border-slate-300 bg-white px-5 py-3.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:border-slate-400 transition">
                  Dashboard →
                </button>
              </div>

              <div className="mt-8 flex items-center gap-4 justify-center lg:justify-start">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-slate-200 text-xs font-bold text-slate-600 shadow-sm">{i}</div>
                  ))}
                </div>
                <p className="text-sm font-semibold text-slate-700"><strong className="text-slate-900">12–15M</strong> kiranas waiting for this</p>
              </div>
            </div>

            {/* Right: Phone mockup — warm Bharat frame */}
            <div className="flex justify-center lg:justify-end">
              <div className="relative">
                <div className="absolute inset-0 -m-6 rounded-3xl bg-gradient-to-br from-emerald-500/20 to-sahayak-amber/20 blur-2xl" />
                <div className="relative w-64 md:w-72">
                  <div className="rounded-[2.5rem] border-[6px] shadow-2xl overflow-hidden" style={{ borderColor: '#f59e0b', boxShadow: '0 20px 50px -12px rgba(0,0,0,0.2), 0 0 0 1px rgba(245,158,11,0.2)' }}>
                    {/* Status bar */}
                    <div className="flex items-center justify-between bg-slate-900 px-4 py-2 text-[0.6rem] text-slate-500">
                      <span>9:00</span>
                      <div className="h-3 w-12 rounded-full bg-slate-800 flex items-center justify-center">
                        <div className="h-1.5 w-1.5 rounded-full bg-slate-600" />
                      </div>
                      <span>●●●</span>
                    </div>

                    {/* Chat header */}
                    <div className="flex items-center gap-2 border-b border-slate-800 bg-slate-800/50 px-3 py-2">
                      <div className="h-7 w-7 rounded-full bg-emerald-500 flex items-center justify-center text-xs font-bold text-white">AI</div>
                      <div>
                        <p className="text-xs font-semibold text-white">AI Sahayak</p>
                        <p className="text-[0.55rem] text-emerald-400 flex items-center gap-1">
                          <span className="h-1 w-1 rounded-full bg-emerald-400 inline-block animate-pulse" />online · EventBridge
                        </p>
                      </div>
                    </div>

                    {/* Messages */}
                    <div className="bg-slate-900 p-3 space-y-2.5 min-h-[260px]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, #1a2332 1px, transparent 1px)', backgroundSize: '16px 16px' }}>
                      <div className="rounded-xl rounded-tl-none bg-slate-700 px-3 py-2 text-xs text-slate-100 max-w-[88%] shadow-sm">
                        <strong>Raju Bhai</strong>, Holi 5 din baad hai! Ghee aur Shakkar ka stock check kar lo!
                        <p className="mt-1 text-[0.55rem] text-slate-400">9:00 AM</p>
                      </div>
                      <div className="rounded-xl rounded-tl-none bg-amber-500/20 border border-amber-500/30 px-3 py-2 text-xs text-amber-100 max-w-[88%] shadow-sm">
                        Aaj ki sale: <strong className="text-emerald-400">₹18,400</strong> · +23% ↑
                        <p className="mt-1 text-[0.55rem] text-amber-500/70">9:01 AM · SageMaker 87% conf.</p>
                      </div>
                      <div className="flex justify-end">
                        <div className="rounded-xl rounded-tr-none bg-emerald-700 px-3 py-2 text-xs text-white max-w-[75%] shadow-sm">
                          Shukriya! Order kar deta hoon.
                          <p className="mt-1 text-[0.55rem] text-emerald-300/70">9:05 AM</p>
                        </div>
                      </div>
                      <div className="rounded-xl rounded-tl-none bg-slate-700 px-3 py-2 text-xs text-slate-100 max-w-[88%] shadow-sm">
                        Indore mein wedding season bhi hai! Dry fruits ka stock badha lo.
                        <p className="mt-1 text-[0.55rem] text-slate-400">9:02 AM · Calendar alert</p>
                      </div>
                    </div>

                    {/* Input bar */}
                    <div className="flex items-center gap-2 border-t border-slate-800 bg-slate-800/60 px-3 py-2">
                      <div className="flex-1 rounded-full bg-slate-700 px-3 py-1.5 text-[0.65rem] text-slate-500">Message…</div>
                      <div className="h-6 w-6 rounded-full bg-emerald-500 flex items-center justify-center text-[0.6rem]">→</div>
                    </div>
                  </div>

                  <div className="absolute -right-3 -top-3 rounded-xl border-2 border-emerald-500/60 bg-white px-2.5 py-1.5 shadow-xl">
                    <p className="text-[0.55rem] font-bold text-emerald-600 uppercase tracking-wider">Live · at your chosen time</p>
                    <p className="text-xs font-black text-slate-800">EventBridge</p>
                  </div>
                  <div className="absolute -left-3 -bottom-3 rounded-xl border-2 border-amber-500/60 bg-white px-2.5 py-1.5 shadow-xl">
                    <p className="text-[0.55rem] font-bold text-amber-600 uppercase tracking-wider">Confidence</p>
                    <p className="text-xs font-black text-slate-800">87%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-16 overflow-hidden rounded-2xl border-2 border-slate-300 bg-white shadow-md">
            <div className="animate-marquee flex whitespace-nowrap py-3">
              {[
                'EventBridge — daily at a time that suits you',
                'Festival alerts — you choose how many days before',
                'SageMaker demand forecast — 92% confidence',
                'Bedrock explains in Hinglish',
                'Dukaan-relevant news only — price hike, GST, FMCG; no Nifty',
                'Wedding season alerts — local events',
                'DynamoDB real-time inventory',
                'S3 festival calendar synced',
                'Lambda serverless processing',
              ].concat([
                'EventBridge — daily at a time that suits you',
                'Festival alerts — you choose how many days before',
                'SageMaker demand forecast — 92% confidence',
                'Bedrock explains in Hinglish',
              ]).map((item, i) => (
                <span key={i} className="inline-flex items-center gap-2 px-6 text-xs font-semibold text-slate-700">
                  {item}
                  <span className="text-slate-400">·</span>
                </span>
              ))}
            </div>
          </div>

          {/* Scroll cue */}
          <div className="mt-8 flex justify-center">
            <div className="flex flex-col items-center gap-1 text-slate-700 font-medium animate-float">
              <span className="text-[0.65rem] font-semibold tracking-widest uppercase">scroll</span>
              <span>↓</span>
            </div>
          </div>
        </div>
      </section>

      <section className="relative z-10 border-b border-slate-200 py-8 bg-white/70 shadow-sm">
        <div className="mx-auto max-w-5xl px-4">
          <p className="text-center text-[0.65rem] font-bold uppercase tracking-[0.3em] text-slate-600 mb-6">Demo Journey — Follow These 4 Steps</p>
          <div className="flex flex-wrap items-center justify-center gap-0">
            {[
              { num: 1, icon: null, title: 'Home', sub: 'The problem', accent: 'border-slate-200 bg-slate-50', numColor: 'bg-slate-500 text-white' },
              { num: 2, icon: null, title: 'Onboarding', sub: 'Setup via chat', accent: 'border-emerald-200 bg-emerald-50', numColor: 'bg-emerald-500 text-white' },
              { num: 3, icon: null, title: 'Dashboard', sub: 'Command center', accent: 'border-emerald-200 bg-emerald-50', numColor: 'bg-emerald-500 text-white' },
              { num: 4, icon: null, title: 'Live Alerts', sub: 'Real-time view', accent: 'border-amber-200 bg-amber-50', numColor: 'bg-amber-500 text-white' },
            ].map((item, i) => (
              <div key={item.title} className="flex items-center">
                <div className={`relative flex items-center gap-3 rounded-2xl border-2 px-4 py-3 transition-all hover:-translate-y-0.5 hover:shadow-md ${item.accent}`}>
                  <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-black ${item.numColor}`}>{item.num}</span>
                  {item.icon != null ? <span className="text-xl">{item.icon}</span> : null}
                  <div className="hidden sm:block">
                    <p className="text-sm font-bold text-slate-900 leading-tight">{item.title}</p>
                    <p className="text-[0.62rem] font-medium text-slate-600 leading-tight">{item.sub}</p>
                  </div>
                </div>
                {i < 3 && (
                  <div className="flex items-center px-1.5">
                    <div className="h-px w-4 bg-slate-300" />
                    <svg className="h-3 w-3 text-slate-400 -ml-0.5" fill="currentColor" viewBox="0 0 6 6"><polygon points="0,0 6,3 0,6" /></svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section ref={storyRef} className="relative z-10 py-16 md:py-24 border-t border-slate-200 bg-white/40">
        <div className={`mx-auto max-w-5xl px-4 transition-all duration-700 ${storySeen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <p className="text-center text-xs font-bold uppercase tracking-[0.3em] text-emerald-700">The story behind AI Sahayak</p>
          <h2 className="mt-2 text-center text-3xl font-black text-slate-900 md:text-4xl">Meet Raju — Our Demo Persona</h2>
          <p className="mx-auto mt-4 max-w-xl text-center text-slate-700 font-medium">A small shopkeeper from Indore — and a problem shared by 15 million kirana owners across India.</p>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            <div className="group relative rounded-3xl border-2 border-slate-300 bg-white p-7 shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl">
              <div className="absolute -top-3 -left-3 h-8 w-8 rounded-full bg-slate-600 text-white text-xs font-black flex items-center justify-center shadow">1</div>
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-2xl font-black text-slate-500 mb-5">1</div>
              <h3 className="text-lg font-bold text-slate-900">Raju — The Kirana Owner</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-700 font-medium">Based in <strong className="text-slate-900">Rajwada area</strong>, Indore. Runs a mid-sized kirana store. Hardworking, honest — but manages inventory with <strong className="text-slate-900">memory and an old notebook</strong>.</p>
              <div className="mt-4 rounded-xl bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-800 border-2 border-slate-200">Indore, MP · Est. 2009 · 15 years running</div>
            </div>
            <div className="group relative rounded-3xl border-2 border-rose-300 bg-rose-50 p-7 shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl">
              <div className="absolute -top-3 -left-3 h-8 w-8 rounded-full bg-rose-500 text-white text-xs font-black flex items-center justify-center shadow">2</div>
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-100 text-2xl font-black text-rose-600 mb-5">2</div>
              <h3 className="text-lg font-bold text-slate-900">The Holi Season Problem</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-700 font-medium">A festival and local wedding season overlapped. Ghee and Mustard Oil ran out 3 days early — customers left empty-handed.</p>
              <div className="mt-4 rounded-xl bg-rose-100 px-3 py-2 text-sm font-bold text-rose-700 border border-rose-200">Loss: ₹15,000+ in a single festive week</div>
            </div>
            <div className="group relative rounded-3xl border-2 border-emerald-300 bg-emerald-50 p-7 shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl">
              <div className="absolute -top-3 -left-3 h-8 w-8 rounded-full bg-emerald-500 text-white text-xs font-black flex items-center justify-center shadow">3</div>
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100 text-2xl font-black text-emerald-600 mb-5">3</div>
              <h3 className="text-lg font-bold text-slate-900">The AI Sahayak Solution</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-700 font-medium"><strong className="text-slate-900">When you want</strong> — you set how many days before (e.g. 3, 5, 7). A proactive alert: &quot;Raju Bhai, Holi is coming — top up your Ghee stock!&quot; EventBridge runs daily at a time you choose.</p>
              <div className="mt-4 rounded-xl bg-emerald-100 px-3 py-2 text-sm font-bold text-emerald-700 border border-emerald-200">Proactive alert — Stock ready — Zero loss</div>
            </div>
          </div>
        </div>
      </section>

      <section ref={statsRef} className="relative z-10 py-16 md:py-24 border-t border-slate-200 bg-white/30">
        <div className={`mx-auto max-w-5xl px-4 transition-all duration-700 ${statsSeen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <p className="text-center text-xs font-bold uppercase tracking-[0.3em] text-emerald-700 mb-2">Numbers that matter</p>
          <h2 className="text-center text-3xl font-black text-slate-900 md:text-4xl mb-12">India's Kirana Stores</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { val: '12–15M', label: 'Kirana stores across India', color: 'text-amber-700', bg: 'bg-amber-50 border-amber-300' },
              { val: '~11%', label: "India's GDP contribution", color: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-300' },
              { val: '~40M', label: 'Jobs dependent on kiranas', color: 'text-sky-700', bg: 'bg-sky-50 border-sky-300' },
              { val: '₹120B+', label: 'Lost to inventory chaos yearly', color: 'text-rose-700', bg: 'bg-rose-50 border-rose-300' },
            ].map((s) => (
              <div key={s.val} className={`rounded-2xl border-2 ${s.bg} bg-white p-5 text-center shadow-md transition hover:scale-[1.02] hover:shadow-lg`}>
                <p className={`text-3xl font-black md:text-4xl ${s.color}`}>{s.val}</p>
                <p className="mt-2 text-xs font-semibold text-slate-700 leading-snug">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section ref={diffRef} className="relative z-10 py-16 md:py-24 border-t border-slate-200 bg-white/40">
        <div className={`mx-auto max-w-5xl px-4 transition-all duration-700 ${diffSeen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <p className="text-center text-xs font-bold uppercase tracking-[0.3em] text-emerald-700 mb-2">How we are different</p>
          <h2 className="text-center text-3xl font-black text-slate-900 md:text-4xl mb-4">Not Reactive — <span className="text-emerald-600">Proactive</span></h2>
          <p className="text-center text-slate-700 font-medium mb-12 max-w-xl mx-auto">Other tools only show you data. We alert you <em>proactively</em> — before the loss happens.</p>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-2xl border-2 border-slate-300 bg-white p-7 shadow-md">
              <div className="flex items-center gap-3 mb-5">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-100 text-sm font-black text-rose-600">—</span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-rose-600">The old way</p>
                  <p className="font-bold text-slate-900">Reactive</p>
                </div>
              </div>
              <ul className="space-y-3 text-sm font-medium text-slate-700">
                {['Check report → stock already empty', 'Festival arrives → realise too late', 'Customer leaves → only then reorder', 'Pure guesswork — no confidence score'].map(t => (
                  <li key={t} className="flex gap-2 items-start"><span className="text-rose-500 mt-0.5 shrink-0 font-bold">×</span>{t}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border-2 border-emerald-400 bg-emerald-50 p-7 shadow-lg">
              <div className="flex items-center gap-3 mb-5">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-200 text-sm font-black text-emerald-700">+</span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-emerald-700">AI Sahayak</p>
                  <p className="font-bold text-slate-900">Proactive</p>
                </div>
              </div>
              <ul className="space-y-3 text-sm font-medium text-slate-700">
                {['EventBridge: daily check at a time you set', 'Proactive alert — you choose how many days before', 'SageMaker: demand confidence score (92%)', 'Bedrock: explains why, in plain language'].map(t => (
                  <li key={t} className="flex gap-2 items-start"><span className="text-emerald-500 mt-0.5 shrink-0 font-bold">✓</span>{t}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section ref={techRef} className="relative z-10 py-16 md:py-24 border-t border-slate-200 bg-white/30">
        <div className={`mx-auto max-w-5xl px-4 transition-all duration-700 ${techSeen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <p className="text-center text-xs font-bold uppercase tracking-[0.3em] text-amber-700 mb-2">Powered by AWS</p>
          <h2 className="text-center text-2xl font-black text-slate-900 md:text-3xl mb-10">The AWS tech stack powering this</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {[
              { name: 'EventBridge', role: 'Daily at your chosen time', icon: null, color: 'bg-orange-50 border-orange-300' },
              { name: 'Lambda', role: 'Festival check', icon: 'λ', color: 'bg-amber-50 border-amber-300' },
              { name: 'Bedrock', role: 'Hinglish AI', icon: null, color: 'bg-violet-50 border-violet-300' },
              { name: 'SageMaker', role: 'Demand forecast', icon: null, color: 'bg-sky-50 border-sky-300' },
              { name: 'DynamoDB', role: 'Store data', icon: null, color: 'bg-emerald-50 border-emerald-300' },
              { name: 'S3', role: 'Festival calendar', icon: null, color: 'bg-green-50 border-green-300' },
            ].map((t) => (
              <div key={t.name} className={`rounded-2xl border-2 ${t.color} bg-white p-4 text-center shadow-md transition hover:-translate-y-1 hover:shadow-lg`}>
                {t.icon != null ? <span className="text-2xl block mb-2">{t.icon}</span> : <span className="block mb-2 h-8" />}
                <p className="text-xs font-black text-slate-900">{t.name}</p>
                <p className="text-[0.6rem] font-semibold text-slate-700 mt-0.5">{t.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section ref={ctaRef} className="relative z-10 py-20 md:py-28 border-t border-slate-200 bg-white/70 shadow-inner">
        <div className={`mx-auto max-w-3xl px-4 text-center transition-all duration-700 ${ctaSeen ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
          <span className="inline-block rounded-full border-2 border-amber-500 bg-amber-50 px-4 py-1.5 text-xs font-bold tracking-widest text-amber-800 uppercase mb-6">
            For Hackathon Judges
          </span>
          <h2 className="text-3xl font-black text-slate-900 md:text-4xl leading-tight">
            See the <span className="text-emerald-600">full AI Sahayak demo</span>
          </h2>
          <p className="mt-5 text-slate-700 font-semibold text-lg">Onboarding → Dashboard → Live Alerts — a complete proactive AI demo in under 2 minutes.</p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
            <button type="button" onClick={onStart} className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-10 py-4 text-base font-black text-white shadow-lg transition hover:bg-emerald-600 hover:scale-[1.02] active:scale-[0.98]">
              Start the Demo →
            </button>
            <button type="button" onClick={onSkipToDashboard} className="rounded-full border-2 border-slate-300 bg-white px-7 py-4 text-sm font-semibold text-slate-700 hover:bg-slate-50">
              Dashboard →
            </button>
            <button type="button" onClick={onSkipToDay} className="rounded-full border-2 border-slate-300 bg-white px-7 py-4 text-sm font-semibold text-slate-700 hover:bg-slate-50">
              Live Alerts →
            </button>
          </div>
          <div className="mt-12 rounded-2xl border-2 border-amber-400 bg-amber-50 px-6 py-5 text-left max-w-lg mx-auto shadow-md">
            <p className="text-xs font-bold uppercase tracking-widest text-amber-800 mb-2">Note for Hackathon Judges</p>
            <p className="text-sm font-semibold text-slate-800"><strong className="text-slate-900">Step 2 (Onboarding)</strong> → then <strong>Dashboard</strong> → <strong>Live Alerts</strong>. End-to-end ~2 min. Backend connect for live AI responses.</p>
          </div>
        </div>
      </section>

      <footer className="relative z-10 bg-slate-100/95 pt-0 pb-5">
        {/* Tricolor strip = top edge of footer (orange/amber starts the footer) */}
        <div className="h-1 w-full shrink-0 rounded-none bg-gradient-to-r from-sahayak-amber via-emerald-500 to-sahayak-green" />
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 pt-4 sm:flex-nowrap">
          <div className="min-w-0 flex-1 text-left">
            <p className="text-xs font-semibold text-slate-700">AWS AI for Bharat Hackathon · Professional Track · Retail &amp; Market Intelligence</p>
            <p className="mt-1 text-xs font-medium text-slate-600">Built for India&apos;s 15M Kirana stores</p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" aria-hidden />
            <span className="text-sm font-bold text-slate-800">AI Sahayak</span>
          </div>
        </div>
      </footer>
    </main>
  )
}
/** Optional: pass this to wire your real bot. Called when user sends a message; return the bot reply and optional quick-reply buttons. */
export type OnboardingBotReply = (userMessage: string) => Promise<{ reply: string; suggestedActions?: string[] }>
/** Optional: called when user uploads a photo (camera/gallery). Return the bot reply. */
export type OnboardingImageUpload = (base64: string, mimeType: string) => Promise<string>
/** Optional: voice message – send audio, get back reply + transcribed text (e.g. via Amazon Transcribe). */
export type OnboardingVoiceMessage = (audioBase64: string, mimeType: string) => Promise<{ reply: string; transcribed_text?: string }>

type ChatOnboardingProps = {
  onContinue: () => void
  /** Wire your bot here. When user sends a message in the phone, this is called with the text; return the bot's reply to show it in the chat. */
  onBotReply?: OnboardingBotReply
  /** When user picks a photo (camera button), this is called with base64 + mime type; return the bot's reply. */
  onImageUpload?: OnboardingImageUpload
  /** When user sends a voice message, this is called with base64 audio; returns { reply, transcribed_text } (e.g. Amazon Transcribe ASR). */
  onVoiceMessage?: OnboardingVoiceMessage
}

// Pre-loaded demo conversation for hackathon demo flow

// Pre-loaded demo conversation for hackathon demo flow
// Real 7-question onboarding flow matching the WhatsApp backend
const onboardingScript: { from: 'user' | 'bot'; text: string }[] = [
  { from: 'bot',  text: 'Namaste! Main AI Sahayak hoon. Aapka naam kya hai?' },
  { from: 'user', text: 'Raju Verma' },
  { from: 'bot',  text: 'Nice to meet you, Raju! Aapki dukan ka naam kya hai?' },
  { from: 'user', text: 'Raju Kirana Store' },
  { from: 'bot',  text: 'What type of store is it? Kirana Store / General Store / Other?' },
  { from: 'user', text: 'Kirana Store' },
  { from: 'bot',  text: 'Super! You run a Kirana store. What is your shop location? You can manually enter an address or share your current location.' },
  { from: 'user', text: 'Rajwada, Indore, MP — Location shared!' },
  { from: 'bot',  text: 'Got it! Your location is Indore. What is your shop\'s 6-digit Pincode?' },
  { from: 'user', text: '452001' },
  { from: 'bot',  text: 'Nice! Your Pincode is 452001. Please enter your Aadhar number or upload a photo of your Aadhar card for verification.' },
  { from: 'user', text: '23982476980241' },
  { from: 'bot',  text: 'Aadhar number received! Do you have a GST number for your business? If yes, please provide it.' },
  { from: 'user', text: '216982189c21cpx9u5' },
  { from: 'bot',  text: 'GST number received! You are all set, Raju Verma!\n\nYour Sahayak Analytics Dashboard Login\nUser ID: 919136359345\nPassword: Raju9136\n\n(Please save these for future access)' },
]

/** Strip emojis and, for language-question messages, the trailing (English, Hindi, ...). Preserve newlines so "User ID" and "Password" stay on separate lines. */
function cleanBotMessageDisplay(text: string): string {
  const noEmoji = text.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F1E0}-\u{1F1FF}\u{FE00}-\u{FE0F}\u{200D}]/gu, '')
  const collapseSpacesOnly = noEmoji.replace(/[^\S\n]+/g, ' ').trim() // keep newlines, collapse spaces
  const isLanguageQuestion = /language|kis bhasha|bhasha me|boloon|bhasha mein|kis boli|kaun si bhasha|chat karna hai|chahte hain/i.test(collapseSpacesOnly)
  if (isLanguageQuestion)
    return collapseSpacesOnly.replace(/\s*\(English[^)]*\)\s*\.?\s*$/i, '').trim()
  return collapseSpacesOnly
}

function renderMarkdown(text: string): JSX.Element[] {
  // Simple markdown parser for bold (**text**) and bullet lists (- item)
  const lines = text.split('\n')
  const elements: JSX.Element[] = []
  
  lines.forEach((line, idx) => {
    // Handle bold text: **text** -> <strong>text</strong>
    const parts: (string | JSX.Element)[] = []
    let remaining = line
    let key = 0
    
    while (remaining.length > 0) {
      const boldMatch = remaining.match(/\*\*([^*]+)\*\*/)
      if (boldMatch && boldMatch.index !== undefined) {
        // Add text before bold
        if (boldMatch.index > 0) {
          parts.push(remaining.substring(0, boldMatch.index))
        }
        // Add bold text
        parts.push(<strong key={`bold-${idx}-${key++}`}>{boldMatch[1]}</strong>)
        remaining = remaining.substring(boldMatch.index + boldMatch[0].length)
      } else {
        parts.push(remaining)
        break
      }
    }
    
    // Handle bullet points
    if (line.trim().startsWith('- ')) {
      elements.push(
        <div key={idx} style={{ marginLeft: '1em', marginTop: idx > 0 ? '0.3em' : 0 }}>
          • {parts.map((p, i) => typeof p === 'string' ? p.replace(/^- /, '') : <span key={i}>{p}</span>)}
        </div>
      )
    } else if (parts.length > 0) {
      elements.push(
        <div key={idx} style={{ marginTop: idx > 0 && line.trim() !== '' ? '0.5em' : 0 }}>
          {parts.map((p, i) => typeof p === 'string' ? p : <span key={i}>{p}</span>)}
        </div>
      )
    }
  })
  
  return elements
}

function ChatOnboarding({ onContinue, onBotReply, onImageUpload, onVoiceMessage }: ChatOnboardingProps) {
  const liveClock = useLiveClock()
  const [step, setStep] = useState(1)
  const [liveMessages, setLiveMessages] = useState<{ from: 'user' | 'bot'; text: string; time?: string }[]>([])
  const [lastSuggestedActions, setLastSuggestedActions] = useState<string[]>([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [recording, setRecording] = useState(false)
  const firstMessageRequestedRef = useRef(false)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const docInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const [playingTtsIdx, setPlayingTtsIdx] = useState<number | null>(null)
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null)
  const agentApiBase = (import.meta as any).env?.VITE_AGENT_API_BASE || 'http://localhost:8000'

  const scriptMessages = onboardingScript.slice(0, step)
  const visibleMessages = liveMessages
  const atEnd = step >= onboardingScript.length

  const scrollToBottom = () => chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(() => { scrollToBottom() }, [visibleMessages.length])

  // Show the hardcoded English welcome + language-poll immediately — never call the LLM for this.
  // The bot's Stage 1 prompt says to ask exactly this, so we skip the round-trip and keep it predictable.
  useEffect(() => {
    if (firstMessageRequestedRef.current) return
    firstMessageRequestedRef.current = true
    const now = new Date()
    setLiveMessages([{
      from: 'bot',
      text: 'Namaste! Welcome to AI Sahayak. What is your preferred language for communication?',
      time: formatISTTime(now),
    }])
    setLastSuggestedActions(['English', 'Hindi', 'Hinglish'])
  }, [])

  useEffect(() => {
    if (atEnd) return
    const timer = setTimeout(
      () => setStep((s) => Math.min(s + 1, onboardingScript.length)),
      1400
    )
    return () => clearTimeout(timer)
  }, [atEnd])

  const nowTime = () => formatISTTime(new Date())

  async function sendUserMessage(text: string) {
    if (!text.trim() || sending) return
    setLastSuggestedActions([])
    setLiveMessages((prev) => [...prev, { from: 'user', text: text.trim(), time: nowTime() }])
    setSending(true)
    try {
      if (onBotReply) {
        const result = await onBotReply(text.trim())
        if (result.reply) setLiveMessages((prev) => [...prev, { from: 'bot', text: result.reply, time: nowTime() }])
        setLastSuggestedActions(result.suggestedActions ?? [])
      } else {
        setLiveMessages((prev) => [
          ...prev,
          { from: 'bot', text: 'Demo mode: connect your bot by passing onBotReply to ChatOnboarding.', time: nowTime() },
        ])
      }
    } catch {
      setLiveMessages((prev) => [
        ...prev,
        { from: 'bot', text: 'Something went wrong. Please try again.', time: nowTime() },
      ])
    } finally {
      setSending(false)
    }
  }

  async function handleSend() {
    const text = inputValue.trim()
    if (!text || sending) return
    setInputValue('')
    await sendUserMessage(text)
  }

  function readFileAsBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const dataUrl = reader.result as string
        const base64 = dataUrl.split(',')[1] ?? ''
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  async function handleCameraFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file || !file.type.startsWith('image/')) return
    setLiveMessages((prev) => [...prev, { from: 'user', text: 'Photo attached', time: nowTime() }])
    setSending(true)
    try {
      const base64 = await readFileAsBase64(file)
      const mimeType = file.type || 'image/jpeg'
      if (onImageUpload) {
        const reply = await onImageUpload(base64, mimeType)
        if (reply) setLiveMessages((prev) => [...prev, { from: 'bot', text: reply, time: nowTime() }])
      } else {
        setLiveMessages((prev) => [...prev, { from: 'bot', text: 'Photo received. You can send more or type a message.', time: nowTime() }])
      }
    } catch {
      setLiveMessages((prev) => [...prev, { from: 'bot', text: 'Could not upload photo. Please try again.', time: nowTime() }])
    } finally {
      setSending(false)
    }
  }

  async function handleDocFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    const name = file.name
    const userMsg = `Document attached: ${name}`
    setLiveMessages((prev) => [...prev, { from: 'user', text: userMsg, time: nowTime() }])
    setSending(true)
    try {
      if (onBotReply) {
        const result = await onBotReply(`Document attached: ${name}`)
        if (result.reply) setLiveMessages((prev) => [...prev, { from: 'bot', text: result.reply, time: nowTime() }])
        setLastSuggestedActions(result.suggestedActions ?? [])
      } else {
        setLiveMessages((prev) => [...prev, { from: 'bot', text: "Thanks for uploading. We'll use this for verification.", time: nowTime() }])
      }
    } catch {
      setLiveMessages((prev) => [...prev, { from: 'bot', text: "Something went wrong. Please try again.", time: nowTime() }])
    } finally {
      setSending(false)
    }
  }

  async function startVoiceRecording() {
    if (!onVoiceMessage || sending || recording) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm'
      const recorder = new MediaRecorder(stream)
      recorder.ondataavailable = (e) => { if (e.data.size) audioChunksRef.current.push(e.data) }
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(audioChunksRef.current, { type: mime })
        const reader = new FileReader()
        reader.onloadend = async () => {
          const base64 = (reader.result as string)?.split(',')[1] ?? ''
          if (!base64) return
          setSending(true)
          const t = nowTime()
          setLiveMessages((prev) => [...prev, { from: 'user', text: '…', time: t }])
          try {
            const result = await onVoiceMessage(base64, mime)
            const t2 = nowTime()
            setLiveMessages((prev) => {
              const withoutPlaceholder = prev.slice(0, -1)
              const userText = result.transcribed_text || 'Voice message'
              return [...withoutPlaceholder, { from: 'user', text: userText, time: t2 }, { from: 'bot', text: result.reply, time: t2 }]
            })
          } catch {
            const t2 = nowTime()
            setLiveMessages((prev) => {
              const withoutPlaceholder = prev.slice(0, -1)
              return [...withoutPlaceholder, { from: 'user', text: 'Voice message', time: t2 }, { from: 'bot', text: 'Voice not available. Please type your message.', time: t2 }]
            })
          } finally {
            setSending(false)
          }
        }
        reader.readAsDataURL(blob)
      }
      mediaRecorderRef.current = recorder
      recorder.start(200)
      setRecording(true)
    } catch (err) {
      console.error('Microphone access error', err)
    }
  }

  function stopVoiceRecording() {
    if (!recording || !mediaRecorderRef.current) return
    mediaRecorderRef.current.stop()
    mediaRecorderRef.current = null
    setRecording(false)
  }

  function toggleVoiceRecording() {
    if (recording) stopVoiceRecording()
    else startVoiceRecording()
  }

  async function playTts(text: string, msgIdx: number) {
    if (!text.trim() || playingTtsIdx !== null) return
    setPlayingTtsIdx(msgIdx)
    try {
      const res = await fetch(`${agentApiBase}/v1/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim(), language_code: 'hi-IN' }),
      })
      if (!res.ok) throw new Error('TTS failed')
      const data = await res.json()
      const binary = atob(data.audio_base64)
      const bytes = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
      const blob = new Blob([bytes], { type: 'audio/mpeg' })
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)
      ttsAudioRef.current = audio
      audio.onended = () => { URL.revokeObjectURL(url); setPlayingTtsIdx(null) }
      audio.onerror = () => { URL.revokeObjectURL(url); setPlayingTtsIdx(null) }
      await audio.play()
    } catch {
      setPlayingTtsIdx(null)
    }
  }

  function stopTts() {
    if (ttsAudioRef.current) {
      ttsAudioRef.current.pause()
      ttsAudioRef.current = null
    }
    setPlayingTtsIdx(null)
  }

  return (
    <main style={{ display: 'flex', flexDirection: 'row', height: 'calc(100vh - 4.5rem)', overflow: 'hidden', position: 'relative', zIndex: 10 }}>

      {/* ══════════════ LEFT PANEL — Bharat light theme ══════════════ */}
      <section className="relative flex flex-col border-r border-slate-200 bg-gradient-to-br from-amber-50/40 via-white/60 to-emerald-50/40"
               style={{ width: '54%', padding: '1rem 1.5rem 0.75rem', overflow: 'hidden', flexShrink: 0 }}>

        <div className="pointer-events-none absolute inset-0"
             style={{ background: 'radial-gradient(ellipse 70% 60% at 0% 30%, rgba(34,197,94,0.12) 0%, transparent 60%)' }} />
        <div className="pointer-events-none absolute inset-0"
             style={{ background: 'radial-gradient(ellipse 50% 50% at 100% 0%, rgba(251,191,36,0.08) 0%, transparent 60%)' }} />

        <div className="relative" style={{ marginBottom: '0.55rem', flexShrink: 0 }}>
          <span className="inline-block rounded-full bg-emerald-500/15 border border-emerald-400/50 px-3 py-1 text-[0.65rem] font-black uppercase tracking-wider text-emerald-700 mb-3">
            Under 60 seconds
          </span>
          <h2 className="text-3xl font-black leading-tight tracking-tight text-slate-900 md:text-[2rem]" style={{ letterSpacing: '-0.03em' }}>
            Zero forms.<br />
            <span className="bg-gradient-to-r from-emerald-600 via-emerald-500 to-cyan-600 bg-clip-text text-transparent">
              Just WhatsApp.
            </span>
          </h2>
          <p className="mt-2 text-sm font-semibold leading-relaxed text-slate-700 max-w-[440px]">
            A kirana owner onboards via WhatsApp — no app, no form, no store visit.
          </p>
        </div>

        {/* ── INFO CARD: Bharat theme — tricolor top, light card ── */}
        <div
          className="relative border-2 border-slate-300 bg-white shadow-lg"
          style={{
            flex: '1 1 auto',
            minHeight: 0,
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 16,
            color: '#0f172a',
            overflow: 'hidden',
          }}
        >
          <div className="h-1 w-full shrink-0 bg-gradient-to-r from-[#f59e0b] via-emerald-500 to-[#16a34a]" />
          <div className="flex flex-col gap-4 p-4 sm:p-5">
            {/* What this page is */}
            <div className="rounded-xl border-l-4 border-emerald-500 bg-emerald-50/70 px-4 py-3">
              <p className="text-[0.65rem] font-black uppercase tracking-widest text-emerald-700 mb-1.5">What this page is</p>
              <p className="text-[0.8rem] font-medium leading-relaxed text-slate-800">
                <strong className="text-slate-900">Onboarding.</strong> A kirana owner answers 7 questions in a chat — no forms, no app. The phone on the right is a <strong className="text-slate-900">web demo</strong> that looks like WhatsApp. In production, the same chat runs on <strong className="text-slate-900">real WhatsApp</strong> on the store owner&apos;s phone.
              </p>
            </div>

            {/* Demo → Production */}
            <div className="rounded-xl border-2 border-emerald-300 bg-gradient-to-br from-emerald-50 to-cyan-50/50 px-4 py-3 shadow-sm">
              <p className="text-[0.65rem] font-black uppercase tracking-widest text-emerald-800 mb-1.5">Demo → Production</p>
              <p className="text-[0.75rem] font-semibold leading-relaxed text-slate-800">
                <strong className="text-slate-900">Now (demo):</strong> You see a web UI that mimics WhatsApp. <strong className="text-slate-900">Later (production):</strong> Same 7 questions, same AI — store owner chats on WhatsApp. Name &amp; phone from WhatsApp; location from &quot;Send location.&quot;
              </p>
            </div>

            {/* Tech stack */}
            <div className="rounded-xl border-l-4 border-sky-500 bg-sky-50/70 px-4 py-3">
              <p className="text-[0.65rem] font-black uppercase tracking-widest text-sky-700 mb-2">Tech stack (AWS)</p>
              <p className="text-[0.72rem] font-medium text-slate-700 mb-2">Receive messages, run AI, store data, create login.</p>
              <div className="flex flex-wrap gap-2">
                {['WhatsApp Cloud API', 'Lambda', 'Bedrock', 'DynamoDB', 'Cognito'].map((t) => (
                  <span key={t} className="rounded-lg border-2 border-sky-300 bg-white px-2.5 py-1.5 text-[0.68rem] font-bold text-sky-700 shadow-sm">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Steps (what happens) */}
            <div className="rounded-xl border-l-4 border-violet-500 bg-violet-50/70 px-4 py-3">
              <p className="text-[0.65rem] font-black uppercase tracking-widest text-violet-700 mb-2">Steps (what happens)</p>
              <p className="text-[0.72rem] font-medium text-slate-700 mb-2">AI asks these 7 things in order; then we create dashboard login.</p>
              <ol className="space-y-1.5 text-[0.78rem] font-semibold text-slate-800">
                {['Name', 'Shop name', 'Store type (Kirana / General)', 'Location (e.g. Send location in WA)', 'Pincode', 'Aadhar (number or photo)', 'GST (optional)'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-500 text-[0.6rem] font-black text-white">{i + 1}</span>
                    {item}
                  </li>
                ))}
              </ol>
            </div>

            {/* Numbers — stats bar */}
            <div className="flex flex-wrap items-center gap-4 rounded-xl border-2 border-slate-200 bg-slate-50 px-4 py-3">
              <span className="text-[0.7rem] font-bold text-slate-600">In numbers:</span>
              <span className="flex items-baseline gap-1"><span className="text-lg font-black text-emerald-600">47s</span><span className="text-[0.65rem] font-semibold text-slate-600">setup</span></span>
              <span className="flex items-baseline gap-1"><span className="text-lg font-black text-sky-600">~60s</span><span className="text-[0.65rem] font-semibold text-slate-600">store live</span></span>
              <span className="flex items-baseline gap-1"><span className="text-lg font-black text-violet-600">7</span><span className="text-[0.65rem] font-semibold text-slate-600">questions</span></span>
            </div>
          </div>
        </div>

        {/* ── CTA at bottom ── */}
        <div className="relative" style={{ marginTop: 'auto', paddingTop: '0.5rem', paddingBottom: '0.5rem', flexShrink: 0 }}>
          {atEnd ? (
            <button type="button" onClick={onContinue}
              className="group flex items-center gap-2 rounded-2xl font-black text-white shadow-lg transition hover:scale-[1.02] active:scale-[0.98] border-2 border-emerald-600/50"
              style={{ background: 'linear-gradient(135deg, #059669, #0891b2)', padding: '0.75rem 1.75rem', fontSize: '0.9rem', boxShadow: '0 8px 28px -4px rgba(5,150,105,0.5)' }}>
              <span>Open Growth Dashboard</span>
              <span className="text-lg leading-none">→</span>
            </button>
          ) : (
            <div className="flex items-center gap-2 rounded-xl border-2 border-emerald-200 bg-emerald-50/80 px-3 py-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shrink-0" />
              <p className="text-sm font-bold text-slate-700">Live onboarding in progress — watch the chat →</p>
            </div>
          )}
        </div>

      </section>

      {/* ══════════════ RIGHT PANEL — Bharat theme, phone ══════════════ */}
      <section className="bg-gradient-to-bl from-emerald-50/30 via-white/20 to-amber-50/25" style={{ flex: '1 1 0%', display: 'grid', placeItems: 'center', overflow: 'hidden', position: 'relative', zIndex: 10 }}>

        {/* Bharat glow */}
        <div className="pointer-events-none absolute inset-0"
             style={{ background: 'radial-gradient(ellipse 80% 80% at 50% 50%, rgba(34,197,94,0.08) 0%, transparent 70%)' }} />
        <div className="pointer-events-none absolute inset-0"
             style={{ background: 'radial-gradient(ellipse 60% 60% at 80% 20%, rgba(251,191,36,0.06) 0%, transparent 60%)' }} />

        {/* Scan badge — Bharat, bold */}
        <div className="absolute top-3 right-3 z-10 flex items-center gap-2 rounded-xl border-2 border-emerald-400 bg-white px-3 py-2 shadow-xl">
          <svg className="h-4 w-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="3" y="3" width="7" height="7" rx="1" strokeWidth={1.5}/><rect x="14" y="3" width="7" height="7" rx="1" strokeWidth={1.5}/><rect x="3" y="14" width="7" height="7" rx="1" strokeWidth={1.5}/>
            <path d="M14 14h3v3h-3zm4 0h3v3h-3zm0 4h3v3h-3zm-4 0h3" strokeWidth={1.5}/>
          </svg>
          <div>
            <p className="text-[0.65rem] font-black text-emerald-700 uppercase tracking-wider leading-tight">Scan to Onboard</p>
            <p className="text-[0.55rem] font-semibold text-slate-600 leading-tight">Opens WhatsApp instantly</p>
          </div>
        </div>

        {/* Live badge — Bharat, bold */}
        <div className="absolute bottom-3 left-3 z-10 flex items-center gap-2 rounded-xl border-2 border-slate-300 bg-white px-3 py-2 shadow-xl">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[0.7rem] font-black text-slate-800 uppercase tracking-wider">Live Demo · Raju</span>
        </div>

        {/* ── PHONE — fills the right panel height ── */}
        <div className="relative" style={{ width: 'min(290px, 36vw)', height: 'min(560px, calc(100vh - 4.5rem - 1rem))', flexShrink: 0, zIndex: 20 }}>
          {/* Side buttons */}
          <div style={{ position: 'absolute', left: -4, top: '18%', width: 3, height: 32, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', left: -4, top: '26%', width: 3, height: 22, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', left: -4, top: '32%', width: 3, height: 22, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', right: -4, top: '22%', width: 3, height: 44, background: '#334155', borderRadius: '0 2px 2px 0' }} />

          {/* Shell — iPhone frame, light WA theme inside */}
          <div className="relative flex h-full w-full flex-col" style={{ borderRadius: '2.4rem', border: '6px solid #1a1a1a', background: '#fff', overflow: 'hidden', isolation: 'isolate', zIndex: 20, boxShadow: '0 0 0 1px rgba(0,0,0,0.15), 0 0 0 2px rgba(0,0,0,0.08), 0 32px 64px -8px rgba(0,0,0,0.7), 0 0 40px -8px rgba(34,197,94,0.15), inset 0 1px 0 rgba(255,255,255,0.3)' }}>

            {/* Dynamic island */}
            <div style={{ position: 'absolute', zIndex: 30, top: 8, left: '50%', transform: 'translateX(-50%)', width: 66, height: 18, borderRadius: 18, background: '#000' }} />

            <div className="flex h-full flex-col">

              {/* ── STATUS BAR — iOS light ── */}
              <div style={{ background: '#075e54', padding: '10px 18px 5px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
                <span style={{ color: '#fff', fontSize: '0.62rem', fontWeight: 700 }}>{formatISTStatusTime(liveClock)}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span style={{ display: 'flex', alignItems: 'flex-end', gap: '2px', height: 9 }}>
                    {[3,5,7,9].map(h => <span key={h} style={{ width: 2, height: h, background: '#fff', borderRadius: 1 }} />)}
                  </span>
                  <svg style={{ width: 10, height: 10, color: '#fff' }} fill="currentColor" viewBox="0 0 24 24"><path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3a4.237 4.237 0 00-6 0zm-4-4l2 2a7.074 7.074 0 0110 0l2-2C15.14 9.14 8.87 9.14 5 13z"/></svg>
                  <span style={{ display: 'inline-flex', alignItems: 'center', border: '1.5px solid rgba(255,255,255,0.8)', borderRadius: 3, padding: '1px 2px' }}>
                    <span style={{ width: 12, height: 5, background: '#4ade80', borderRadius: 1 }} />
                    <span style={{ width: 2, height: 3, background: 'rgba(255,255,255,0.5)', borderRadius: '0 1px 1px 0', alignSelf: 'center', marginLeft: 1 }} />
                  </span>
                </div>
              </div>

              {/* ── APP BAR — WhatsApp green header ── */}
              <div style={{ background: '#075e54', padding: '6px 10px 10px', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                {/* Back arrow */}
                <button type="button" style={{ color: '#fff', padding: '0 2px', flexShrink: 0, background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 1 }} aria-label="Back">
                  <svg style={{ width: 16, height: 16 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" /></svg>
                </button>
                {/* Avatar */}
                <div style={{ position: 'relative', flexShrink: 0 }}>
                  <div style={{ width: 32, height: 32, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', background: '#128c7e', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#fff' }}>AI</span>
                  </div>
                  <span style={{ position: 'absolute', bottom: 0, right: 0, width: 9, height: 9, borderRadius: '50%', background: '#4ade80', border: '1.5px solid #075e54' }} />
                </div>
                {/* Name + status */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: '0.88rem', fontWeight: 700, color: '#fff', lineHeight: 1.1 }}>AI Sahayak</p>
                  <p style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.75)', lineHeight: 1 }}>online · typing…</p>
                </div>
                {/* Right icons — video + phone */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 3 }} aria-label="Video call">
                    <svg style={{ width: 16, height: 16 }} fill="currentColor" viewBox="0 0 24 24"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>
                  </button>
                  <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 3 }} aria-label="Voice call">
                    <svg style={{ width: 16, height: 16 }} fill="currentColor" viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
                  </button>
                  <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 3 }} aria-label="Menu">
                    <svg style={{ width: 14, height: 14 }} fill="currentColor" viewBox="0 0 24 24"><path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>
                  </button>
                </div>
              </div>

              {/* ── CHAT AREA — WA beige background with subtle tiles ── */}
              <div className="flex flex-1 flex-col gap-1.5 overflow-y-auto px-2 py-2"
                   style={{ background: '#efeae2', backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")" }}>

                {/* Date pill — same format as Live Alerts */}
                <div style={{ display: 'flex', justifyContent: 'center', margin: '0 0 6px' }}>
                  <span style={{ fontSize: '0.55rem', color: '#667781', background: '#d4d0c8', padding: '2px 10px', borderRadius: 8, fontWeight: 500 }}>TODAY · {getTodayDatePill()}</span>
                </div>

                {(() => {
                  const stripEmoji = (s: string) => s.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F1E0}-\u{1F1FF}]/gu, '').replace(/\s+/g, ' ').trim()
                  const lastBot = [...visibleMessages].reverse().find(m => m.from === 'bot')
                  const revBotIdx = [...visibleMessages].reverse().findIndex(m => m.from === 'bot')
                  const lastBotIdx = revBotIdx === -1 ? -1 : visibleMessages.length - 1 - revBotIdx
                  const isLanguageQuestion = lastBot?.text && /language|kis bhasha|bhasha me|boloon|bhasha mein|kis boli|kaun si bhasha|chat karna hai|chahte hain/i.test(lastBot.text)
                  const languagePollOptions = lastSuggestedActions.length > 0 ? lastSuggestedActions : isLanguageQuestion ? ['English', 'Hindi', 'Hinglish'] : []
                  return visibleMessages.map((msg, idx) => (
                    <div key={`${msg.from}-${idx}`} style={{ display: 'flex', flexDirection: 'column' as const, alignItems: msg.from === 'user' ? 'flex-end' : 'flex-start' }}>
                      <div style={{ display: 'flex', justifyContent: msg.from === 'user' ? 'flex-end' : 'flex-start' }}>
                        <div style={{
                          maxWidth: '85%',
                          borderRadius: msg.from === 'user' ? '8px 8px 2px 8px' : '8px 8px 8px 2px',
                          padding: '6px 8px 4px',
                          background: msg.from === 'user' ? '#d9fdd3' : '#ffffff',
                          color: '#111b21',
                          fontSize: '0.76rem',
                          lineHeight: 1.45,
                          wordBreak: msg.from === 'user' ? ('normal' as const) : ('break-word' as const),
                          boxShadow: '0 1px 2px rgba(0,0,0,0.13)',
                          position: 'relative' as const,
                        }}>
                          {msg.from === 'bot' && idx === 0 && (
                            <div style={{ position: 'absolute', left: -6, top: 0, width: 0, height: 0, borderTop: '8px solid #fff', borderLeft: '6px solid transparent' }} />
                          )}
                          {msg.from === 'bot' ? (
                            <div style={{ color: '#111b21' }}>{renderMarkdown(cleanBotMessageDisplay(msg.text))}</div>
                          ) : (
                            <span style={{ display: 'block', whiteSpace: 'pre-wrap', color: '#111b21' }}>{msg.text}</span>
                          )}
                          {msg.from === 'bot' && msg.text.trim() && (
                            <button type="button" onClick={() => playingTtsIdx === idx ? stopTts() : playTts(cleanBotMessageDisplay(msg.text), idx)} title={playingTtsIdx === idx ? 'Stop' : 'Play'}
                              style={{ marginTop: 4, padding: 2, background: 'none', border: 'none', cursor: 'pointer', color: '#667781' }} aria-label={playingTtsIdx === idx ? 'Stop' : 'Play'}>
                              {playingTtsIdx === idx ? (
                                <svg style={{ width: 14, height: 14 }} fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h12v12H6z"/></svg>
                              ) : (
                                <svg style={{ width: 14, height: 14 }} fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                              )}
                            </button>
                          )}
                          {msg.from === 'bot' && (msg.text.toLowerCase().includes('location') || msg.text.toLowerCase().includes('pincode')) && !msg.text.toLowerCase().includes('user id:') && (
                            <button type="button"
                              onClick={() => setLiveMessages(prev => [...prev, { from: 'user', text: 'Rajwada, Indore, MP — Location shared!', time: nowTime() }])}
                              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5, marginTop: 6, width: '100%', background: '#f0fdf4', border: '1px solid #86efac', borderRadius: 6, padding: '6px 8px', cursor: 'pointer', color: '#15803d' }}>
                              <svg style={{ width: 12, height: 12, flexShrink: 0 }} fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                              <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>Send location</span>
                            </button>
                          )}
                          {msg.from === 'bot' && msg.text.toLowerCase().includes('aadhar') && !msg.text.toLowerCase().includes('user id:') && (
                            <button type="button" onClick={() => docInputRef.current?.click()}
                              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5, marginTop: 6, width: '100%', background: '#faf5ff', border: '1px solid #d8b4fe', borderRadius: 6, padding: '6px 8px', cursor: 'pointer', color: '#7c3aed' }}>
                              <svg style={{ width: 12, height: 12, flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                              <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>Upload Aadhar photo</span>
                            </button>
                          )}
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 3, marginTop: 3 }}>
                            <span style={{ fontSize: '0.52rem', color: '#667781' }}>{msg.time ?? formatISTTime(new Date())}</span>
                            {msg.from === 'user' && (
                              <svg style={{ width: 13, height: 13, color: '#53bdeb' }} fill="currentColor" viewBox="0 0 24 24"><path d="M18 7l-1.41-1.41-6.34 6.34 1.41 1.41L18 7zm4.24-1.41L11.66 16.17 7.48 12l-1.41 1.41L11.66 19l12-12-1.42-1.41zM.41 13.41L6 19l1.41-1.41L1.83 12 .41 13.41z"/></svg>
                            )}
                          </div>
                        </div>
                      </div>
                      {/* Poll-style language options directly under this bot message */}
                      {msg.from === 'bot' && idx === lastBotIdx && languagePollOptions.length > 0 && (
                        <div style={{ maxWidth: '85%', marginTop: 6, display: 'flex', flexDirection: 'column' as const, gap: 6 }}>
                          {languagePollOptions.map((label) => {
                            const displayLabel = stripEmoji(label) || label
                            return (
                              <button
                                key={label}
                                type="button"
                                onClick={() => sendUserMessage(label)}
                                disabled={sending}
                                style={{
                                  width: '100%',
                                  textAlign: 'left' as const,
                                  background: '#fff',
                                  border: '1px solid #d1d7db',
                                  borderRadius: 8,
                                  padding: '10px 12px',
                                  fontSize: '0.76rem',
                                  fontWeight: 600,
                                  color: '#111b21',
                                  cursor: sending ? 'not-allowed' : 'pointer',
                                  boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
                                }}
                              >
                                {displayLabel}
                              </button>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  ))
                })()}

                {sending && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div style={{ background: '#fff', borderRadius: '8px 8px 8px 2px', padding: '8px 14px', display: 'flex', gap: 4, alignItems: 'center', boxShadow: '0 1px 2px rgba(0,0,0,0.13)' }}>
                      {[0,150,300].map(d => <span key={d} className="rounded-full animate-bounce" style={{ width: 5, height: 5, background: '#8696a0', animationDelay: `${d}ms`, display: 'inline-block' }} />)}
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden" aria-hidden onChange={handleCameraFile} />
              <input ref={docInputRef} type="file" accept=".pdf,image/*,.doc,.docx" className="hidden" aria-hidden onChange={handleDocFile} />

              {/* ── INPUT BAR — real WA style ── */}
              <div style={{ background: '#f0f2f5', borderTop: '1px solid #e9edef', padding: '6px 8px', flexShrink: 0 }}>
                {/* Message row */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  {/* Emoji button */}
                  <button type="button" style={{ color: '#8696a0', background: 'none', border: 'none', cursor: 'pointer', padding: 2, flexShrink: 0 }} aria-label="Emoji">
                    <svg style={{ width: 20, height: 20 }} fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/></svg>
                  </button>
                  {/* Input field */}
                  <div style={{ flex: 1, display: 'flex', alignItems: 'center', background: '#fff', borderRadius: 22, padding: '5px 12px', boxShadow: '0 1px 2px rgba(0,0,0,0.08)' }}>
                    <input type="text" value={inputValue} onChange={e => setInputValue(e.target.value)} onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()} placeholder="Message" disabled={sending}
                      style={{ flex: 1, minWidth: 0, background: 'transparent', border: 'none', outline: 'none', fontSize: '0.76rem', color: '#111b21' }} />
                    {/* Sticker icon in input */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#8696a0' }}>
                      <svg style={{ width: 14, height: 14 }} fill="currentColor" viewBox="0 0 24 24"><path d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>
                    </div>
                  </div>
                  {/* Send / Mic button */}
                  <button type="button" onClick={inputValue.trim() ? handleSend : toggleVoiceRecording} disabled={sending} aria-label={inputValue.trim() ? 'Send' : 'Voice'}
                    style={{ width: 36, height: 36, borderRadius: '50%', background: '#128c7e', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: 'pointer', flexShrink: 0, boxShadow: '0 2px 8px rgba(18,140,126,0.5)' }}>
                    {inputValue.trim() ? (
                      <svg style={{ width: 16, height: 16 }} fill="currentColor" viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
                    ) : (
                      <svg style={{ width: 16, height: 16 }} fill="currentColor" viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V7a3 3 0 0 0-6 0v4a3 3 0 0 0 3 3z" /><path d="M19 11a1 1 0 0 0-2 0 5 5 0 0 1-10 0 1 1 0 0 0-2 0 7 7 0 0 0 6 6.92V21a1 1 0 0 0 2 0v-3.08A7 7 0 0 0 19 11z" /></svg>
                    )}
                  </button>
                </div>
              </div>

            </div>
          </div>

          {/* Home indicator */}
          <div style={{ position: 'absolute', bottom: 4, left: '50%', transform: 'translateX(-50%)', width: 48, height: 3, borderRadius: 10, background: 'rgba(0,0,0,0.2)' }} />
        </div>

      </section>
    </main>
  )
}

type RajuDayProps = {
  welcomeName?: string | null
  onBackToDashboard: () => void
}

type DayMessage = {
  from: 'user' | 'bot' | 'alert'
  text: string
  time?: string
  alertId?: string
  event_confidence_score?: number  // 0-100 from Lambda
}

// Start with empty chat so it looks real; no prefilled questions or demo alerts.
// Real alerts from Lambda will appear when they're sent (poll). User types anything and the bot replies.
const INITIAL_LIVE_MESSAGES: DayMessage[] = []

function RajuDay({ welcomeName, onBackToDashboard: _onBackToDashboard }: RajuDayProps) {
  const liveClock = useLiveClock()
  const displayName = formatWelcomeName(welcomeName)
  const retailerKey = (welcomeName || '').toString().trim().toLowerCase() || 'raju'
  const [welcome, setWelcome] = useState<{ main: string; sub: string } | null>(() =>
    displayName ? getWelcomeMessage(displayName, false) : null
  )
  useEffect(() => {
    if (displayName && !welcome) setWelcome(getWelcomeMessage(displayName, false))
  }, [displayName, welcome])

  const agentApiBase = (import.meta as any).env?.VITE_AGENT_API_BASE || 'http://localhost:8000'
  const [messages, setMessages] = useState<DayMessage[]>(INITIAL_LIVE_MESSAGES)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const seenAlertIdsRef = useRef<Set<string>>(new Set())

  // Restore chat history for this retailer from sessionStorage so messages
  // are not lost when navigating between Dashboard and Live Alerts.
  useEffect(() => {
    if (typeof window === 'undefined') return
    const key = `ai_sahayak_live_messages_${retailerKey}`
    try {
      const raw = window.sessionStorage.getItem(key)
      if (raw) {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) {
          setMessages(parsed)
        }
      }
    } catch {
      // ignore malformed cache
    }
  }, [retailerKey])

  // Persist messages whenever they change so the history survives view switches.
  useEffect(() => {
    if (typeof window === 'undefined') return
    const key = `ai_sahayak_live_messages_${retailerKey}`
    try {
      window.sessionStorage.setItem(key, JSON.stringify(messages))
    } catch {
      // ignore quota errors
    }
  }, [messages, retailerKey])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Poll backend for Lambda-sent alerts (Step 4: deliver into WP UI)
  useEffect(() => {
    const userId = retailerKey
    const fetchAlerts = async () => {
      try {
        const res = await fetch(`${agentApiBase}/v1/alerts/for-user?user_id=${encodeURIComponent(userId)}`)
        if (!res.ok) return
        const data = await res.json()
        const alerts = data.alerts || []
        if (alerts.length === 0) return
        setMessages((prev) => {
          const seen = seenAlertIdsRef.current
          const toAdd: DayMessage[] = []
          for (const a of alerts) {
            if (a.id && !seen.has(a.id)) {
              seen.add(a.id)
              const timeStr = a.time ? new Date(a.time).toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true }) : ''
              toAdd.push({ from: 'alert', text: a.text, time: timeStr, alertId: a.id, event_confidence_score: a.event_confidence_score })
            }
          }
          if (toAdd.length === 0) return prev
          return [...prev, ...toAdd]
        })
      } catch {
        // ignore
      }
    }
    fetchAlerts()
    const t = setInterval(fetchAlerts, 30000)
    return () => clearInterval(t)
  }, [agentApiBase, retailerKey])

  async function sendMessage(overrideText?: string) {
    const text = (overrideText ?? input.trim()).trim()
    if (!text || sending) return
    if (!overrideText) setInput('')
    setMessages((prev) => [...prev, { from: 'user', text }])
    setSending(true)
    try {
      const response = await fetch(`${agentApiBase}/v1/webhook/incoming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: retailerKey,
          text,
          platform: 'web',
          session_id: `day-session-${retailerKey}`,
        }),
      })
      if (!response.ok) throw new Error('Bot unavailable')
      const data = await response.json()
      const reply = data.reply || data.message || 'No reply from bot.'
      setMessages((prev) => [...prev, { from: 'bot', text: reply }])
    } catch {
      setMessages((prev) => [...prev, { from: 'bot', text: 'Bot is unavailable right now. Please try again.' }])
    } finally {
      setSending(false)
    }
  }

  return (
    <main style={{ display: 'flex', flexDirection: 'row', height: 'calc(100vh - 4.5rem)', overflow: 'hidden', position: 'relative', zIndex: 10 }}>

      {/* ══════════════ LEFT: Timeline — Bharat light theme ══════════════ */}
      <section className="border-r border-slate-200" style={{ width: '52%', display: 'flex', flexDirection: 'column', overflow: 'hidden', flexShrink: 0 }}>

        <div className="border-b border-slate-200 bg-white/80 backdrop-blur-sm" style={{ padding: '1rem 1.75rem 0.75rem', flexShrink: 0 }}>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#0f172a', lineHeight: 1.0, letterSpacing: '-0.02em', margin: 0 }}>
            Raju's day —{' '}
            <span style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>powered by AI</span>
          </h2>
          <p className="text-slate-600" style={{ fontSize: '0.75rem', marginTop: 4 }}>EventBridge at a time you set · SageMaker forecasts · Bedrock explains in Hinglish</p>
        </div>

        {/* Scrollable timeline */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '0.75rem 1.75rem 1rem', scrollbarWidth: 'none' }}>

          {/* TODAY'S STATS STRIP */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginBottom: 14 }}>
            {[
              { label: 'Today\'s Sales', value: '₹15,200', delta: '+12%', color: '#34d399' },
              { label: 'Items Low Stock', value: '3 items', delta: 'reorder now', color: '#f87171' },
              { label: 'Festival Alert', value: 'Holi', delta: '4 din baad', color: '#fbbf24' },
              { label: 'AI Confidence', value: '92%', delta: 'demand spike', color: '#818cf8' },
            ].map(s => (
              <div key={s.label} style={{ background: `${s.color}08`, border: `1px solid ${s.color}20`, borderRadius: 10, padding: '8px 10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 3 }}>
                  <span style={{ fontSize: '0.55rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{s.label}</span>
                </div>
                <p style={{ fontSize: '0.95rem', fontWeight: 900, color: s.color, lineHeight: 1 }}>{s.value}</p>
                <p style={{ fontSize: '0.55rem', color: '#64748b', marginTop: 2 }}>{s.delta}</p>
              </div>
            ))}
          </div>

          {/* TIMELINE HEADING */}
          <p style={{ fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', color: '#475569', marginBottom: 10 }}>
            Today's Flow — How Raju uses AI Sahayak
          </p>

          {/* TIMELINE EVENTS */}
          {([
            {
              time: '8:59 AM',
              icon: 'E',
              iconBg: '#0891b2',
              title: 'EventBridge triggers',
              sub: 'AWS EventBridge runs daily at the time you chose in chat',
              badge: 'EventBridge',
              badgeColor: '#38bdf8',
              detail: 'Scheduled rule checks FESTIVAL_CALENDAR + sales data from DynamoDB',
              alert: null,
            },
            {
              time: '9:00 AM',
              icon: 'F',
              iconBg: '#d97706',
              title: 'Festival Alert — Holi in 4 days!',
              sub: 'SageMaker predicts 3.2x demand spike for color, ghee, sweets',
              badge: 'SageMaker',
              badgeColor: '#a78bfa',
              detail: null,
              alert: 'Holi 4 din baad! Gulal, Ghee aur Shakkar ka stock check karo. SageMaker confidence: 92%',
            },
            {
              time: '9:01 AM',
              icon: 'S',
              iconBg: '#059669',
              title: 'Daily Sales Summary',
              sub: 'Bedrock summarizes yesterday\'s performance in Hinglish',
              badge: 'Bedrock LLM',
              badgeColor: '#34d399',
              detail: null,
              alert: 'Kal ki sales: ₹15,200 (12% zyada!) Top item: Amul Ghee 500g. Low stock: Tata Salt, Parle-G, Ariel.',
            },
            {
              time: '9:05 AM',
              icon: 'W',
              iconBg: '#db2777',
              title: 'Wedding Season Nudge',
              sub: 'Location-based alert: 3 weddings this week near Rajwada',
              badge: 'Google Maps API',
              badgeColor: '#f472b6',
              detail: null,
              alert: 'Wedding season Indore mein! Dry fruits, Mithai, Gifting items ka stock ready karo. 3 shaadiyaan is hafte.',
            },
            {
              time: '10:30 AM',
              icon: 'C',
              iconBg: '#7c3aed',
              title: 'Raju asks the AI',
              sub: 'Raju types: "Gulal kitna mangwau?" — AI replies with forecast',
              badge: 'Bedrock Chat',
              badgeColor: '#818cf8',
              detail: '"Raju Bhai, 25-30 kg gulal lo. Last Holi mein 22 kg bika tha, is baar 3.2x spike expected hai!"',
              alert: null,
            },
            {
              time: '12:00 PM',
              icon: 'R',
              iconBg: '#ea580c',
              title: 'Reorder Triggered',
              sub: 'Raju confirms reorder — Lambda updates DynamoDB inventory',
              badge: 'Lambda + DynamoDB',
              badgeColor: '#fbbf24',
              detail: 'Tata Salt (50 pkt), Parle-G (10 box), Ariel (20 kg) — order placed via WhatsApp',
              alert: null,
            },
            {
              time: '6:00 PM',
              icon: 'P',
              iconBg: '#0f766e',
              title: 'Evening Check-in',
              sub: 'Raju asks: "Aaj kitna hua?" — AI gives live P&L summary',
              badge: 'Bedrock',
              badgeColor: '#34d399',
              detail: '"₹15,200 aaj. Profit ~₹2,800 (18.4%). Kal Holi preps ka expect karo 2x traffic!"',
              alert: null,
            },
          ] as Array<{time:string;icon:string;iconBg:string;title:string;sub:string;badge:string;badgeColor:string;detail:string|null;alert:string|null}>).map((ev, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, marginBottom: 14, position: 'relative' }}>
              {/* Vertical line */}
              {i < 6 && <div className="bg-slate-200" style={{ position: 'absolute', left: 14, top: 30, width: 2, height: 'calc(100% + 2px)' }} />}
              {/* Icon */}
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: ev.iconBg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', flexShrink: 0, zIndex: 1, boxShadow: `0 0 10px ${ev.iconBg}50` }}>{ev.icon}</div>
              {/* Content */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, flexWrap: 'wrap', marginBottom: 2 }}>
                  <span style={{ fontSize: '0.58rem', color: '#475569', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{ev.time}</span>
                  <span className="text-slate-800" style={{ fontSize: '0.75rem', fontWeight: 700 }}>{ev.title}</span>
                  <span style={{ fontSize: '0.55rem', fontWeight: 700, color: ev.badgeColor, background: `${ev.badgeColor}15`, border: `1px solid ${ev.badgeColor}30`, borderRadius: 20, padding: '1px 7px' }}>{ev.badge}</span>
                </div>
                <p style={{ fontSize: '0.67rem', color: '#64748b', lineHeight: 1.35, marginBottom: ev.alert || ev.detail ? 5 : 0 }}>{ev.sub}</p>
                {ev.alert && (
                  <div style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)', borderRadius: 8, padding: '6px 10px', fontSize: '0.7rem', color: '#fde68a', lineHeight: 1.4 }}>
                    <em>{ev.alert}</em>
                  </div>
                )}
                {ev.detail && (
                  <div style={{ background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.15)', borderRadius: 8, padding: '6px 10px', fontSize: '0.68rem', color: '#c7d2fe', lineHeight: 1.4 }}>
                    {ev.detail}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* AWS FLOW DIAGRAM */}
          <div className="bg-white/80 border border-slate-200" style={{ marginTop: 4, borderRadius: 12, padding: '10px 12px' }}>
            <p style={{ fontSize: '0.58rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#475569', marginBottom: 8 }}>AWS proactive flow</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
              {[
                { label: 'EventBridge', color: '#38bdf8', icon: 'EB' },
                { label: '→', color: '#334155', icon: '' },
                { label: 'Lambda', color: '#34d399', icon: 'λ' },
                { label: '→', color: '#334155', icon: '' },
                { label: 'SageMaker', color: '#a78bfa', icon: 'SM' },
                { label: '→', color: '#334155', icon: '' },
                { label: 'Bedrock', color: '#fbbf24', icon: 'B' },
                { label: '→', color: '#334155', icon: '' },
                { label: 'WhatsApp', color: '#34d399', icon: 'WA' },
              ].map((s, i) => (
                s.label === '→'
                  ? <span key={i} style={{ color: '#334155', fontSize: '0.7rem' }}>→</span>
                  : <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 3, fontSize: '0.62rem', fontWeight: 700, color: s.color, background: `${s.color}10`, border: `1px solid ${s.color}25`, borderRadius: 20, padding: '2px 8px' }}>{s.icon} {s.label}</span>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* ══════════════ RIGHT: Live WhatsApp Feed — Bharat theme shows through ══════════════ */}
      <section style={{ flex: '1 1 0%', display: 'grid', placeItems: 'center', overflow: 'hidden', position: 'relative', zIndex: 10 }}>

        {/* Glow */}
        <div style={{ pointerEvents: 'none', position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 70% 70% at 55% 50%, rgba(251,191,36,0.05) 0%, transparent 65%)' }} />

        {/* Phone */}
        <div style={{ position: 'relative', width: 'min(290px, 36vw)', height: 'min(560px, calc(100vh - 4.5rem - 1rem))', flexShrink: 0, zIndex: 20 }}>
          {/* Side buttons */}
          <div style={{ position: 'absolute', left: -4, top: '18%', width: 3, height: 32, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', left: -4, top: '26%', width: 3, height: 22, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', right: -4, top: '22%', width: 3, height: 44, background: '#334155', borderRadius: '0 2px 2px 0' }} />

          {/* Shell */}
          <div style={{ borderRadius: '2.4rem', border: '6px solid #1a1a1a', background: '#fff', overflow: 'hidden', isolation: 'isolate', zIndex: 20, height: '100%', display: 'flex', flexDirection: 'column', boxShadow: '0 0 0 1px rgba(0,0,0,0.15), 0 32px 64px -8px rgba(0,0,0,0.85), 0 0 40px -8px rgba(251,191,36,0.12), inset 0 1px 0 rgba(255,255,255,0.3)' }}>

            {/* Dynamic island */}
            <div style={{ position: 'absolute', zIndex: 30, top: 8, left: '50%', transform: 'translateX(-50%)', width: 66, height: 18, borderRadius: 18, background: '#000' }} />

            {/* Status bar — live IST, same as Onboarding */}
            <div style={{ background: '#075e54', padding: '10px 18px 4px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
              <span style={{ color: '#fff', fontSize: '0.62rem', fontWeight: 700 }}>{formatISTStatusTime(liveClock)}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ display: 'flex', alignItems: 'flex-end', gap: '2px' }}>
                  {[3,5,7,9].map(h => <span key={h} style={{ width: 2, height: h, background: '#fff', borderRadius: 1 }} />)}
                </span>
                <svg style={{ width: 10, height: 10, color: '#fff' }} fill="currentColor" viewBox="0 0 24 24"><path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3a4.237 4.237 0 00-6 0zm-4-4l2 2a7.074 7.074 0 0110 0l2-2C15.14 9.14 8.87 9.14 5 13z"/></svg>
                <span style={{ display: 'inline-flex', border: '1.5px solid rgba(255,255,255,0.7)', borderRadius: 3, padding: '1px 2px' }}>
                  <span style={{ width: 12, height: 5, background: '#4ade80', borderRadius: 1 }} />
                </span>
              </div>
            </div>

            {/* App bar */}
            <div style={{ background: '#075e54', padding: '5px 10px 9px', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
              <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer' }} aria-label="Back">
                <svg style={{ width: 16, height: 16 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" /></svg>
              </button>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#128c7e', border: '2px solid rgba(255,255,255,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 800, color: '#fff', flexShrink: 0 }}>AI</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: '0.88rem', fontWeight: 700, color: '#fff', lineHeight: 1.1 }}>AI Sahayak</p>
              </div>
              <div style={{ display: 'flex', gap: 2 }}>
                <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 4 }} aria-label="Video">
                  <svg style={{ width: 15, height: 15 }} fill="currentColor" viewBox="0 0 24 24"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>
                </button>
                <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 4 }} aria-label="Call">
                  <svg style={{ width: 15, height: 15 }} fill="currentColor" viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
                </button>
              </div>
            </div>

            {/* Chat */}
            <div style={{ flex: 1, overflowY: 'auto', background: '#efeae2', backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")", padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 6 }}>

              {/* Date pill — same format as Onboarding */}
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 2 }}>
                <span style={{ fontSize: '0.55rem', color: '#667781', background: '#d4d0c8', padding: '2px 10px', borderRadius: 8, fontWeight: 500 }}>TODAY · {getTodayDatePill()}</span>
              </div>

              {messages.map((msg, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: msg.from === 'user' ? 'flex-end' : 'flex-start' }}>
                  {/* Alert messages — full-width amber banner */}
                  {msg.from === 'alert' ? (
                    <div style={{ width: '94%', background: '#fff9e6', border: '1px solid #fcd34d', borderRadius: 10, padding: '7px 10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 3 }}>
                        <span style={{ fontSize: '0.55rem', fontWeight: 700, color: '#92400e', background: '#fde68a', borderRadius: 20, padding: '1px 7px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>AI Alert</span>
                        <span style={{ fontSize: '0.5rem', color: '#92400e', opacity: 0.7 }}>{msg.time}</span>
                        {msg.event_confidence_score != null && (
                          <span style={{ fontSize: '0.5rem', fontWeight: 700, color: '#b45309', marginLeft: 'auto' }}>{msg.event_confidence_score}% confidence</span>
                        )}
                      </div>
                      <p style={{ fontSize: '0.72rem', color: '#111b21', lineHeight: 1.4, whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                    </div>
                  ) : (
                    <div style={{ maxWidth: '86%', borderRadius: msg.from === 'user' ? '8px 8px 2px 8px' : '8px 8px 8px 2px', padding: '6px 9px 4px', background: msg.from === 'user' ? '#d9fdd3' : '#ffffff', color: '#111b21', fontSize: '0.73rem', lineHeight: 1.42, wordBreak: 'break-word' as const, boxShadow: '0 1px 2px rgba(0,0,0,0.12)' }}>
                      <span style={{ display: 'block', whiteSpace: 'pre-wrap' }}>{msg.text}</span>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 3, marginTop: 3 }}>
                        <span style={{ fontSize: '0.5rem', color: '#667781' }}>{msg.time ?? formatISTTime(new Date())}</span>
                        {msg.from === 'user' && <svg style={{ width: 12, height: 12, color: '#53bdeb' }} fill="currentColor" viewBox="0 0 24 24"><path d="M18 7l-1.41-1.41-6.34 6.34 1.41 1.41L18 7zm4.24-1.41L11.66 16.17 7.48 12l-1.41 1.41L11.66 19l12-12-1.42-1.41zM.41 13.41L6 19l1.41-1.41L1.83 12 .41 13.41z"/></svg>}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {sending && (
                <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div style={{ background: '#fff', borderRadius: '8px 8px 8px 2px', padding: '8px 14px', display: 'flex', gap: 4, alignItems: 'center', boxShadow: '0 1px 2px rgba(0,0,0,0.12)' }}>
                    {[0,150,300].map(d => <span key={d} className="rounded-full animate-bounce" style={{ width: 5, height: 5, background: '#8696a0', animationDelay: `${d}ms`, display: 'inline-block' }} />)}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input bar */}
            <div style={{ background: '#f0f2f5', borderTop: '1px solid #e9edef', padding: '7px 8px', flexShrink: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
              <button type="button" style={{ color: '#8696a0', background: 'none', border: 'none', cursor: 'pointer', padding: 2 }} aria-label="Emoji">
                <svg style={{ width: 20, height: 20 }} fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/></svg>
              </button>
              <div style={{ flex: 1, background: '#fff', borderRadius: 22, padding: '5px 12px', display: 'flex', alignItems: 'center', boxShadow: '0 1px 2px rgba(0,0,0,0.08)' }}>
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendMessage(undefined)}
                  disabled={sending}
                  style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', fontSize: '0.73rem', color: '#111b21' }}
                />
              </div>
              <button type="button" onClick={() => sendMessage(undefined)} disabled={sending || !input.trim()} aria-label="Send"
                style={{ width: 36, height: 36, borderRadius: '50%', background: '#128c7e', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: input.trim() ? 'pointer' : 'default', flexShrink: 0, boxShadow: '0 2px 8px rgba(18,140,126,0.5)', opacity: sending || !input.trim() ? 0.5 : 1 }}>
                {sending
                  ? <span style={{ fontSize: '0.65rem' }}>…</span>
                  : <svg style={{ width: 16, height: 16 }} fill="currentColor" viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
                }
              </button>
            </div>

          </div>

          {/* Home indicator */}
          <div style={{ position: 'absolute', bottom: 4, left: '50%', transform: 'translateX(-50%)', width: 48, height: 3, borderRadius: 10, background: 'rgba(0,0,0,0.18)' }} />
        </div>

      </section>
    </main>
  )
}

export default App
