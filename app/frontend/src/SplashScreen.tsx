/**
 * Popup card shown when someone opens the site (once per session).
 * Centered card: logo + "What our logo means" for Bharat. Dismissible via Continue.
 */
import { useEffect, useState } from 'react'

// Bump key so updated splash shows even for people who saw the older version once
const SPLASH_STORAGE_KEY = 'ai_sahayak_splash_seen_v2'

export function SplashScreen({ onDismiss }: { onDismiss: () => void }) {
  const [ready, setReady] = useState(false)
  const [minShowDone, setMinShowDone] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setMinShowDone(true), 1200)
    return () => clearTimeout(t)
  }, [])

  useEffect(() => {
    const t = setTimeout(() => setReady(true), 100)
    return () => clearTimeout(t)
  }, [])

  const handleContinue = () => {
    if (typeof window !== 'undefined') {
      try {
        sessionStorage.setItem(SPLASH_STORAGE_KEY, '1')
      } catch {
        /* ignore */
      }
    }
    onDismiss()
  }

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center p-4"
      style={{
        background: 'linear-gradient(165deg, #0d2818 0%, #071207 40%, #14532d 100%)',
        minHeight: '100dvh',
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="splash-title"
      aria-describedby="splash-desc"
    >
      {/* Solid gradient so main site is never visible behind */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background: 'linear-gradient(165deg, #0d2818 0%, #071207 40%, #14532d 100%)',
          opacity: 0.98,
        }}
      />

      {/* Centered card — pop in + glow (keyframes start at opacity 0, no extra opacity-0 class) */}
      <div
        className={`relative w-full max-w-lg rounded-3xl border-2 border-emerald-500/50 bg-white/95 backdrop-blur-2xl p-6 sm:p-8 md:p-10 ${
          ready ? 'splash-pop-in splash-card-glow splash-stagger-0' : 'opacity-0 scale-95 translate-y-4'
        }`}
        style={{
          boxShadow: ready ? undefined : '0 25px 50px -12px rgba(0,0,0,0.25)',
        }}
      >
        {/* Tricolor accent strip on card */}
        <div className="absolute top-0 left-0 right-0 flex h-1 rounded-t-3xl overflow-hidden">
          <div className="flex-1 bg-[#f59e0b]" />
          <div className="flex-1 bg-white border-x border-slate-200" />
          <div className="flex-1 bg-[#16a34a]" />
        </div>

        <div className="flex flex-col items-center pt-2">
          <h1
            id="splash-title"
            className={`text-center text-lg font-bold tracking-tight text-slate-900 sm:text-xl ${ready ? 'splash-pop-in splash-stagger-1' : ''}`}
          >
            What our logo means — for Bharat
          </h1>

          {/* Logo — pop + glow ring */}
          <div
            className={`mt-4 flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-2xl border-2 border-emerald-500/70 bg-white sm:h-28 sm:w-28 ${
              ready ? 'splash-pop-in splash-stagger-2 splash-logo-glow' : ''
            }`}
          >
            <img
              src="/Generated_image.png"
              alt="AI Sahayak logo"
              className="h-full w-full object-contain"
            />
          </div>

          {/* Content cards — staggered pop */}
          <div id="splash-desc" className="mt-5 w-full space-y-3 text-left">
            <div
              className={`rounded-xl border-l-4 border-emerald-500 bg-emerald-50/90 px-4 py-3 transition-transform duration-300 hover:scale-[1.02] hover:shadow-md ${
                ready ? 'splash-pop-in splash-stagger-3' : ''
              }`}
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">Green</p>
              <p className="mt-0.5 text-sm leading-relaxed text-slate-700">
                Growth and trust — the backbone of India&apos;s 12M+ MSME stores.
              </p>
            </div>
            <div
              className={`rounded-xl border-l-4 border-amber-500 bg-amber-50/90 px-4 py-3 transition-transform duration-300 hover:scale-[1.02] hover:shadow-md ${
                ready ? 'splash-pop-in splash-stagger-4' : ''
              }`}
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-800">Amber / Saffron</p>
              <p className="mt-0.5 text-sm leading-relaxed text-slate-700">
                Warmth and tradition. The mark is a <strong className="text-slate-900">helping hand</strong> — <em>Sahayak</em> — for every shopkeeper.
              </p>
            </div>
            <div
              className={`rounded-xl border-l-4 border-slate-400 bg-slate-50/95 px-4 py-3 transition-transform duration-300 hover:scale-[1.02] hover:shadow-md ${
                ready ? 'splash-pop-in splash-stagger-5' : ''
              }`}
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-600">Our promise</p>
              <p className="mt-0.5 text-sm leading-relaxed text-slate-700">
                We&apos;re your quiet co-pilot: we surface the right insight at the right time — before the festival, before the rush.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleContinue}
            disabled={!minShowDone}
            className={`mt-6 inline-flex items-center justify-center rounded-full bg-emerald-500 px-8 py-3.5 text-sm font-bold text-white transition-all duration-300 ease-out ${
              ready ? 'splash-pop-in splash-stagger-6' : ''
            } ${
              minShowDone
                ? 'splash-btn-glow cursor-pointer hover:bg-emerald-600 hover:shadow-[0_0_40px_-5px_rgba(34,197,94,0.6)] hover:scale-[1.06] active:scale-[0.98]'
                : 'opacity-60 cursor-not-allowed'
            }`}
          >
            {minShowDone ? 'Continue' : 'Loading…'}
          </button>
        </div>

        <p
          className={`mt-4 text-center text-[0.65rem] font-semibold uppercase tracking-widest text-slate-500 ${
            ready ? 'splash-pop-in splash-stagger-7' : ''
          }`}
        >
          AI Sahayak — AWS AI for Bharat Hackathon
        </p>
      </div>
    </div>
  )
}

export function wasSplashAlreadySeen(): boolean {
  if (typeof window === 'undefined') return true
  try {
    return sessionStorage.getItem(SPLASH_STORAGE_KEY) === '1'
  } catch {
    return false
  }
}
