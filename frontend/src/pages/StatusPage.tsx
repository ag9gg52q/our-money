import { useEffect, useState } from 'react'
import { fetchHealth } from '../api/health'

type ApiState = 'loading' | 'ok' | 'error'

export default function StatusPage() {
  const [apiState, setApiState] = useState<ApiState>('loading')

  useEffect(() => {
    let ignore = false

    fetchHealth()
      .then(() => {
        if (!ignore) setApiState('ok')
      })
      .catch(() => {
        if (!ignore) setApiState('error')
      })

    return () => {
      ignore = true
    }
  }, [])

  return (
    <>
      <h1>Status</h1>
      {apiState === 'loading' && <p>Se verifică legătura cu serverul...</p>}
      {apiState === 'ok' && <p>✅ API-ul funcționează.</p>}
      {apiState === 'error' && (
        <p>❌ API-ul nu răspunde. Backend-ul e pornit?</p>
      )}
    </>
  )
}
