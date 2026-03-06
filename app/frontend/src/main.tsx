import { StrictMode, Component, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { Amplify } from 'aws-amplify'
import { cognitoConfig, isCognitoConfigured } from './cognitoConfig'
import { SimpleAuthProvider } from './authContext'

if (isCognitoConfigured && cognitoConfig.userPoolId && cognitoConfig.userPoolWebClientId) {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: cognitoConfig.userPoolId,
        userPoolClientId: cognitoConfig.userPoolWebClientId,
      },
    },
  })
}

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }
  static getDerivedStateFromError(error: Error) {
    return { error }
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 560 }}>
          <h1 style={{ color: '#b91c1c' }}>Something went wrong</h1>
          <pre style={{ background: '#fef2f2', padding: 12, overflow: 'auto' }}>
            {this.state.error.message}
          </pre>
          <p style={{ color: '#666' }}>Check the browser console for more details.</p>
        </div>
      )
    }
    return this.props.children
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <SimpleAuthProvider>
        <App />
      </SimpleAuthProvider>
    </ErrorBoundary>
  </StrictMode>,
)
