import { useState } from 'react'
import type { WelcomeCardProps } from './types'

export function WelcomeCard({ main, onContinue, onLanguageChoice, onLogout }: WelcomeCardProps) {
  const [pageLang, setPageLang] = useState<'en' | 'hi' | null>(null)

  const handleLang = (lang: 'en' | 'hi') => {
    setPageLang(lang)
    onLanguageChoice?.(lang)
  }

  return (
    <div className="flex flex-1 items-center justify-center">
      <div className="w-full max-w-sm rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-xl">
        <p className="text-center text-lg font-semibold text-slate-900">{main}</p>
        <p className="mt-3 text-center text-sm text-slate-600">View this page in:</p>
        <div className="mt-2 flex justify-center gap-3">
          <button
            type="button"
            onClick={() => handleLang('en')}
            className={`rounded-full px-5 py-2.5 text-sm font-semibold transition-all ${
              pageLang === 'en'
                ? 'bg-emerald-500 text-white shadow-lg hover:bg-emerald-600'
                : 'border-2 border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
            }`}
          >
            English
          </button>
          <button
            type="button"
            onClick={() => handleLang('hi')}
            className={`rounded-full px-5 py-2.5 text-sm font-semibold transition-all ${
              pageLang === 'hi'
                ? 'bg-emerald-500 text-white shadow-lg hover:bg-emerald-600'
                : 'border-2 border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
            }`}
          >
            हिंदी
          </button>
        </div>
        {pageLang && (
          <p className="mt-3 text-center text-sm text-slate-500">
            {pageLang === 'en' ? 'Viewing in English.' : 'Page ab Hindi mein dikhegi.'}
          </p>
        )}
        <button
          type="button"
          onClick={onContinue}
          className="mt-5 w-full rounded-full bg-emerald-500 px-4 py-2.5 text-sm font-bold text-white shadow-lg hover:bg-emerald-600"
        >
          Continue to dashboard
        </button>
        {onLogout && (
          <button
            type="button"
            onClick={onLogout}
            className="mt-3 w-full text-center text-xs font-medium text-slate-500 hover:text-rose-600 transition-colors"
          >
            Not you? Log out
          </button>
        )}
      </div>
    </div>
  )
}
