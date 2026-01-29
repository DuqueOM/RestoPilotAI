'use client'

import AgentDashboard from '@/components/AgentDashboard'
import AIChat from '@/components/AIChat'
import AnalysisPanel from '@/components/AnalysisPanel'
import BCGResultsPanel from '@/components/BCGResultsPanel'
import CampaignCards from '@/components/CampaignCards'
import CompetitorDashboard from '@/components/CompetitorDashboard'
import FeedbackSummary from '@/components/FeedbackSummary'
import FileUpload from '@/components/FileUpload'
import LocationPicker from '@/components/LocationPicker'
import SentimentDashboard from '@/components/SentimentDashboard'
import ThoughtSignature from '@/components/ThoughtSignature'
import { api } from '@/lib/api'
import axios from 'axios'
import { BarChart3, Brain, Calendar, ChefHat, ClipboardCheck, Cpu, Download, Loader2, Megaphone, MessageSquare, Play, Sparkles, Target, TrendingUp, Upload } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Time period options for re-analysis
const TIME_PERIODS = [
  { id: '30d', label: 'Last 30 Days', description: 'Recommended for operational analysis' },
  { id: '90d', label: 'Last 90 Days', description: 'Good for identifying trends' },
  { id: '180d', label: 'Last 6 Months', description: 'Includes seasonal patterns' },
  { id: '365d', label: 'Last Year', description: 'Full annual cycle' },
  { id: 'all', label: 'All Data', description: 'Complete historical analysis' },
]

type Step = 'upload' | 'analysis' | 'results'
type ResultsTab = 'overview' | 'feedback' | 'agents' | 'bcg' | 'competitors' | 'sentiment' | 'predictions' | 'campaigns'

export default function Home() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState<Step>('upload')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionData, setSessionData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [thoughtSignature, setThoughtSignature] = useState<any>(null)
  const [demoLoading, setDemoLoading] = useState(false)
  const [resultsTab, setResultsTab] = useState<ResultsTab>('overview')
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30d')
  const [reanalysisLoading, setReanalysisLoading] = useState(false)

  // Re-run BCG analysis with a different time period
  const rerunBCGAnalysis = async (period: string) => {
    if (!sessionId) return
    setReanalysisLoading(true)
    setSelectedPeriod(period)
    try {
      const res = await axios.post(
        `${API_URL}/api/v1/analyze/bcg?session_id=${sessionId}&period=${period}`,
        {},
        { timeout: 0 }
      )
      setSessionData((prev: any) => ({ ...prev, bcg_analysis: res.data }))
    } catch (err: any) {
      console.error('Re-analysis failed:', err)
      alert(`Re-analysis failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setReanalysisLoading(false)
    }
  }

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

            {/* Location Picker */}
            {sessionId && (
              <LocationPicker
                onLocationSelect={(location, competitors) => {
                  console.log('Location selected:', location, competitors);
                  // Store location and competitors in session data
                  setSessionData((prev: any) => ({
                    ...prev,
                    location: location,
                    competitors: competitors,
                  }));
                }}
              />
            )}
            
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
            {/* Results Tabs + Export Button */}
            <div className="flex items-center gap-4">
              <div className="bg-white rounded-xl border border-gray-200 p-1 flex gap-1 overflow-x-auto flex-1">
                {[
                  { id: 'overview', label: 'Overview', icon: Sparkles },
                  { id: 'feedback', label: 'AI Feedback', icon: ClipboardCheck },
                  { id: 'agents', label: 'AI Agents', icon: Cpu },
                  { id: 'bcg', label: 'BCG Matrix', icon: BarChart3 },
                  { id: 'competitors', label: 'Competitors', icon: Target },
                  { id: 'sentiment', label: 'Sentiment', icon: MessageSquare },
                  { id: 'predictions', label: 'Predictions', icon: TrendingUp },
                  { id: 'campaigns', label: 'Campaigns', icon: Megaphone },
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
              
              {/* Export Button */}
              <a
                href={`${API_URL}/api/v1/session/${sessionId}/export?format=json`}
                download
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors text-sm font-medium whitespace-nowrap"
                title="Download all analysis data as JSON"
              >
                <Download className="h-4 w-4" />
                Export Results
              </a>
            </div>

            {/* Overview Tab - Executive Dashboard */}
            {resultsTab === 'overview' && (
              <div className="space-y-6">
                {/* Thought Signature */}
                {thoughtSignature && (
                  <ThoughtSignature signature={thoughtSignature} />
                )}

                {/* Executive Summary Header */}
                <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white">
                  <h2 className="text-xl font-bold mb-2">Executive Summary</h2>
                  <p className="text-primary-100 text-sm">
                    Complete analysis of {sessionData.bcg_analysis?.summary?.total_items || 0} products • 
                    Portfolio Health: {((sessionData.bcg_analysis?.summary?.portfolio_health_score || 0) * 100).toFixed(0)}%
                  </p>
                </div>

                {/* Key Metrics Grid - Summary of ALL tabs */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  {/* BCG Summary */}
                  <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
                    <p className="text-xs text-amber-600 uppercase tracking-wide">Stars</p>
                    <p className="text-2xl font-bold text-amber-900">
                      {sessionData.bcg_analysis?.summary?.counts?.star || 0}
                    </p>
                    <p className="text-xs text-amber-600">High growth</p>
                  </div>
                  <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
                    <p className="text-xs text-emerald-600 uppercase tracking-wide">Cash Cows</p>
                    <p className="text-2xl font-bold text-emerald-900">
                      {sessionData.bcg_analysis?.summary?.counts?.cash_cow || 0}
                    </p>
                    <p className="text-xs text-emerald-600">Stable revenue</p>
                  </div>
                  <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-4 border border-indigo-200">
                    <p className="text-xs text-indigo-600 uppercase tracking-wide">Question Marks</p>
                    <p className="text-2xl font-bold text-indigo-900">
                      {sessionData.bcg_analysis?.summary?.counts?.question_mark || 0}
                    </p>
                    <p className="text-xs text-indigo-600">Needs decision</p>
                  </div>
                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4 border border-red-200">
                    <p className="text-xs text-red-600 uppercase tracking-wide">Dogs</p>
                    <p className="text-2xl font-bold text-red-900">
                      {sessionData.bcg_analysis?.summary?.counts?.dog || 0}
                    </p>
                    <p className="text-xs text-red-600">Review/remove</p>
                  </div>
                  {/* Predictions Summary */}
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
                    <p className="text-xs text-blue-600 uppercase tracking-wide">14-day Forecast</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {sessionData.predictions?.scenario_totals?.baseline?.toLocaleString() || '--'}
                    </p>
                    <p className="text-xs text-blue-600">baseline units</p>
                  </div>
                  {/* Campaigns Summary */}
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200">
                    <p className="text-xs text-purple-600 uppercase tracking-wide">Campaigns</p>
                    <p className="text-2xl font-bold text-purple-900">
                      {sessionData.campaigns?.length || 0}
                    </p>
                    <p className="text-xs text-purple-600">AI proposals</p>
                  </div>
                </div>

                {/* Two Column Layout: Top Actions + Marathon Agent */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Top Priority Actions */}
                  <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Target className="h-5 w-5 text-primary-500" />
                      Priority Actions
                    </h3>
                    <div className="space-y-3">
                      {sessionData.bcg_analysis?.classifications?.filter((c: any) => c.priority === 'high').slice(0, 3).map((item: any, idx: number) => (
                        <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            item.bcg_class === 'star' ? 'bg-amber-100 text-amber-700' :
                            item.bcg_class === 'question_mark' ? 'bg-indigo-100 text-indigo-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>{item.bcg_label}</span>
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{item.name}</p>
                            <p className="text-xs text-gray-500 mt-1">{item.strategy?.summary?.slice(0, 80)}...</p>
                          </div>
                        </div>
                      )) || <p className="text-gray-500 text-sm">Run BCG analysis to see actions</p>}
                    </div>
                  </div>

                  {/* Marathon Agent Context - Long Term Memory */}
                  {sessionData.marathon_agent_context ? (
                    <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl p-5 border border-violet-200">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-violet-500 rounded-lg">
                          <Brain className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-violet-900">Marathon Agent</h3>
                          <p className="text-xs text-violet-600">Long-Term Memory (1M tokens)</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-2 mb-3">
                        <div className="bg-white/60 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-violet-700">{sessionData.marathon_agent_context.session_count}</p>
                          <p className="text-xs text-gray-500">Sessions</p>
                        </div>
                        <div className="bg-white/60 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-violet-700">{sessionData.marathon_agent_context.total_analyses}</p>
                          <p className="text-xs text-gray-500">Analyses</p>
                        </div>
                        <div className="bg-white/60 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-violet-700">{sessionData.marathon_agent_context.last_interaction}</p>
                          <p className="text-xs text-gray-500">Last</p>
                        </div>
                      </div>
                      <div className="space-y-1">
                        {sessionData.marathon_agent_context.long_term_insights?.slice(0, 2).map((insight: string, idx: number) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-violet-700 bg-white/40 rounded p-2">
                            <span className="text-violet-500">→</span>
                            {insight}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-xl p-5 border border-gray-200">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-gray-400 rounded-lg">
                          <Brain className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-700">Marathon Agent</h3>
                          <p className="text-xs text-gray-500">Long-term memory not available</p>
                        </div>
                      </div>
                      <p className="text-sm text-gray-500">Memory context builds with more analysis sessions.</p>
                    </div>
                  )}
                </div>

                {/* Quick Insights from All Sources */}
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary-500" />
                    Key Insights (All Sources)
                  </h3>
                  <div className="grid md:grid-cols-3 gap-4">
                    {/* BCG Insight */}
                    <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                      <p className="text-xs text-amber-600 font-medium mb-1">BCG Matrix</p>
                      <p className="text-sm text-gray-700">
                        {sessionData.bcg_analysis?.ai_insights?.portfolio_assessment?.slice(0, 100) || 
                         `Portfolio ${sessionData.bcg_analysis?.summary?.is_balanced ? 'is balanced' : 'needs attention'}`}...
                      </p>
                    </div>
                    {/* Predictions Insight */}
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-xs text-blue-600 font-medium mb-1">Predictions</p>
                      <p className="text-sm text-gray-700">
                        {sessionData.predictions?.insights?.[0]?.slice(0, 100) || 
                         'Run predictions to get future sales insights'}...
                      </p>
                    </div>
                    {/* Campaign Insight */}
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
                      <p className="text-xs text-purple-600 font-medium mb-1">Campaigns</p>
                      <p className="text-sm text-gray-700">
                        {sessionData.campaigns?.[0]?.rationale?.slice(0, 100) || 
                         'Generate campaigns to get marketing recommendations'}...
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Feedback Tab */}
            {resultsTab === 'feedback' && sessionId && (
              <FeedbackSummary sessionId={sessionId} sessionData={sessionData} />
            )}

            {/* Agents Tab */}
            {resultsTab === 'agents' && (
              <AgentDashboard />
            )}

            {/* BCG Tab */}
            {resultsTab === 'bcg' && sessionData.bcg_analysis && (
              <div className="space-y-4">
                {/* Time Period Selector */}
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-5 w-5 text-primary-500" />
                      <h3 className="font-semibold text-gray-900">Analysis Period</h3>
                    </div>
                    {reanalysisLoading && (
                      <div className="flex items-center gap-2 text-primary-600">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Re-analyzing...</span>
                      </div>
                    )}
                  </div>
                  
                  {/* Current Period Info */}
                  {sessionData.bcg_analysis.date_range && (
                    <div className="mb-3 p-2 bg-blue-50 rounded-lg text-sm text-blue-700">
                      <span className="font-medium">Current data: </span>
                      {sessionData.bcg_analysis.date_range.start} → {sessionData.bcg_analysis.date_range.end}
                      {sessionData.bcg_analysis.total_records && (
                        <span className="ml-2">({sessionData.bcg_analysis.total_records.toLocaleString()} records)</span>
                      )}
                    </div>
                  )}
                  
                  {/* Period Buttons */}
                  <div className="flex flex-wrap gap-2">
                    {TIME_PERIODS.map((period) => (
                      <button
                        key={period.id}
                        onClick={() => rerunBCGAnalysis(period.id)}
                        disabled={reanalysisLoading}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                          selectedPeriod === period.id
                            ? 'bg-primary-500 text-white shadow-sm'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        <span className="flex items-center gap-1">
                          {period.label}
                          {selectedPeriod === period.id && reanalysisLoading && (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          )}
                        </span>
                      </button>
                    ))}
                  </div>
                  
                  {/* Period Description */}
                  <p className="mt-2 text-xs text-gray-500">
                    {TIME_PERIODS.find(p => p.id === selectedPeriod)?.description}
                    {' • '}Menu Engineering recommends 30-90 days for operational decisions.
                  </p>
                </div>
                
                {/* BCG Results */}
                <BCGResultsPanel data={sessionData.bcg_analysis} />
              </div>
            )}

            {/* Competitors Tab */}
            {resultsTab === 'competitors' && (
              <CompetitorDashboard 
                analysis={sessionData?.competitorAnalysis}
                insights={sessionData?.competitors?.map((c: any, idx: number) => ({
                  competitorName: c.name,
                  priceComparison: 'similar' as const,
                  avgPriceDifference: 0,
                  uniqueItems: [],
                  recommendations: [],
                  confidenceScore: 0.7,
                  itemCount: 0,
                  priceRange: { min: 0, max: 0 },
                  rating: c.rating,
                  address: c.address,
                  distance: c.distance,
                }))}
              />
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

      {/* AI Chat - Always visible, even without session */}
      <AIChat 
        sessionId={sessionId || 'general'} 
        context={sessionId ? resultsTab : 'onboarding'}
        title="MenuPilot AI"
        placeholder={sessionId ? "Ask about your restaurant analysis..." : "Ask questions about MenuPilot..."}
      />

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
