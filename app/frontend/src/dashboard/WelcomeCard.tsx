import type { WelcomeCardProps } from './types'

export function WelcomeCard({ main, onContinue, onLogout }: WelcomeCardProps) {
  return (
    <div className="flex flex-1 items-center justify-center" style={{ paddingTop: '4rem', minHeight: 'calc(100vh - 4rem)' }}>
      <div className="w-full max-w-sm rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-xl">
        <p className="text-center text-lg font-semibold text-slate-900">{main}</p>
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
