'use client'

import AgentDashboard from '@/components/AgentDashboard'
import AnalysisPanel from '@/components/AnalysisPanel'
import BCGChart from '@/components/BCGChart'
import BCGResultsPanel from '@/components/BCGResultsPanel'
import CampaignCards from '@/components/CampaignCards'
import CompetitorDashboard from '@/components/CompetitorDashboard'
import FileUpload from '@/components/FileUpload'
import SentimentDashboard from '@/components/SentimentDashboard'
import ThoughtSignature from '@/components/ThoughtSignature'
import { api } from '@/lib/api'
import { BarChart3, Brain, ChefHat, Cpu, Megaphone, MessageSquare, Play, Sparkles, Target, TrendingUp, Upload } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

type Step = 'upload' | 'analysis' | 'results'
type ResultsTab = 'overview' | 'agents' | 'bcg' | 'competitors' | 'sentiment' | 'predictions' | 'campaigns'

export default function Home() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState<Step>('upload')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionData, setSessionData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [thoughtSignature, setThoughtSignature] = useState<any>(null)
  const [demoLoading, setDemoLoading] = useState(false)
  const [resultsTab, setResultsTab] = useState<ResultsTab>('overview')

  const handleLoadDemo = async () => {
    setDemoLoading(true)
    try {
      const demoData = await api.getDemoSession()
      router.push(`/analysis/${demoData.session_id}`)
    } catch (error) {
      console.error('Failed to load demo:', error)
      alert('Failed to load demo data. Make sure the backend is running.')
    } finally {
      setDemoLoading(false)
    }
  }

  const handleSessionCreated = (id: string, data: any) => {
    setSessionId(id)
    setSessionData(data)
    if (data.thought_process) {
      setThoughtSignature(data.thought_process)
    }
  }

  const handleAnalysisComplete = (data: any) => {
    setSessionData((prev: any) => ({ ...prev, ...data }))
    if (data.thought_signature) {
      setThoughtSignature(data.thought_signature)
    }
    setCurrentStep('results')
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-500 rounded-lg">
                <ChefHat className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MenuPilot</h1>
                <p className="text-sm text-gray-500">AI-Powered Restaurant Optimization</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary-500" />
              <span className="text-sm font-medium text-gray-600">Powered by Gemini 3</span>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center gap-8">
            {[
              { id: 'upload', label: 'Upload Data', icon: Upload },
              { id: 'analysis', label: 'Analysis', icon: BarChart3 },
              { id: 'results', label: 'Results & Campaigns', icon: Megaphone }
            ].map((step, idx) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
                  currentStep === step.id 
                    ? 'bg-primary-500 text-white' 
                    : sessionData && idx < ['upload', 'analysis', 'results'].indexOf(currentStep)
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-gray-100 text-gray-500'
                }`}>
                  <step.icon className="h-4 w-4" />
                  <span className="text-sm font-medium">{step.label}</span>
                </div>
                {idx < 2 && <div className="w-12 h-0.5 bg-gray-200 mx-2" />}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {currentStep === 'upload' && (
          <div className="space-y-6">
            <FileUpload 
              onSessionCreated={handleSessionCreated}
              onComplete={() => setCurrentStep('analysis')}
              sessionId={sessionId}
            />
            
            {/* Demo Button */}
            <div className="text-center">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-gray-50 text-gray-500">or</span>
                </div>
              </div>
              
              <button
                onClick={handleLoadDemo}
                disabled={demoLoading}
                className="mt-4 inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50"
              >
                {demoLoading ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                    Loading Demo...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    Try Demo (Mexican Restaurant)
                  </>
                )}
              </button>
              <p className="mt-2 text-sm text-gray-500">
                See MenuPilot in action with pre-loaded sample data
              </p>
            </div>
          </div>
        )}

        {currentStep === 'analysis' && sessionId && (
          <AnalysisPanel 
            sessionId={sessionId}
            onComplete={handleAnalysisComplete}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        )}

        {currentStep === 'results' && sessionData && (
          <div className="space-y-6">
            {/* Results Tabs */}
            <div className="bg-white rounded-xl border border-gray-200 p-1 flex gap-1 overflow-x-auto">
              {[
                { id: 'overview', label: 'Resumen', icon: Sparkles },
                { id: 'agents', label: 'Agents', icon: Cpu },
                { id: 'bcg', label: 'BCG Matrix', icon: BarChart3 },
                { id: 'competitors', label: 'Competencia', icon: Target },
                { id: 'sentiment', label: 'Sentimiento', icon: MessageSquare },
                { id: 'predictions', label: 'Predicciones', icon: TrendingUp },
                { id: 'campaigns', label: 'Campañas', icon: Megaphone },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setResultsTab(tab.id as ResultsTab)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                    resultsTab === tab.id
                      ? 'bg-primary-500 text-white shadow-sm'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Overview Tab */}
            {resultsTab === 'overview' && (
              <div className="space-y-6">
                {/* Thought Signature */}
                {thoughtSignature && (
                  <ThoughtSignature signature={thoughtSignature} />
                )}

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
                    <p className="text-sm text-amber-700">Stars</p>
                    <p className="text-2xl font-bold text-amber-900">
                      {sessionData.bcg_analysis?.summary?.counts?.star || 0}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
                    <p className="text-sm text-emerald-700">Cash Cows</p>
                    <p className="text-2xl font-bold text-emerald-900">
                      {sessionData.bcg_analysis?.summary?.counts?.cash_cow || 0}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-4 border border-indigo-200">
                    <p className="text-sm text-indigo-700">Question Marks</p>
                    <p className="text-2xl font-bold text-indigo-900">
                      {sessionData.bcg_analysis?.summary?.counts?.question_mark || 0}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4 border border-red-200">
                    <p className="text-sm text-red-700">Dogs</p>
                    <p className="text-2xl font-bold text-red-900">
                      {sessionData.bcg_analysis?.summary?.counts?.dog || 0}
                    </p>
                  </div>
                </div>

                {/* Marathon Agent Context - Long Term Memory */}
                {sessionData.marathon_agent_context && (
                  <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl p-5 border border-violet-200">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-violet-500 rounded-lg">
                        <Brain className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-violet-900">Marathon Agent - Memoria de Largo Plazo</h3>
                        <p className="text-xs text-violet-600">Gemini 3 Context Window: 1M tokens</p>
                      </div>
                    </div>
                    <div className="grid md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-white/60 rounded-lg p-3">
                        <p className="text-xs text-gray-500">Sesiones Analizadas</p>
                        <p className="text-xl font-bold text-violet-700">{sessionData.marathon_agent_context.session_count}</p>
                      </div>
                      <div className="bg-white/60 rounded-lg p-3">
                        <p className="text-xs text-gray-500">Análisis Totales</p>
                        <p className="text-xl font-bold text-violet-700">{sessionData.marathon_agent_context.total_analyses}</p>
                      </div>
                      <div className="bg-white/60 rounded-lg p-3">
                        <p className="text-xs text-gray-500">Última Interacción</p>
                        <p className="text-xl font-bold text-violet-700">{sessionData.marathon_agent_context.last_interaction}</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-violet-800">Insights de Largo Plazo:</p>
                      {sessionData.marathon_agent_context.long_term_insights?.map((insight: string, idx: number) => (
                        <div key={idx} className="flex items-start gap-2 text-sm text-violet-700 bg-white/40 rounded-lg p-2">
                          <span className="text-violet-500">→</span>
                          {insight}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* BCG Mini Chart */}
                {sessionData.bcg_analysis && (
                  <div className="card">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-primary-500" />
                      BCG Matrix Overview
                    </h2>
                    <BCGChart data={sessionData.bcg_analysis} />
                  </div>
                )}
              </div>
            )}

            {/* Agents Tab */}
            {resultsTab === 'agents' && (
              <AgentDashboard />
            )}

            {/* BCG Tab */}
            {resultsTab === 'bcg' && sessionData.bcg_analysis && (
              <BCGResultsPanel data={sessionData.bcg_analysis} />
            )}

            {/* Competitors Tab */}
            {resultsTab === 'competitors' && (
              <CompetitorDashboard />
            )}

            {/* Sentiment Tab */}
            {resultsTab === 'sentiment' && (
              <SentimentDashboard />
            )}

            {/* Predictions Tab */}
            {resultsTab === 'predictions' && (
              <div className="space-y-6">
                {sessionData.predictions ? (
                  <>
                    {/* Model Info */}
                    <div className="bg-white rounded-xl border border-gray-200 p-4">
                      <h3 className="font-semibold text-gray-900 mb-3">Información del Modelo</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">Modelo Principal</p>
                          <p className="font-medium">{sessionData.predictions.model_info?.primary || 'XGBoost'}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Ensemble</p>
                          <p className="font-medium">{sessionData.predictions.model_info?.ensemble || 'LSTM'}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">MAPE</p>
                          <p className="font-medium">{sessionData.predictions.metrics?.mape?.toFixed(1) || '--'}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">R²</p>
                          <p className="font-medium">{sessionData.predictions.metrics?.r2?.toFixed(2) || '--'}</p>
                        </div>
                      </div>
                    </div>

                    {/* Scenario Comparison */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {Object.entries(sessionData.predictions.scenario_totals || {}).map(([name, total]: [string, any]) => (
                        <div key={name} className={`rounded-xl p-5 border ${
                          name === 'with_promotion' 
                            ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200' 
                            : name === 'baseline'
                              ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200'
                              : 'bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200'
                        }`}>
                          <p className="text-sm text-gray-600 capitalize mb-1">{name.replace(/_/g, ' ')}</p>
                          <p className="text-3xl font-bold text-gray-900">{total.toLocaleString()}</p>
                          <p className="text-xs text-gray-500 mt-1">unidades en {sessionData.predictions.horizon_days || 14} días</p>
                        </div>
                      ))}
                    </div>

                    {/* Item Predictions */}
                    {sessionData.predictions.item_predictions && (
                      <div className="bg-white rounded-xl border border-gray-200 p-4">
                        <h3 className="font-semibold text-gray-900 mb-4">Predicciones por Producto</h3>
                        <div className="space-y-3">
                          {sessionData.predictions.item_predictions.map((item: any, idx: number) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                              <div>
                                <p className="font-medium text-gray-900">{item.name}</p>
                                <p className="text-xs text-gray-500">
                                  Tendencia: {item.trend} | Estacionalidad: {item.seasonality}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="text-lg font-bold text-primary-600">{item.baseline?.total?.toLocaleString()}</p>
                                <p className="text-xs text-green-600">
                                  +{((item.with_promotion?.total / item.baseline?.total - 1) * 100).toFixed(0)}% con promoción
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Insights */}
                    {sessionData.predictions.insights && (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
                        <h3 className="font-semibold text-blue-900 mb-3">Insights de Predicción</h3>
                        <ul className="space-y-2">
                          {sessionData.predictions.insights.map((insight: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                              <TrendingUp className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                              {insight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No hay predicciones disponibles para esta sesión.</p>
                    <p className="text-sm mt-2">Las predicciones requieren datos históricos de ventas.</p>
                  </div>
                )}
              </div>
            )}

            {/* Campaigns Tab */}
            {resultsTab === 'campaigns' && (
              <div>
                {sessionData.campaigns && sessionData.campaigns.length > 0 ? (
                  <>
                    <div className="mb-4 flex items-center justify-between">
                      <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Megaphone className="h-5 w-5 text-primary-500" />
                        Propuestas de Campaña Generadas
                      </h2>
                      <span className="text-sm text-gray-500">
                        {sessionData.campaigns.length} campañas
                      </span>
                    </div>
                    <CampaignCards campaigns={sessionData.campaigns} />
                  </>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Megaphone className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No hay campañas generadas para esta sesión.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            MenuPilot - Built for Gemini 3 Hackathon | Multimodal AI for Restaurant Optimization
          </p>
        </div>
      </footer>
    </main>
  )
}
