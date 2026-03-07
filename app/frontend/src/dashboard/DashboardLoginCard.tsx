import { useState } from 'react'
import { signIn } from 'aws-amplify/auth'
import { isCognitoConfigured } from '../cognitoConfig'
import type { DashboardLoginCardProps } from './types'

async function doSignIn(id: string, pwd: string) {
  try {
    await signIn({ username: id, password: pwd })
  } catch (firstErr: unknown) {
    const msg =
      firstErr && typeof firstErr === 'object' && 'message' in firstErr
        ? String((firstErr as { message: unknown }).message)
        : ''
    if (
      msg &&
      (msg.includes('Incorrect') || msg.includes('authFlowType') || msg.includes('not enabled'))
    ) {
      await signIn({
        username: id,
        password: pwd,
        options: { authFlowType: 'USER_PASSWORD_AUTH' },
      })
    } else {
      throw firstErr
    }
  }
}

export function DashboardLoginCard({ title, subtitle, onSuccess, demoUsers }: DashboardLoginCardProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    const id = username.trim()
    const pwd = password.trim()
    if (!id || !pwd) {
      setError('Enter your ID and password.')
      return
    }
    if (!isCognitoConfigured) {
      setError('Cognito is not configured. Add VITE_COGNITO_* to .env.')
      return
    }
    setLoading(true)
    try {
      await doSignIn(id, pwd)
      onSuccess(id)
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: unknown }).message)
          : 'Sign-in failed.'
      setError(
        message.includes('Incorrect')
          ? 'Incorrect User ID or password. Use the exact ID and Password from your onboarding chat (e.g. 9004755498 / Raju_5498!).'
          : message
      )
    } finally {
      setLoading(false)
    }
  }

  async function handleQuickLogin(user: { username: string; password: string; name: string }) {
    setError('')
    if (!isCognitoConfigured) {
      setError('Cognito is not configured.')
      return
    }
    setLoading(true)
    try {
      await doSignIn(user.username, user.password)
      onSuccess(user.username, user.name)
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: unknown }).message)
          : 'Sign-in failed.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex flex-1 items-center justify-center min-h-[60vh]">
      {demoUsers && demoUsers.length > 0 && (
        <div className="absolute top-0 right-0 w-[280px] -mr-4 md:-mr-8 lg:-mr-14 rounded-2xl border-2 border-emerald-200 bg-white p-4 shadow-xl">
          <div className="mb-3 pb-2 border-b border-emerald-200">
            <p className="text-xs font-bold uppercase tracking-widest text-emerald-600">For judges</p>
            <p className="text-[0.65rem] text-slate-600 mt-1">Click to log in — no onboarding.</p>
          </div>
          <ul className="space-y-2">
            {demoUsers.map((u) => (
              <li
                key={u.username}
                className="rounded-xl border-2 border-slate-200 bg-slate-50 p-2.5 hover:border-emerald-300 hover:bg-emerald-50/50 transition-all duration-200"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-slate-900">{u.name}</p>
                    <p className="text-[0.65rem] text-slate-500 mt-0.5">{u.shopCategory}</p>
                    <p className="mt-1.5 text-[0.65rem] text-slate-600 font-mono leading-snug break-all">
                      {u.username}<br />
                      <span className="text-slate-500">{u.password}</span>
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleQuickLogin(u)}
                    disabled={loading}
                    className="shrink-0 rounded-lg bg-emerald-500 px-2.5 py-1.5 text-[0.65rem] font-bold text-white shadow-md hover:bg-emerald-600 disabled:opacity-50 transition-all"
                  >
                    Login
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="w-full max-w-sm rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-xl">
        <p className="text-center text-sm font-semibold text-slate-900">{title}</p>
        <p className="mt-2 text-center text-xs text-slate-600">{subtitle}</p>
        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <input
            type="text"
            placeholder="User ID"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-lg border-2 border-slate-200 bg-slate-50 px-3 py-3 text-base text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
            autoComplete="username"
            disabled={loading}
          />
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border-2 border-slate-200 bg-slate-50 pl-3 pr-10 py-3 text-base text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              autoComplete="current-password"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showPassword ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
              )}
            </button>
          </div>
          {error && <p className="text-center text-xs text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-emerald-500 px-4 py-2.5 text-sm font-bold text-white shadow-lg hover:bg-emerald-600 disabled:opacity-60"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
