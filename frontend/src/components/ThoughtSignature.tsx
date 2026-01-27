'use client'

import { AlertTriangle, Brain, CheckCircle, Lightbulb, ListChecks } from 'lucide-react'
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
  }
}

export default function ThoughtSignature({ signature }: ThoughtSignatureProps) {
  const [expanded, setExpanded] = useState(false)

  const confidenceColor = signature.confidence >= 0.8 ? 'text-green-600' : signature.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'
  const confidenceLabel = signature.confidence >= 0.8 ? 'High' : signature.confidence >= 0.6 ? 'Medium' : 'Low'

  return (
    <div className="card bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-600" />
          <h3 className="font-semibold text-purple-900">Thought Signature</h3>
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">AI Reasoning Trace</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${confidenceColor}`}>
            {confidenceLabel} Confidence ({(signature.confidence * 100).toFixed(0)}%)
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-purple-600 hover:text-purple-800"
          >
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>

      {/* Always visible: Plan */}
      <div className="mb-4">
        <div className="flex items-center gap-2 text-purple-700 mb-2">
          <ListChecks className="h-4 w-4" />
          <span className="text-sm font-medium">Agent Plan</span>
        </div>
        <ol className="space-y-1">
          {signature.plan.slice(0, expanded ? undefined : 3).map((step, idx) => (
            <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
              <span className="text-purple-500 font-medium">{idx + 1}.</span>
              {step}
            </li>
          ))}
          {!expanded && signature.plan.length > 3 && (
            <li className="text-sm text-purple-600">+{signature.plan.length - 3} more steps...</li>
          )}
        </ol>
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
