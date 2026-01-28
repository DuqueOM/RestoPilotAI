/**
 * Custom hooks for API interactions
 */

import { useCallback, useState } from 'react'
import { api } from '@/lib/api'
import type { ApiError, SessionData } from '@/lib/types'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
}

/**
 * Hook for loading demo session
 */
export function useDemo() {
  const [state, setState] = useState<UseApiState<SessionData>>({
    data: null,
    loading: false,
    error: null,
  })

  const loadDemo = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await api.getDemoSession()
      setState({ data: data as unknown as SessionData, loading: false, error: null })
      return data
    } catch (err) {
      const error: ApiError = {
        message: err instanceof Error ? err.message : 'Failed to load demo',
      }
      setState({ data: null, loading: false, error })
      throw error
    }
  }, [])

  return { ...state, loadDemo }
}

/**
 * Hook for session management
 */
export function useSession(sessionId: string | null) {
  const [state, setState] = useState<UseApiState<SessionData>>({
    data: null,
    loading: false,
    error: null,
  })

  const fetchSession = useCallback(async () => {
    if (!sessionId) return null
    
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await api.getSession(sessionId)
      setState({ data: data as unknown as SessionData, loading: false, error: null })
      return data
    } catch (err) {
      const error: ApiError = {
        message: err instanceof Error ? err.message : 'Failed to fetch session',
      }
      setState({ data: null, loading: false, error })
      throw error
    }
  }, [sessionId])

  return { ...state, fetchSession }
}

/**
 * Hook for health check
 */
export function useHealthCheck() {
  const [healthy, setHealthy] = useState<boolean | null>(null)
  const [checking, setChecking] = useState(false)

  const checkHealth = useCallback(async () => {
    setChecking(true)
    try {
      await api.healthCheck()
      setHealthy(true)
    } catch {
      setHealthy(false)
    } finally {
      setChecking(false)
    }
  }, [])

  return { healthy, checking, checkHealth }
}
