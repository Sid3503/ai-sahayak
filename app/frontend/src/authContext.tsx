import { createContext, useContext, type ReactNode } from 'react'

// Minimal auth shape so App doesn't depend on OIDC loading. Real sign-in is via Amplify + dashboardLoggedIn.
const fallbackAuth = { isAuthenticated: false }
const AuthContext = createContext(fallbackAuth)

export function SimpleAuthProvider({ children }: { children: ReactNode }) {
  return (
    <AuthContext.Provider value={fallbackAuth}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
