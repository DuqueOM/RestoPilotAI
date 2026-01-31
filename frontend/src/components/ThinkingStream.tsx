'use client'

import { Brain, ChevronDown, ChevronUp, Loader2, Sparkles, Eye, CheckCircle2, AlertCircle } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'

export interface ThoughtStep {
  id: string
  type: 'thinking' | 'observation' | 'action' | 'verification' | 'result'
  content: string
  timestamp: number
  confidence?: number
  isStreaming?: boolean
}

interface ThinkingStreamProps {
  thoughts: ThoughtStep[]
  isActive: boolean
  title?: string
  showConfidence?: boolean
  defaultExpanded?: boolean
  onToggle?: (expanded: boolean) => void
}

const THOUGHT_ICONS = {
  thinking: Brain,
  observation: Eye,
  action: Sparkles,
  verification: CheckCircle2,
  result: AlertCircle,
}

const THOUGHT_COLORS = {
  thinking: 'text-purple-600 bg-purple-50 border-purple-200',
  observation: 'text-blue-600 bg-blue-50 border-blue-200',
  action: 'text-amber-600 bg-amber-50 border-amber-200',
  verification: 'text-green-600 bg-green-50 border-green-200',
  result: 'text-indigo-600 bg-indigo-50 border-indigo-200',
}

const THOUGHT_LABELS = {
  thinking: 'Razonando',
  observation: 'Observación',
  action: 'Ejecutando',
  verification: 'Verificando',
  result: 'Resultado',
}

export default function ThinkingStream({
  thoughts,
  isActive,
  title = 'Gemini está pensando...',
  showConfidence = true,
  defaultExpanded = true,
  onToggle,
}: ThinkingStreamProps) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const streamRef = useRef<HTMLDivElement>(null)
  const [displayedText, setDisplayedText] = useState<Record<string, string>>({})

  // Auto-scroll to latest thought
  useEffect(() => {
    if (expanded && streamRef.current && thoughts.length > 0) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight
    }
  }, [thoughts, expanded])

  // Streaming text effect for active thoughts
  useEffect(() => {
    const activeThought = thoughts.find(t => t.isStreaming)
    if (!activeThought) {
      // Set all non-streaming thoughts to their full content
      const newDisplayed: Record<string, string> = {}
      thoughts.forEach(t => {
        newDisplayed[t.id] = t.content
      })
      setDisplayedText(newDisplayed)
      return
    }

    const fullText = activeThought.content
    let currentIndex = displayedText[activeThought.id]?.length || 0

    if (currentIndex >= fullText.length) return

    const interval = setInterval(() => {
      currentIndex += 2 // Speed of typing
      setDisplayedText(prev => ({
        ...prev,
        [activeThought.id]: fullText.slice(0, currentIndex),
      }))

      if (currentIndex >= fullText.length) {
        clearInterval(interval)
      }
    }, 20) // Typing speed in ms

    return () => clearInterval(interval)
  }, [thoughts])

  const handleToggle = () => {
    const newExpanded = !expanded
    setExpanded(newExpanded)
    onToggle?.(newExpanded)
  }

  const averageConfidence = thoughts.length > 0
    ? thoughts.filter(t => t.confidence).reduce((sum, t) => sum + (t.confidence || 0), 0) /
      thoughts.filter(t => t.confidence).length
    : 0

  if (thoughts.length === 0 && !isActive) return null

  return (
    <div className={`
      rounded-xl border transition-all duration-300 overflow-hidden
      ${isActive 
        ? 'bg-gradient-to-br from-purple-50/80 to-indigo-50/80 border-purple-200 shadow-lg shadow-purple-100/50' 
        : 'bg-gray-50/50 border-gray-200'
      }
    `}>
      {/* Header - Always visible */}
      <button
        onClick={handleToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          {isActive ? (
            <div className="relative">
              <Brain className="h-5 w-5 text-purple-600" />
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-purple-500"></span>
              </span>
            </div>
          ) : (
            <Brain className="h-5 w-5 text-gray-500" />
          )}
          
          <span className={`font-medium text-sm ${isActive ? 'text-purple-900' : 'text-gray-600'}`}>
            {isActive ? title : 'Proceso de razonamiento'}
          </span>

          {isActive && (
            <Loader2 className="h-4 w-4 text-purple-500 animate-spin" />
          )}

          {!isActive && thoughts.length > 0 && (
            <span className="text-xs text-gray-500 bg-gray-200/50 px-2 py-0.5 rounded-full">
              {thoughts.length} pasos
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {showConfidence && averageConfidence > 0 && !isActive && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              averageConfidence >= 0.8 ? 'bg-green-100 text-green-700' :
              averageConfidence >= 0.6 ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              {(averageConfidence * 100).toFixed(0)}% confianza
            </span>
          )}
          
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          )}
        </div>
      </button>

      {/* Content - Collapsible */}
      <div className={`
        transition-all duration-300 ease-in-out
        ${expanded ? 'max-h-[400px] opacity-100' : 'max-h-0 opacity-0'}
      `}>
        <div 
          ref={streamRef}
          className="px-4 pb-4 space-y-2 max-h-[360px] overflow-y-auto scrollbar-thin scrollbar-thumb-purple-200 scrollbar-track-transparent"
        >
          {thoughts.length === 0 && isActive && (
            <div className="flex items-center gap-2 text-sm text-purple-600 py-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="animate-pulse">Iniciando análisis...</span>
            </div>
          )}

          {thoughts.map((thought, index) => {
            const Icon = THOUGHT_ICONS[thought.type]
            const colorClass = THOUGHT_COLORS[thought.type]
            const label = THOUGHT_LABELS[thought.type]
            const text = displayedText[thought.id] || thought.content

            return (
              <div
                key={thought.id}
                className={`
                  flex items-start gap-3 p-3 rounded-lg border animate-in fade-in slide-in-from-bottom-2 duration-300
                  ${colorClass}
                `}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex-shrink-0 mt-0.5">
                  <Icon className="h-4 w-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold uppercase tracking-wide opacity-75">
                      {label}
                    </span>
                    {thought.confidence && (
                      <span className="text-xs opacity-60">
                        ({(thought.confidence * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm leading-relaxed">
                    {text}
                    {thought.isStreaming && (
                      <span className="inline-block w-1.5 h-4 bg-current ml-0.5 animate-pulse" />
                    )}
                  </p>
                </div>
              </div>
            )
          })}

          {/* Typing indicator when active but no current streaming thought */}
          {isActive && thoughts.length > 0 && !thoughts.find(t => t.isStreaming) && (
            <div className="flex items-center gap-2 text-sm text-purple-500 py-2 pl-3">
              <span className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </span>
              <span className="text-xs text-purple-400">procesando...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
