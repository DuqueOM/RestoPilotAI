'use client'

import { ThoughtStep } from '@/components/common/ProgressTracker'
import { useCallback, useEffect, useRef, useState } from 'react'

interface UseThinkingStreamOptions {
  sessionId: string | null
  autoConnect?: boolean
  onThought?: (thought: ThoughtStep) => void
  onComplete?: () => void
  onError?: (error: string) => void
}

interface ThinkingStreamState {
  thoughts: ThoughtStep[]
  isConnected: boolean
  isActive: boolean
  currentStep: string | null
  error: string | null
}

type WebSocketMessage = {
  type: 'connected' | 'thought' | 'progress' | 'stage_complete' | 'completed' | 'error' | 'heartbeat' | 'pong'
  session_id?: string
  thought?: {
    id: string
    type: 'thinking' | 'observation' | 'action' | 'verification' | 'result'
    content: string
    confidence?: number
    step?: string
  }
  stage?: string
  progress?: number
  message?: string
  error?: string
  timestamp?: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_BASE = API_BASE.replace('http', 'ws')

export function useThinkingStream({
  sessionId,
  autoConnect = true,
  onThought,
  onComplete,
  onError,
}: UseThinkingStreamOptions) {
  const [state, setState] = useState<ThinkingStreamState>({
    thoughts: [],
    isConnected: false,
    isActive: false,
    currentStep: null,
    error: null,
  })

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const addThought = useCallback((thought: ThoughtStep) => {
    setState(prev => {
      // Mark previous streaming thought as complete
      const updatedThoughts = prev.thoughts.map(t => 
        t.isStreaming ? { ...t, isStreaming: false } : t
      )
      return {
        ...prev,
        thoughts: [...updatedThoughts, thought],
      }
    })
    onThought?.(thought)
  }, [onThought])

  const connect = useCallback(() => {
    if (!sessionId || wsRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = `${WS_BASE}/ws/analysis/${sessionId}`
    
    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setState(prev => ({ ...prev, isConnected: true, error: null }))
        
        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 25000)
      }

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)

          switch (data.type) {
            case 'connected':
              setState(prev => ({ ...prev, isActive: true }))
              break

            case 'thought':
              if (data.thought) {
                const thought: ThoughtStep = {
                  id: data.thought.id || `thought-${Date.now()}`,
                  type: data.thought.type,
                  content: data.thought.content,
                  timestamp: Date.now(),
                  confidence: data.thought.confidence,
                  isStreaming: true,
                }
                addThought(thought)
                if (data.thought.step) {
                  setState(prev => ({ ...prev, currentStep: data.thought!.step! }))
                }
              }
              break

            case 'progress':
              // Convert progress message to thought
              if (data.message && data.stage) {
                const thought: ThoughtStep = {
                  id: `progress-${data.stage}-${Date.now()}`,
                  type: 'action',
                  content: data.message,
                  timestamp: Date.now(),
                  isStreaming: false,
                }
                addThought(thought)
                setState(prev => ({ ...prev, currentStep: data.stage! }))
              }
              break

            case 'stage_complete':
              setState(prev => ({ 
                ...prev, 
                thoughts: prev.thoughts.map(t => ({ ...t, isStreaming: false }))
              }))
              break

            case 'completed':
              setState(prev => ({ 
                ...prev, 
                isActive: false,
                thoughts: prev.thoughts.map(t => ({ ...t, isStreaming: false }))
              }))
              onComplete?.()
              break

            case 'error':
              setState(prev => ({ ...prev, error: data.error || 'Unknown error', isActive: false }))
              onError?.(data.error || 'Unknown error')
              break

            case 'heartbeat':
            case 'pong':
              // Keep-alive, no action needed
              break
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setState(prev => ({ ...prev, error: 'Connection error' }))
      }

      ws.onclose = () => {
        setState(prev => ({ ...prev, isConnected: false }))
        
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current)
        }

        // Attempt reconnect after 3 seconds if session is still active
        if (state.isActive) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 3000)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      setState(prev => ({ ...prev, error: 'Failed to connect' }))
    }
  }, [sessionId, addThought, onComplete, onError, state.isActive])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setState(prev => ({ ...prev, isConnected: false, isActive: false }))
  }, [])

  const clearThoughts = useCallback(() => {
    setState(prev => ({ ...prev, thoughts: [], currentStep: null, error: null }))
  }, [])

  const setActive = useCallback((active: boolean) => {
    setState(prev => ({ ...prev, isActive: active }))
  }, [])

  // Simulate thoughts for testing/demo (when no WebSocket)
  const simulateThought = useCallback((
    type: ThoughtStep['type'],
    content: string,
    confidence?: number
  ) => {
    const thought: ThoughtStep = {
      id: `simulated-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type,
      content,
      timestamp: Date.now(),
      confidence,
      isStreaming: true,
    }
    addThought(thought)

    // Mark as complete after short delay
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        thoughts: prev.thoughts.map(t => 
          t.id === thought.id ? { ...t, isStreaming: false } : t
        ),
      }))
    }, 1500)
  }, [addThought])

  // Auto-connect when sessionId is available
  useEffect(() => {
    if (autoConnect && sessionId) {
      connect()
    }
    return () => {
      disconnect()
    }
  }, [sessionId, autoConnect, connect, disconnect])

  return {
    ...state,
    connect,
    disconnect,
    clearThoughts,
    setActive,
    simulateThought,
  }
}

export default useThinkingStream
