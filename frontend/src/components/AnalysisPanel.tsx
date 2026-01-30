'use client'

import axios from 'axios'
import { BarChart3, CheckCircle, ChevronRight, Clock, Loader2, Megaphone, MessageSquare, Play, RefreshCw, Target, TrendingUp } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AnalysisPanelProps {
  sessionId: string
  sessionData?: any
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
    'Cargando histórico de ventas...',
    'Entrenando modelo de predicción (XGBoost + LSTM)...',
    'Generando pronóstico a 14 días...',
    'Calculando intervalos de confianza...',
    'Finalizando proyecciones...'
  ],
  competitors: [
    'Identificando competidores cercanos...',
    'Analizando posicionamiento de precios...',
    'Comparando oferta gastronómica...',
    'Detectando brechas de mercado...',
    'Finalizando inteligencia competitiva...'
  ],
  sentiment: [
    'Recopilando reseñas de Google y redes sociales...',
    'Analizando sentimiento de clientes...',
    'Procesando feedback sobre platos específicos...',
    'Detectando quejas recurrentes y elogios...',
    'Generando insights de reputación...'
  ],
  campaigns: [
    'Analizando segmentos objetivo...',
    'Generando ideas de campaña creativas...',
    'Redactando copy de marketing...',
    'Optimizando calendario de promociones...',
    'Finalizando propuestas de campaña...'
  ]
}

export default function AnalysisPanel({ sessionId, sessionData, onComplete, isLoading, setIsLoading }: AnalysisPanelProps) {
  const [bcgDone, setBcgDone] = useState(!!sessionData?.bcg_analysis)
  const [predictionsDone, setPredictionsDone] = useState(!!sessionData?.predictions)
  const [competitorsDone, setCompetitorsDone] = useState(!!sessionData?.competitor_analysis)
  const [sentimentDone, setSentimentDone] = useState(!!sessionData?.sentiment_analysis)
  const [campaignsDone, setCampaignsDone] = useState(!!sessionData?.campaigns && sessionData.campaigns.length > 0)
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [results, setResults] = useState<any>({})
  const [elapsedTime, setElapsedTime] = useState(0)
  const [progressIndex, setProgressIndex] = useState(0)
  const [retryCount, setRetryCount] = useState<Record<string, number>>({})
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const mounted = useRef(false)

  // Auto-start analysis on mount
  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true
      runFullAnalysis()
    }
  }, [])

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
      }, 8000)
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
        { timeout: 0 }
      )
      const data = { bcg_analysis: res.data }
      setResults((prev: any) => ({ ...prev, ...data }))
      onComplete(data)
      setBcgDone(true)
    } catch (err: any) {
      console.error('BCG error:', err)
      alert(`BCG Analysis failed: ${err.message}`)
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
        { timeout: 0 }
      )
      const data = { predictions: res.data }
      setResults((prev: any) => ({ ...prev, ...data }))
      onComplete(data)
      setPredictionsDone(true)
    } catch (err: any) {
      console.error('Predictions error:', err)
      alert(`Predictions failed: ${err.message}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const runCompetitorAnalysis = async (isRetry = false) => {
    setCurrentStep('competitors')
    setIsLoading(true)
    if (isRetry) {
      setRetryCount(prev => ({ ...prev, competitors: (prev.competitors || 0) + 1 }))
    }
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/analyze/competitors?session_id=${sessionId}`,
        {},
        { timeout: 0 }
      )
      const data = { competitor_analysis: res.data.competitor_analysis }
      setResults((prev: any) => ({ ...prev, ...data }))
      onComplete(data)
      setCompetitorsDone(true)
    } catch (err: any) {
      console.error('Competitor Analysis error:', err)
      // Non-blocking error
      console.warn('Continuing without competitor analysis')
      setCompetitorsDone(true) // Mark as done to allow flow to continue
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const runSentimentAnalysis = async (isRetry = false) => {
    setCurrentStep('sentiment')
    setIsLoading(true)
    if (isRetry) {
      setRetryCount(prev => ({ ...prev, sentiment: (prev.sentiment || 0) + 1 }))
    }
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/analyze/sentiment?session_id=${sessionId}`,
        {},
        { timeout: 0 }
      )
      const data = { sentiment_analysis: res.data.sentiment_analysis }
      setResults((prev: any) => ({ ...prev, ...data }))
      onComplete(data)
      setSentimentDone(true)
    } catch (err: any) {
      console.error('Sentiment Analysis error:', err)
      // Non-blocking error
      console.warn('Continuing without sentiment analysis')
      setSentimentDone(true) // Mark as done to allow flow to continue
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
        { timeout: 300000 }
      )
      const data = { campaigns: res.data.campaigns, thought_signature: res.data.thought_signature }
      setResults((prev: any) => ({ ...prev, ...data }))
      onComplete(data)
      setCampaignsDone(true)
    } catch (err: any) {
      console.error('Campaign error:', err)
      alert(`Campaign generation failed: ${err.message}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const runFullAnalysis = async () => {
    if (!bcgDone) await runBCGAnalysis()
    if (!predictionsDone) await runPredictions()
    if (!competitorsDone) await runCompetitorAnalysis()
    if (!sentimentDone) await runSentimentAnalysis()
    if (!campaignsDone) await generateCampaigns()
  }

  // Get current progress message
  const getCurrentMessage = () => {
    if (!currentStep) return ''
    const messages = PROGRESS_MESSAGES[currentStep] || []
    return messages[Math.min(progressIndex, messages.length - 1)] || 'Processing...'
  }

  // Render a step item
  const renderStep = (
    id: string, 
    title: string, 
    description: string, 
    icon: any, 
    isDone: boolean, 
    onRun: () => void, 
    isDisabled: boolean
  ) => {
    const isRunning = currentStep === id
    const Icon = icon

    return (
      <div className={`relative flex gap-4 p-4 rounded-xl border transition-all ${
        isRunning 
          ? 'bg-blue-50 border-blue-200 shadow-md scale-[1.02]' 
          : isDone 
            ? 'bg-white border-green-200' 
            : 'bg-white border-gray-100 hover:border-gray-300'
      }`}>
        {/* Icon & Status */}
        <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
          isRunning 
            ? 'bg-blue-100 text-blue-600 animate-pulse' 
            : isDone 
              ? 'bg-green-100 text-green-600' 
              : 'bg-gray-100 text-gray-500'
        }`}>
          {isRunning ? <Loader2 className="h-6 w-6 animate-spin" /> : isDone ? <CheckCircle className="h-6 w-6" /> : <Icon className="h-6 w-6" />}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className={`font-semibold text-lg ${isRunning ? 'text-blue-900' : 'text-gray-900'}`}>{title}</h3>
            {isDone && !isRunning && (
              <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">Completed</span>
            )}
          </div>
          
          <p className="text-sm text-gray-600 mb-3">{description}</p>
          
          {isRunning && (
            <div className="mb-3 space-y-2">
              <div className="flex items-center gap-2 text-xs text-blue-700 font-medium">
                <Clock className="h-3 w-3" />
                {formatTime(elapsedTime)} - {getCurrentMessage()}
              </div>
              <div className="w-full bg-blue-200 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="bg-blue-500 h-full rounded-full transition-all duration-1000"
                  style={{ width: `${Math.min((progressIndex + 1) * 20, 95)}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex gap-2">
            {!isRunning && (
              <button
                onClick={onRun}
                disabled={isDisabled}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
                  isDone 
                    ? 'bg-gray-100 text-gray-600 hover:bg-gray-200' 
                    : 'bg-primary-600 text-white hover:bg-primary-700 shadow-sm'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isDone ? <RefreshCw className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                {isDone ? 'Run Again' : 'Run Analysis'}
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-4">
        {/* Step 1: BCG */}
        {renderStep(
          'bcg',
          '1. BCG Matrix Classification',
          'Classify your menu items into Stars, Cash Cows, Question Marks, and Dogs based on sales performance.',
          BarChart3,
          bcgDone,
          () => runBCGAnalysis(bcgDone),
          isLoading && currentStep !== 'bcg'
        )}

        {/* Connector Line */}
        <div className="pl-6">
          <div className={`w-0.5 h-6 ${bcgDone ? 'bg-green-200' : 'bg-gray-200'}`} />
        </div>

        {/* Step 2: Predictions */}
        {renderStep(
          'predictions',
          '2. AI Sales Predictions',
          'Forecast sales for the next 14 days to optimize inventory and staffing.',
          TrendingUp,
          predictionsDone,
          () => runPredictions(predictionsDone),
          isLoading && currentStep !== 'predictions'
        )}

        {/* Connector Line */}
        <div className="pl-6">
          <div className={`w-0.5 h-6 ${predictionsDone ? 'bg-green-200' : 'bg-gray-200'}`} />
        </div>

        {/* Step 3: Competitor Analysis */}
        {renderStep(
          'competitors',
          '3. Competitive Intelligence',
          'Analyze market positioning, price gaps, and competitor offerings.',
          Target,
          competitorsDone,
          () => runCompetitorAnalysis(competitorsDone),
          isLoading && currentStep !== 'competitors'
        )}

        {/* Connector Line */}
        <div className="pl-6">
          <div className={`w-0.5 h-6 ${competitorsDone ? 'bg-green-200' : 'bg-gray-200'}`} />
        </div>

        {/* Step 4: Sentiment Analysis */}
        {renderStep(
          'sentiment',
          '4. Customer Sentiment',
          'Analyze reviews and feedback to understand customer satisfaction and reputation.',
          MessageSquare,
          sentimentDone,
          () => runSentimentAnalysis(sentimentDone),
          isLoading && currentStep !== 'sentiment'
        )}

        {/* Connector Line */}
        <div className="pl-6">
          <div className={`w-0.5 h-6 ${sentimentDone ? 'bg-green-200' : 'bg-gray-200'}`} />
        </div>

        {/* Step 5: Campaigns */}
        {renderStep(
          'campaigns',
          '5. Marketing Campaigns',
          'Generate targeted marketing proposals to boost revenue and promote specific items.',
          Megaphone,
          campaignsDone,
          () => generateCampaigns(campaignsDone),
          isLoading && currentStep !== 'campaigns'
        )}
      </div>

      {/* Global Actions */}
      <div className="flex justify-end items-center gap-4 pt-4 border-t border-gray-100">
        {!isLoading && !currentStep && (
          <>
            {(!bcgDone || !predictionsDone || !competitorsDone || !sentimentDone || !campaignsDone) && (
               <button 
                onClick={runFullAnalysis}
                className="text-primary-600 hover:text-primary-700 text-sm font-medium hover:underline"
              >
                Run Remaining Steps Automatically
              </button>
            )}
            
            {(bcgDone || campaignsDone) && (
              <button 
                onClick={() => onComplete(results)} 
                className="btn-primary px-6 py-3 flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
              >
                View Strategic Results
                <ChevronRight className="h-5 w-5" />
              </button>
            )}
          </>
        )}
      </div>
    </div>
  )
}
