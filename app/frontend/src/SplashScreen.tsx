/**
 * Popup card shown when someone opens the site (once per session).
 * Centered card: logo + "What our logo means" for Bharat. Dismissible via Continue.
 */
import { useEffect, useState } from 'react'

const SPLASH_STORAGE_KEY = 'ai_sahayak_splash_seen'

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
      role="dialog"
      aria-modal="true"
      aria-labelledby="splash-title"
      aria-describedby="splash-desc"
    >
      {/* Dimmed overlay — page visible behind */}
      <button
        type="button"
        onClick={handleContinue}
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"
        aria-label="Close"
      />

      {/* Centered card */}
      <div
        className={`relative w-full max-w-lg rounded-3xl border-2 border-emerald-500/30 bg-white p-6 shadow-2xl transition-all duration-300 sm:p-8 md:p-10 ${
          ready ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
        }`}
        style={{ boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25), 0 0 0 1px rgba(34,197,94,0.1)' }}
      >
        {/* Tricolor accent strip on card */}
        <div className="absolute top-0 left-0 right-0 flex h-1 rounded-t-3xl overflow-hidden">
          <div className="flex-1 bg-[#f59e0b]" />
          <div className="flex-1 bg-white border-x border-slate-200" />
          <div className="flex-1 bg-[#16a34a]" />
        </div>

        <div className="flex flex-col items-center pt-2">
          <h1 id="splash-title" className="text-center text-lg font-bold tracking-tight text-slate-900 sm:text-xl">
            What our logo means — for Bharat
          </h1>

          {/* Logo */}
          <div className="mt-4 flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-2xl border-2 border-emerald-500/50 bg-white shadow-md sm:h-28 sm:w-28">
            <img
              src="/Generated_image.png"
              alt="AI Sahayak logo"
              className="h-full w-full object-contain"
            />
          </div>

          {/* Content cards — easy to read */}
          <div id="splash-desc" className="mt-5 w-full space-y-3 text-left">
            <div className="rounded-xl border-l-4 border-emerald-500 bg-emerald-50/80 px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">Green</p>
              <p className="mt-0.5 text-sm leading-relaxed text-slate-700">
                Growth and trust — the backbone of India&apos;s 12M+ kirana stores.
              </p>
            </div>
            <div className="rounded-xl border-l-4 border-amber-500 bg-amber-50/80 px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-800">Amber / Saffron</p>
              <p className="mt-0.5 text-sm leading-relaxed text-slate-700">
                Warmth and tradition. The mark is a <strong className="text-slate-900">helping hand</strong> — <em>Sahayak</em> — for every shopkeeper.
              </p>
            </div>
            <div className="rounded-xl border-l-4 border-slate-400 bg-slate-50 px-4 py-3">
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
            className={`mt-6 rounded-full bg-emerald-500 px-8 py-3.5 text-sm font-bold text-white shadow-lg transition-all ${
              minShowDone ? 'opacity-100 cursor-pointer hover:bg-emerald-600 hover:scale-[1.02] active:scale-[0.98]' : 'opacity-60 cursor-not-allowed'
            }`}
          >
            {minShowDone ? 'Continue' : 'Loading…'}
          </button>
        </div>

        <p className="mt-4 text-center text-[0.65rem] font-semibold uppercase tracking-widest text-slate-500">
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
