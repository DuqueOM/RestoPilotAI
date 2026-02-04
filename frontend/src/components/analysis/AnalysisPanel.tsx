'use client'

import { useWebSocket } from '@/hooks/useWebSocket'
import { WebSocketMessage } from '@/lib/api/websocket'
import axios from 'axios'
import {
    BarChart3,
    Camera,
    CheckCircle,
    Clock,
    Loader2,
    MapPin,
    Megaphone,
    Play,
    ShieldCheck,
    TrendingUp,
    Utensils
} from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import ThinkingStream, { ThoughtStep } from '../common/ProgressTracker'

const API_URL = ''

interface AnalysisPanelProps {
  sessionId: string
  sessionData?: any
  onComplete: (data: any) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

// Stages of the new RestoPilotAI Pipeline
const ANALYSIS_STAGES = [
  { 
    id: 'menu_ingestion', 
    title: '1. Ingesta y Digitalización', 
    description: 'Extracción multimodal del menú y análisis de calidad fotográfica.',
    icon: Utensils
  },
  { 
    id: 'competitor_scout', 
    title: '2. Scout Agent: Discovery', 
    description: 'Búsqueda autónoma de competidores y análisis de posicionamiento.',
    icon: MapPin 
  },
  { 
    id: 'visual_sentiment', 
    title: '3. Análisis Sensorial y Reputación', 
    description: 'Evaluación visual de platos (Visual Gap) y sentimiento de reseñas.',
    icon: Camera 
  },
  { 
    id: 'strategic_analysis', 
    title: '4. Matriz Estratégica BCG', 
    description: 'Clasificación de rentabilidad y popularidad de productos.',
    icon: BarChart3 
  },
  { 
    id: 'predictive_model', 
    title: '5. Motor Predictivo', 
    description: 'Proyección de demanda futura con escenarios (XGBoost).',
    icon: TrendingUp 
  },
  { 
    id: 'growth_actions', 
    title: '6. Plan de Crecimiento', 
    description: 'Generación de campañas y verificación autónoma de estrategias.',
    icon: Megaphone 
  }
]

// Mapping from Backend Pipeline Stages to Frontend UI Stages
const BACKEND_TO_FRONTEND_STAGE_MAP: Record<string, string> = {
  'data_ingestion': 'menu_ingestion',
  'menu_extraction': 'menu_ingestion',
  'image_analysis': 'menu_ingestion',
  
  'competitor_discovery': 'competitor_scout',
  'competitor_analysis': 'competitor_scout',
  
  'sentiment_analysis': 'visual_sentiment',
  'visual_gap_analysis': 'visual_sentiment',
  
  'bcg_classification': 'strategic_analysis',
  'sales_processing': 'strategic_analysis',
  
  'sales_prediction': 'predictive_model',
  
  'campaign_generation': 'growth_actions',
  'verification': 'growth_actions'
}

export default function AnalysisPanel({ sessionId, sessionData, onComplete, isLoading, setIsLoading }: AnalysisPanelProps) {
  // State for each stage completion
  const [stageStatus, setStageStatus] = useState<Record<string, 'pending' | 'running' | 'completed' | 'failed'>>({})
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [stepThoughts, setStepThoughts] = useState<Record<string, ThoughtStep[]>>({})
  const [processingTime, setProcessingTime] = useState<Record<string, number>>({})
  
  const startTimeRef = useRef<number | null>(null)
  const mounted = useRef(false)

  // Initialize status based on sessionData if available
  useEffect(() => {
    if (sessionData) {
      const newStatus: any = {}
      if (sessionData.menu_items?.length > 0) newStatus.menu_ingestion = 'completed'
      if (sessionData.competitor_analysis) newStatus.competitor_scout = 'completed'
      if (sessionData.sentiment_analysis) newStatus.visual_sentiment = 'completed'
      if (sessionData.bcg_analysis) newStatus.strategic_analysis = 'completed'
      if (sessionData.predictions) newStatus.predictive_model = 'completed'
      if (sessionData.campaigns?.length > 0) newStatus.growth_actions = 'completed'
      setStageStatus(prev => ({ ...prev, ...newStatus }))
    }
  }, [sessionData])

  // Helper to add thoughts to stream
  const addThought = useCallback((step: string, thought: Omit<ThoughtStep, 'id' | 'timestamp'>) => {
    const newThought: ThoughtStep = {
      ...thought,
      id: `${step}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      timestamp: Date.now(),
      isStreaming: true, // Only new thoughts stream
    }
    
    setStepThoughts(prev => ({
      ...prev,
      [step]: [...(prev[step] || []), newThought],
    }))

    // Turn off streaming effect after a delay
    setTimeout(() => {
      setStepThoughts(prev => ({
        ...prev,
        [step]: prev[step]?.map(t => t.id === newThought.id ? { ...t, isStreaming: false } : t) || [],
      }))
    }, 1500)
  }, [])

  // WebSocket Connection - Dynamic URL derivation
  const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = typeof window !== 'undefined' ? window.location.host : 'localhost:3000'
  const defaultWsUrl = `${wsProtocol}//${wsHost}/api/v1`
  const WS_URL = process.env.NEXT_PUBLIC_WS_URL || defaultWsUrl
  
  const { lastMessage } = useWebSocket(sessionId ? `${WS_URL}/ws/analysis/${sessionId}` : null)

  useEffect(() => {
    if (!lastMessage) return

    try {
      const msg: WebSocketMessage = JSON.parse(lastMessage)

      // 1. Handle Thoughts
      if (msg.type === 'thought' && msg.thought) {
        const backendStep = msg.thought.step || ''
        const frontendStage = BACKEND_TO_FRONTEND_STAGE_MAP[backendStep] || currentStep
        
        if (frontendStage) {
          // If we receive a thought for a stage, ensure it's marked as running if not completed
          setStageStatus(prev => {
             if (prev[frontendStage] === 'completed') return prev;
             return { ...prev, [frontendStage]: 'running' }
          })
          
          if (!currentStep) setCurrentStep(frontendStage)

          addThought(frontendStage, {
            type: msg.thought.type,
            content: msg.thought.content,
            confidence: msg.thought.confidence
          })
        }
      }

      // 2. Handle Progress / Stage Updates
      if (msg.type === 'progress' && msg.stage) {
        const frontendStage = BACKEND_TO_FRONTEND_STAGE_MAP[msg.stage]
        if (frontendStage) {
          setCurrentStep(frontendStage)
          setStageStatus(prev => {
            // Don't revert completed stages
            if (prev[frontendStage] === 'completed') return prev
            return { ...prev, [frontendStage]: 'running' }
          })
        }
      }

      // 3. Handle Stage Completion
      if (msg.type === 'stage_complete' && msg.stage) {
        const frontendStage = BACKEND_TO_FRONTEND_STAGE_MAP[msg.stage]
        if (frontendStage) {
          setStageStatus(prev => ({ ...prev, [frontendStage]: 'completed' }))
          
          // Calculate processing time if we were tracking it
          if (startTimeRef.current) {
            const elapsed = (Date.now() - startTimeRef.current) / 1000
            setProcessingTime(prev => ({ ...prev, [frontendStage]: elapsed }))
          }
        }
        // Update parent data if provided
        if (msg.data) {
          onComplete(msg.data)
        }
      }

      // 4. Handle Full Completion
      if (msg.type === 'completed') {
        setIsLoading(false)
        setCurrentStep(null)
        onComplete({}) // Trigger refresh or final state update
        toast.success("Analysis completed successfully!")
      }

      // 5. Handle Errors
      if (msg.type === 'error') {
        console.error("Orchestrator Error:", msg.message)
        const errorMessage = msg.error || msg.message || "Unknown error occurred"
        toast.error(`Analysis Error: ${errorMessage}`)
        
        if (msg.stage) {
           const frontendStage = BACKEND_TO_FRONTEND_STAGE_MAP[msg.stage]
           if (frontendStage) {
             setStageStatus(prev => ({ ...prev, [frontendStage]: 'failed' }))
           }
        }
        setIsLoading(false)
      }
    } catch (e) {
      console.error("Failed to parse WebSocket message", e)
    }
  }, [lastMessage, currentStep, addThought, onComplete, setIsLoading])

  // Orchestrator Execution (Full Pipeline)
  const runFullPipeline = async () => {
    setIsLoading(true)
    startTimeRef.current = Date.now()
    
    // Reset statuses for a fresh run
    setStageStatus({})
    setStepThoughts({})
    
    try {
      // Resume/Start the orchestrator on the existing session
      // This endpoint now supports triggering the pipeline via background tasks
      await axios.post(`${API_URL}/api/v1/orchestrator/resume/${sessionId}`, new FormData())
      toast.info("Analysis pipeline started...")
      
    } catch (error) {
      console.error('Failed to start pipeline:', error)
      toast.error("Failed to start analysis pipeline. Please try again.")
      setIsLoading(false)
      setStageStatus(prev => ({ ...prev, [currentStep || 'unknown']: 'failed' }))
    }
  }

  // Legacy/Manual Stage Execution
  const runStage = async (stageId: string) => {
    setCurrentStep(stageId)
    setStageStatus(prev => ({ ...prev, [stageId]: 'running' }))
    setIsLoading(true)

    try {
      let endpoint = ''
      let body = {}

      switch (stageId) {
        case 'menu_ingestion':
          // Usually handled by upload, but maybe re-extract?
          await new Promise(r => setTimeout(r, 1000)) 
          break
        case 'competitor_scout':
          endpoint = `/api/v1/analyze/competitors?session_id=${sessionId}`
          break
        case 'visual_sentiment':
          endpoint = `/api/v1/analyze/sentiment?session_id=${sessionId}`
          break
        case 'strategic_analysis':
          endpoint = `/api/v1/analyze/bcg?session_id=${sessionId}`
          break
        case 'predictive_model':
          endpoint = `/api/v1/predict/sales?session_id=${sessionId}&horizon_days=14`
          body = []
          break
        case 'growth_actions':
          endpoint = `/api/v1/campaigns/generate?session_id=${sessionId}&num_campaigns=3`
          body = []
          break
      }

      if (endpoint) {
        const res = await axios.post(`${API_URL}${endpoint}`, body)
        if (res.data) {
           onComplete(res.data)
           setStageStatus(prev => ({ ...prev, [stageId]: 'completed' }))
           toast.success(`Stage '${stageId.replace('_', ' ')}' completed`)
        }
      } else {
         setStageStatus(prev => ({ ...prev, [stageId]: 'completed' }))
      }
      
    } catch (error) {
      console.error(`Error in stage ${stageId}:`, error)
      toast.error(`Stage execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setStageStatus(prev => ({ ...prev, [stageId]: 'failed' }))
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header Actions */}
      <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Orquestador de Análisis</h2>
          <p className="text-sm text-gray-500">RestoPilotAI Autonomous Pipeline</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={runFullPipeline}
            disabled={isLoading}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all
              ${isLoading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl hover:-translate-y-0.5'
              }
            `}
          >
            {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />}
            {isLoading ? 'Ejecutando...' : 'Iniciar Análisis Completo'}
          </button>
        </div>
      </div>

      {/* Vertical Pipeline Steps */}
      <div className="relative space-y-6 before:absolute before:inset-0 before:ml-8 before:w-0.5 before:-translate-x-1/2 before:bg-gray-200 before:h-full before:-z-10">
        {ANALYSIS_STAGES.map((stage, index) => {
          const status = stageStatus[stage.id] || 'pending'
          const isRunning = (currentStep === stage.id) || (status === 'running')
          const isCompleted = status === 'completed'
          const Icon = stage.icon

          return (
            <div key={stage.id} className="relative flex gap-6 group">
              {/* Timeline Node */}
              <div className={`
                flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center border-4 transition-all duration-500 z-10
                ${isRunning 
                  ? 'bg-white border-blue-500 text-blue-600 shadow-lg shadow-blue-200 scale-110' 
                  : isCompleted 
                    ? 'bg-green-50 border-green-500 text-green-600' 
                    : 'bg-gray-50 border-gray-200 text-gray-400'
                }
              `}>
                {isRunning ? (
                  <Loader2 className="h-8 w-8 animate-spin" />
                ) : isCompleted ? (
                  <CheckCircle className="h-8 w-8" />
                ) : (
                  <Icon className="h-7 w-7" />
                )}
              </div>

              {/* Card Content */}
              <div className={`
                flex-1 p-5 rounded-xl border transition-all duration-300 bg-white
                ${isRunning 
                  ? 'border-blue-200 shadow-lg ring-1 ring-blue-100' 
                  : 'border-gray-200 hover:border-gray-300 shadow-sm'
                }
              `}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className={`font-bold text-lg ${isRunning ? 'text-blue-900' : 'text-gray-900'}`}>
                      {stage.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
                  </div>
                  
                  {!isRunning && !isCompleted && (
                    <button 
                      onClick={() => runStage(stage.id)}
                      disabled={isLoading}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      <Play className="h-5 w-5" />
                    </button>
                  )}
                  
                  {isCompleted && (
                    <div className="flex items-center gap-1 text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">
                      <CheckCircle className="h-3 w-3" />
                      Completado
                    </div>
                  )}
                </div>

                {/* Thinking Stream Component */}
                {(isRunning || (stepThoughts[stage.id] && stepThoughts[stage.id].length > 0)) && (
                  <div className="mt-4 border-t border-gray-100 pt-4">
                    <ThinkingStream
                      thoughts={stepThoughts[stage.id] || []}
                      isActive={isRunning}
                      title={`Agente IA: ${stage.title}`}
                      showConfidence={true}
                      defaultExpanded={true}
                    />
                  </div>
                )}
                
                {/* Stats / Mini Result Preview */}
                {isCompleted && (
                  <div className="mt-3 flex gap-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" /> 
                      {processingTime[stage.id] ? `${processingTime[stage.id].toFixed(1)}s` : 'Procesado'}
                    </span>
                    <span className="flex items-center gap-1">
                      <ShieldCheck className="h-3 w-3" /> Verificado
                    </span>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
