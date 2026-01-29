'use client'

import axios from 'axios'
import { AlertCircle, BarChart3, CheckCircle, Clock, Loader2, Megaphone, Play, RefreshCw, TrendingUp } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AnalysisPanelProps {
  sessionId: string
  onComplete: (data: any) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

// Progress messages for each step
const PROGRESS_MESSAGES: Record<string, string[]> = {
  bcg: [
    'Analizando portafolio de productos (últimos 30 días)...',
    'Calculando popularidad y margen de contribución...',
    'Clasificando productos (Estrellas, Caballos, Rompecabezas, Perros)...',
    'Generando estrategias por categoría...',
    'Finalizando análisis de Ingeniería de Menú...'
  ],
  predictions: [
    'Loading sales history...',
    'Training prediction model...',
    'Generating 14-day forecast...',
    'Calculating confidence intervals...',
    'Finalizing predictions...'
  ],
  campaigns: [
    'Analyzing target segments...',
    'Generating campaign ideas...',
    'Creating marketing copy...',
    'Optimizing campaign schedule...',
    'Finalizing campaign proposals...'
  ]
}

export default function AnalysisPanel({ sessionId, onComplete, isLoading, setIsLoading }: AnalysisPanelProps) {
  const [bcgDone, setBcgDone] = useState(false)
  const [predictionsDone, setPredictionsDone] = useState(false)
  const [campaignsDone, setCampaignsDone] = useState(false)
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [results, setResults] = useState<any>({})
  const [elapsedTime, setElapsedTime] = useState(0)
  const [progressIndex, setProgressIndex] = useState(0)
  const [retryCount, setRetryCount] = useState<Record<string, number>>({})
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  // Timer for elapsed time and progress messages
  useEffect(() => {
    if (currentStep) {
      setElapsedTime(0)
      setProgressIndex(0)
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1)
        setProgressIndex(prev => {
          const messages = PROGRESS_MESSAGES[currentStep] || []
          return Math.min(prev + 1, messages.length - 1)
        })
      }, 8000) // Change message every 8 seconds
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [currentStep])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  const runBCGAnalysis = async (isRetry = false) => {
    setCurrentStep('bcg')
    setIsLoading(true)
    if (isRetry) {
      setRetryCount(prev => ({ ...prev, bcg: (prev.bcg || 0) + 1 }))
    }
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/analyze/bcg?session_id=${sessionId}`,
        {},
        { timeout: 0 } // No timeout - allow analysis to complete
      )
      setResults((prev: any) => ({ ...prev, bcg_analysis: res.data }))
      setBcgDone(true)
    } catch (err: any) {
      console.error('BCG error:', err)
      let errorMsg = 'Network Error - is the backend running?'
      if (err.code === 'ECONNABORTED') {
        errorMsg = 'Analysis timed out. The AI is processing a lot of data. Click Retry to continue.'
      } else if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail)
      } else if (err.message) {
        errorMsg = err.message
      }
      alert(`BCG Analysis failed: ${errorMsg}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const runPredictions = async (isRetry = false) => {
    setCurrentStep('predictions')
    setIsLoading(true)
    if (isRetry) {
      setRetryCount(prev => ({ ...prev, predictions: (prev.predictions || 0) + 1 }))
    }
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/predict/sales?session_id=${sessionId}&horizon_days=14`,
        [],
        { timeout: 0 } // No timeout - allow training to complete
      )
      setResults((prev: any) => ({ ...prev, predictions: res.data }))
      setPredictionsDone(true)
    } catch (err: any) {
      console.error('Predictions error:', err)
      let errorMsg = 'Network Error - is the backend running?'
      if (err.code === 'ECONNABORTED') {
        errorMsg = 'Prediction timed out. The ML model needs more time. Click Retry to continue.'
      } else if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail)
      } else if (err.message) {
        errorMsg = err.message
      }
      alert(`Predictions failed: ${errorMsg}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const generateCampaigns = async (isRetry = false) => {
    setCurrentStep('campaigns')
    setIsLoading(true)
    if (isRetry) {
      setRetryCount(prev => ({ ...prev, campaigns: (prev.campaigns || 0) + 1 }))
    }
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/campaigns/generate?session_id=${sessionId}&num_campaigns=3`,
        [],
        { timeout: 300000 } // 5 minutes timeout
      )
      setResults((prev: any) => ({ ...prev, campaigns: res.data.campaigns, thought_signature: res.data.thought_signature }))
      setCampaignsDone(true)
    } catch (err: any) {
      console.error('Campaign error:', err)
      let errorMsg = 'Network Error - is the backend running?'
      if (err.code === 'ECONNABORTED') {
        errorMsg = 'Campaign generation timed out. Gemini is creating detailed proposals. Click Retry to continue.'
      } else if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail)
      } else if (err.message) {
        errorMsg = err.message
      }
      alert(`Campaign generation failed: ${errorMsg}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const runFullAnalysis = async () => {
    await runBCGAnalysis()
    await runPredictions()
    await generateCampaigns()
  }

  const canComplete = bcgDone && campaignsDone

  // Get current progress message
  const getCurrentMessage = () => {
    if (!currentStep) return ''
    const messages = PROGRESS_MESSAGES[currentStep] || []
    return messages[Math.min(progressIndex, messages.length - 1)] || 'Processing...'
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Run Analysis</h2>
        <p className="text-gray-600 mt-2">Execute BCG classification, sales prediction, and campaign generation.</p>
      </div>

      {/* Progress Banner - Shows when any step is running */}
      {currentStep && (
        <div className="bg-gradient-to-r from-primary-50 to-indigo-50 border border-primary-200 rounded-xl p-4 animate-pulse">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Loader2 className="h-5 w-5 text-primary-600 animate-spin" />
              </div>
              <div>
                <p className="font-semibold text-primary-900">{getCurrentMessage()}</p>
                <p className="text-sm text-primary-600">This may take 1-3 minutes. Please wait...</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-primary-700">
              <Clock className="h-4 w-4" />
              <span className="font-mono text-sm">{formatTime(elapsedTime)}</span>
            </div>
          </div>
          {/* Progress bar */}
          <div className="w-full bg-primary-100 rounded-full h-2">
            <div 
              className="bg-primary-500 h-2 rounded-full transition-all duration-1000"
              style={{ width: `${Math.min((progressIndex + 1) * 20, 95)}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* BCG Analysis */}
        <div className={`card ${currentStep === 'bcg' ? 'ring-2 ring-primary-500' : ''}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary-500" />
              <h3 className="font-semibold">BCG Analysis</h3>
            </div>
            {bcgDone && <CheckCircle className="h-5 w-5 text-green-500" />}
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Classify products as Stars, Cash Cows, Question Marks, or Dogs based on market performance.
          </p>
          <button
            onClick={() => runBCGAnalysis(retryCount.bcg > 0)}
            disabled={isLoading || bcgDone}
            className={`w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
              bcgDone ? 'bg-green-100 text-green-700' : 'btn-primary'
            }`}
          >
            {currentStep === 'bcg' ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Processing...</>
            ) : bcgDone ? (
              'Completed'
            ) : retryCount.bcg > 0 ? (
              <><RefreshCw className="h-4 w-4" /> Retry</>
            ) : (
              'Run BCG'
            )}
          </button>
        </div>

        {/* Predictions */}
        <div className={`card ${currentStep === 'predictions' ? 'ring-2 ring-primary-500' : ''}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary-500" />
              <h3 className="font-semibold">Sales Prediction</h3>
            </div>
            {predictionsDone && <CheckCircle className="h-5 w-5 text-green-500" />}
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Forecast sales for the next 14 days under different campaign scenarios.
          </p>
          <button
            onClick={() => runPredictions(retryCount.predictions > 0)}
            disabled={isLoading || predictionsDone || !bcgDone}
            className={`w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
              predictionsDone ? 'bg-green-100 text-green-700' : !bcgDone ? 'bg-gray-200 text-gray-500' : 'btn-primary'
            }`}
          >
            {currentStep === 'predictions' ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Processing...</>
            ) : predictionsDone ? (
              'Completed'
            ) : retryCount.predictions > 0 ? (
              <><RefreshCw className="h-4 w-4" /> Retry</>
            ) : (
              'Run Predictions'
            )}
          </button>
        </div>

        {/* Campaigns */}
        <div className={`card ${currentStep === 'campaigns' ? 'ring-2 ring-primary-500' : ''}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Megaphone className="h-5 w-5 text-primary-500" />
              <h3 className="font-semibold">Campaign Generation</h3>
            </div>
            {campaignsDone && <CheckCircle className="h-5 w-5 text-green-500" />}
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Generate 3 strategic marketing campaign proposals with copy and scheduling.
          </p>
          <button
            onClick={() => generateCampaigns(retryCount.campaigns > 0)}
            disabled={isLoading || campaignsDone || !bcgDone}
            className={`w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
              campaignsDone ? 'bg-green-100 text-green-700' : !bcgDone ? 'bg-gray-200 text-gray-500' : 'btn-primary'
            }`}
          >
            {currentStep === 'campaigns' ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Processing...</>
            ) : campaignsDone ? (
              'Completed'
            ) : retryCount.campaigns > 0 ? (
              <><RefreshCw className="h-4 w-4" /> Retry</>
            ) : (
              'Generate'
            )}
          </button>
        </div>
      </div>

      {/* Time Warning */}
      {!currentStep && !bcgDone && (
        <div className="flex items-center justify-center gap-2 text-amber-600 bg-amber-50 rounded-lg p-3">
          <AlertCircle className="h-5 w-5" />
          <p className="text-sm">Each analysis step may take 1-3 minutes. Please be patient while the AI processes your data.</p>
        </div>
      )}

      {/* Run All Button */}
      <div className="text-center space-y-4">
        {!bcgDone && (
          <button onClick={runFullAnalysis} disabled={isLoading} className="btn-secondary px-8 py-3 flex items-center gap-2 mx-auto">
            {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />}
            Run Full Analysis
          </button>
        )}
        
        {canComplete && (
          <button onClick={() => onComplete(results)} className="btn-primary px-8 py-3 text-lg">
            View Results
          </button>
        )}
      </div>
    </div>
  )
}
