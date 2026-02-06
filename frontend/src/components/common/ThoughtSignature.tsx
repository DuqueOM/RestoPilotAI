'use client'

import { AlertTriangle, Brain, CheckCircle, ChevronDown, ChevronUp, Lightbulb, ListChecks, Sparkles } from 'lucide-react'
import { useState } from 'react'

interface ThoughtSignatureProps {
  signature: {
    plan: string[]
    observations: string[]
    reasoning: string
    assumptions: string[]
    confidence: number
    verification_checks?: Array<{ check: string; passed: boolean }>
    corrections_made?: string[]
    thinking_level?: 'QUICK' | 'STANDARD' | 'DEEP' | 'EXHAUSTIVE'
  }
}

const THINKING_LEVEL_COLORS = {
  QUICK: 'bg-blue-100 text-blue-700',
  STANDARD: 'bg-purple-100 text-purple-700',
  DEEP: 'bg-indigo-100 text-indigo-700',
  EXHAUSTIVE: 'bg-violet-100 text-violet-700',
}

export default function ThoughtSignature({ signature }: ThoughtSignatureProps) {
  const [expanded, setExpanded] = useState(false)
  const [showAllSteps, setShowAllSteps] = useState(false)

  const confidenceColor = signature.confidence >= 0.8 ? 'text-green-600' : signature.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'
  const confidenceLabel = signature.confidence >= 0.8 ? 'High' : signature.confidence >= 0.6 ? 'Medium' : 'Low'
  const thinkingLevel = signature.thinking_level || 'STANDARD'

  return (
    <div className="card bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-600" />
          <h3 className="font-semibold text-purple-900">Thought Signature</h3>
          <span className={`text-xs px-2 py-0.5 rounded-full ${THINKING_LEVEL_COLORS[thinkingLevel]}`}>
            {thinkingLevel}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-medium ${confidenceColor}`}>
            Confidence {confidenceLabel} ({(signature.confidence * 100).toFixed(0)}%)
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-800 font-medium transition-colors"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Collapse
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Expand
              </>
            )}
          </button>
        </div>
      </div>

      {/* Always visible: Plan with expandable steps */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-purple-700">
            <ListChecks className="h-4 w-4" />
            <span className="text-sm font-medium">Agent Plan</span>
            <span className="text-xs text-purple-500">({signature.plan.length} steps)</span>
          </div>
          {signature.plan.length > 3 && (
            <button
              onClick={() => setShowAllSteps(!showAllSteps)}
              className="text-xs text-purple-600 hover:text-purple-800 flex items-center gap-1"
            >
              {showAllSteps ? 'Show less' : `Show all (+${signature.plan.length - 3})`}
              {showAllSteps ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>
          )}
        </div>
        <ol className="space-y-1.5">
          {signature.plan.slice(0, showAllSteps ? undefined : 3).map((step, idx) => (
            <li key={idx} className="text-sm text-gray-700 flex items-start gap-2 p-2 bg-white/50 rounded-lg">
              <span className="flex items-center justify-center w-5 h-5 bg-purple-500 text-white text-xs font-bold rounded-full shrink-0">
                {idx + 1}
              </span>
              <span>{step}</span>
            </li>
          ))}
        </ol>
        {!showAllSteps && signature.plan.length > 3 && (
          <button 
            onClick={() => setShowAllSteps(true)}
            className="mt-2 w-full py-2 text-sm text-purple-600 hover:text-purple-800 hover:bg-purple-100 rounded-lg transition-colors flex items-center justify-center gap-1"
          >
            <Sparkles className="h-4 w-4" />
            Show {signature.plan.length - 3} more steps
          </button>
        )}
      </div>

      {expanded && (
        <>
          {/* Observations */}
          <div className="mb-4">
            <div className="flex items-center gap-2 text-purple-700 mb-2">
              <Lightbulb className="h-4 w-4" />
              <span className="text-sm font-medium">Key Observations</span>
            </div>
            <ul className="space-y-1">
              {signature.observations.map((obs, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-purple-400">•</span>
                  {obs}
                </li>
              ))}
            </ul>
          </div>

          {/* Reasoning */}
          <div className="mb-4">
            <div className="flex items-center gap-2 text-purple-700 mb-2">
              <Brain className="h-4 w-4" />
              <span className="text-sm font-medium">Reasoning Chain</span>
            </div>
            <p className="text-sm text-gray-700 bg-white/50 p-3 rounded-lg">{signature.reasoning}</p>
          </div>

          {/* Assumptions */}
          <div className="mb-4">
            <div className="flex items-center gap-2 text-yellow-700 mb-2">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm font-medium">Assumptions Made</span>
            </div>
            <ul className="space-y-1">
              {signature.assumptions.map((assumption, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-yellow-500">⚠</span>
                  {assumption}
                </li>
              ))}
            </ul>
          </div>

          {/* Verification Checks */}
          {signature.verification_checks && signature.verification_checks.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-green-700 mb-2">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm font-medium">Self-Verification</span>
              </div>
              <ul className="space-y-1">
                {signature.verification_checks.map((check, idx) => (
                  <li key={idx} className="text-sm flex items-center gap-2">
                    {check.passed ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    )}
                    <span className={check.passed ? 'text-green-700' : 'text-red-700'}>{check.check}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  )
}
