'use client'

import AgentDashboard from '@/components/analysis/AgentDashboard'
import AnalysisPanel from '@/components/analysis/AnalysisPanel'
import BCGResultsPanel from '@/components/analysis/BCGMatrix'
import CampaignCards from '@/components/analysis/Campaigns'
import CompetitorDashboard from '@/components/analysis/CompetitorDashboard'
import FeedbackSummary from '@/components/analysis/FeedbackSummary'
import SentimentDashboard from '@/components/analysis/SentimentDashboard'
import AIChat from '@/components/common/AIChat'
import ThoughtSignature from '@/components/common/ThoughtSignature'
import FileUpload from '@/components/setup/FileUpload'
import LocationPicker from '@/components/setup/LocationInput'
import { api } from '@/lib/api'
import axios from 'axios'
import { ArrowDown, ArrowRight, BarChart3, Brain, Calendar, ChefHat, ClipboardCheck, Cpu, Download, Loader2, Megaphone, MessageSquare, Play, RefreshCw, Sparkles, Target, TrendingUp, X } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Time period options for re-analysis
const TIME_PERIODS = [
  { id: '30d', label: 'Last 30 Days', description: 'Recommended for operational analysis' },
  { id: '90d', label: 'Last 90 Days', description: 'Good for identifying trends' },
  { id: '180d', label: 'Last 6 Months', description: 'Includes seasonal patterns' },
  { id: '365d', label: 'Last Year', description: 'Full annual cycle' },
  { id: 'all', label: 'All Data', description: 'Complete historical analysis' },
]

// Filter periods based on available data
function getAvailablePeriods(sessionData: any) {
  const available = sessionData?.available_periods?.available_periods || [];
  if (available.length === 0) return TIME_PERIODS;
  
  return TIME_PERIODS.filter(p => available.includes(p.id));
}

type Step = 'upload' | 'analysis' | 'results'
type ResultsTab = 'overview' | 'feedback' | 'agents' | 'bcg' | 'competitors' | 'sentiment' | 'predictions' | 'campaigns'

export default function Home() {
  const router = useRouter()
  // Steps state: Track max progress
  const [analysisStarted, setAnalysisStarted] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [canProceed, setCanProceed] = useState(false)
  
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionData, setSessionData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [thoughtSignature, setThoughtSignature] = useState<any>(null)
  const [demoLoading, setDemoLoading] = useState(false)
  const [resumeId, setResumeId] = useState('')
  const [resumeLoading, setResumeLoading] = useState(false)
  const [showResumeInput, setShowResumeInput] = useState(false)
  const [resultsTab, setResultsTab] = useState<ResultsTab>('overview')
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30d')
  const [reanalysisLoading, setReanalysisLoading] = useState(false)
  
  // Refs for scrolling
  const analysisRef = useRef<HTMLDivElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Scroll to analysis when started
  useEffect(() => {
    if (analysisStarted && analysisRef.current) {
      setTimeout(() => {
        analysisRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }, [analysisStarted])

  // Scroll to results when complete
  useEffect(() => {
    if (analysisComplete && resultsRef.current) {
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }, [analysisComplete])

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

  const handleResumeSession = async () => {
    if (!resumeId.trim()) return
    setResumeLoading(true)
    try {
      const data = await api.getSession(resumeId.trim())
      setSessionId(data.session_id)
      setSessionData(data)
      
      // Determine state based on loaded data
      const hasAnalysis = data.bcg || (data as any).bcg_analysis || data.predictions || (data as any).competitors
      if (hasAnalysis) {
        setAnalysisStarted(true)
        setAnalysisComplete(true)
      } else if (data.session_id) {
        setCanProceed(true)
      }
      
      setShowResumeInput(false)
    } catch (error) {
      console.error('Failed to resume session:', error)
      alert('Session not found or invalid.')
    } finally {
      setResumeLoading(false)
    }
  }

  const handleSessionCreated = (id: string, data: any) => {
    setSessionId(id)
    setSessionData(data)
    if (data.thought_process) {
      setThoughtSignature(data.thought_process)
    }
  }

  const startAnalysis = () => {
    setAnalysisStarted(true)
    // Loading state is managed by the AnalysisPanel when it mounts
  }

  const handleAnalysisComplete = (data: any) => {
    setSessionData((prev: any) => ({ ...prev, ...data }))
    if (data.thought_signature) {
      setThoughtSignature(data.thought_signature)
    }
    setAnalysisComplete(true)
    setIsLoading(false)
  }

  return (
    <main className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
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
            <div className="flex items-center gap-4">
               {/* Resume Session */}
              {!sessionId && (
                <div className="flex items-center">
                  {showResumeInput ? (
                    <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1 animate-in fade-in slide-in-from-right-4">
                      <input 
                        type="text" 
                        value={resumeId}
                        onChange={(e) => setResumeId(e.target.value)}
                        placeholder="Session ID..."
                        className="bg-transparent border-none text-sm w-32 focus:ring-0 px-2"
                        onKeyPress={(e) => e.key === 'Enter' && handleResumeSession()}
                      />
                      <button 
                        onClick={handleResumeSession}
                        disabled={resumeLoading}
                        className="p-1 bg-white rounded-md shadow-sm text-primary-600 hover:text-primary-700"
                      >
                        {resumeLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                      </button>
                      <button 
                        onClick={() => setShowResumeInput(false)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowResumeInput(true)}
                      className="hidden md:flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 transition-colors mr-4"
                    >
                      <RefreshCw className="h-4 w-4" />
                      Resume Session
                    </button>
                  )}
                </div>
              )}

               {/* Demo Button - Moved to Header for cleanliness */}
              {!sessionId && (
                <button
                  onClick={handleLoadDemo}
                  disabled={demoLoading}
                  className="hidden md:flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  {demoLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                  Try Demo
                </button>
              )}
              <div className="flex items-center gap-2 px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-xs font-medium border border-primary-100">
                <Sparkles className="h-3 w-3" />
                <span>Powered by Gemini 3</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Stream */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section 1: Data Upload & Context */}
        <section className={`transition-opacity duration-500 ${analysisStarted ? 'opacity-80' : 'opacity-100'}`}>
          <div className="flex items-center gap-4 mb-6">
            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 text-blue-600 font-bold text-lg">1</div>
            <h2 className="text-2xl font-bold text-gray-900">Upload Data & Context</h2>
          </div>
          
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
            <FileUpload 
              onSessionCreated={handleSessionCreated}
              onComplete={() => {}} // No-op now
              sessionId={sessionId}
              onValidationChange={setCanProceed}
            />

            {/* Location Picker - Nested here as requested */}
            {sessionId && (
              <div className="mt-8 pt-8 border-t border-gray-100">
                 <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Target className="h-5 w-5 text-red-500" />
                    Business Location
                 </h3>
                <LocationPicker
                  sessionId={sessionId}
                  onLocationSelect={(location, competitors) => {
                    console.log('Location selected:', location, competitors);
                    setSessionData((prev: any) => ({
                      ...prev,
                      location: location,
                      competitors: competitors,
                    }));
                  }}
                />
              </div>
            )}
            
            {/* Primary Action Button - Located at bottom of upload/context section */}
            <div className="mt-8 flex justify-center">
              <button 
                onClick={() => {
                  if (analysisStarted) {
                    // If already started, just scroll to it
                    analysisRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                  } else {
                    startAnalysis()
                  }
                }}
                disabled={!canProceed}
                className={`group relative px-8 py-4 text-lg font-semibold rounded-2xl transition-all flex items-center gap-3 ${
                  canProceed 
                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white shadow-lg hover:shadow-primary-500/30 transform hover:-translate-y-0.5' 
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                {analysisStarted ? (
                   <>
                    <RefreshCw className="h-5 w-5" />
                    Re-run Analysis
                    <ArrowDown className="h-5 w-5 group-hover:translate-y-1 transition-transform" />
                   </>
                ) : (
                   <>
                    <Brain className="h-5 w-5" />
                    Start AI Analysis
                    <ArrowDown className="h-5 w-5 group-hover:translate-y-1 transition-transform" />
                   </>
                )}
              </button>
            </div>
            {analysisStarted && (
                <p className="text-center text-xs text-gray-400 mt-2">
                    Scroll down to modify or re-run specific analysis steps
                </p>
            )}
          </div>
        </section>

        {/* Section 2: Active Analysis */}
        {analysisStarted && (
          <section ref={analysisRef} className="animate-in fade-in slide-in-from-bottom-10 duration-700">
             <div className="flex items-center gap-4 mb-6">
                <div className={`h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-lg transition-colors ${
                    analysisComplete && !isLoading ? 'bg-green-100 text-green-600' : 'bg-purple-100 text-purple-600 animate-pulse'
                }`}>
                    {analysisComplete && !isLoading ? '✓' : '2'}
                </div>
                <h2 className="text-2xl font-bold text-gray-900">
                    {analysisComplete && !isLoading ? 'Analysis Results Ready' : 'AI Reasoning & Processing'}
                </h2>
             </div>

             <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8 min-h-[400px]">
                {sessionId && (
                    <AnalysisPanel 
                        sessionId={sessionId}
                        sessionData={sessionData}
                        onComplete={handleAnalysisComplete}
                        isLoading={isLoading}
                        setIsLoading={setIsLoading}
                    />
                )}
             </div>
          </section>
        )}

        {/* Section 3: Results Dashboard */}
        {analysisComplete && sessionData && (
          <section ref={resultsRef} className="animate-in fade-in slide-in-from-bottom-10 duration-700">
            <div className="flex items-center gap-4 mb-6">
                <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 text-emerald-600 font-bold text-lg">3</div>
                <h2 className="text-2xl font-bold text-gray-900">Strategic Results</h2>
            </div>

            <div className="space-y-6">
            {/* Results Tabs + Export Button */}
            <div className="flex items-center gap-4 sticky top-20 z-40 bg-gray-50/95 backdrop-blur py-2">
              <div className="bg-white rounded-xl border border-gray-200 p-1 flex gap-1 overflow-x-auto flex-1 shadow-sm">
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
              
              <a
                href={`${API_URL}/api/v1/session/${sessionId}/export?format=json`}
                download
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors text-sm font-medium whitespace-nowrap shadow-sm"
                title="Download all analysis data as JSON"
              >
                <Download className="h-4 w-4" />
                Export
              </a>
            </div>

            {/* Results Content Area */}
            <div className="min-h-[600px]">
                {/* Overview Tab - Executive Dashboard */}
                {resultsTab === 'overview' && (
                  <div className="space-y-6 animate-in fade-in duration-500">
                    {/* Thought Signature */}
                    {thoughtSignature && (
                      <ThoughtSignature signature={thoughtSignature} />
                    )}

                    {/* Period Selector for Overview */}
                    {sessionData.bcg_analysis && getAvailablePeriods(sessionData).length > 1 && (
                      <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-primary-500" />
                            <h4 className="text-sm font-semibold text-gray-900">Analysis Period</h4>
                          </div>
                          {reanalysisLoading && (
                            <span className="text-xs text-primary-600 flex items-center gap-1">
                              <Loader2 className="h-3 w-3 animate-spin" />
                              Updating...
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {getAvailablePeriods(sessionData).map((period) => (
                            <button
                              key={period.id}
                              onClick={() => rerunBCGAnalysis(period.id)}
                              disabled={reanalysisLoading}
                              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                                selectedPeriod === period.id
                                  ? 'bg-primary-500 text-white'
                                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                              } disabled:opacity-50`}
                            >
                              {period.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Executive Summary Header */}
                    <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white shadow-lg">
                      <h2 className="text-xl font-bold mb-2">Executive Summary</h2>
                      <p className="text-primary-100 text-sm mb-3">
                        Completed analysis for <span className="font-semibold text-white">{sessionData.location?.address || 'Restaurant'}</span>
                      </p>
                      
                      {/* Key High-Level Stats */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                        <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-primary-100 text-xs">Total Revenue (Period)</p>
                          <p className="text-2xl font-bold">${sessionData.bcg_analysis?.total_revenue?.toLocaleString() || '0'}</p>
                        </div>
                        <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-primary-100 text-xs">Menu Items</p>
                          <p className="text-2xl font-bold">{sessionData.bcg_analysis?.total_items || 0}</p>
                        </div>
                        <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-primary-100 text-xs">Star Products</p>
                          <p className="text-2xl font-bold">{sessionData.bcg_analysis?.summary?.stars_count || 0}</p>
                        </div>
                        <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-primary-100 text-xs">Competitors Analyzed</p>
                          <p className="text-2xl font-bold">{sessionData.competitors?.length || 0}</p>
                        </div>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Strategic Actions Card */}
                      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                          <Target className="h-5 w-5 text-red-500" />
                          Recommended Actions
                        </h3>
                        {sessionData.bcg_analysis?.ai_insights?.priority_actions ? (
                          <ul className="space-y-3">
                            {sessionData.bcg_analysis.ai_insights.priority_actions.map((action: string, idx: number) => (
                              <li key={idx} className="flex items-start gap-3 text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-bold">
                                  {idx + 1}
                                </span>
                                {action}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-500 text-sm">Run BCG analysis to see actions</p>
                        )}
                      </div>

                      {/* Marathon Agent Context - Long Term Memory */}
                      {sessionData.marathon_agent_context ? (
                        <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl p-5 border border-violet-200 shadow-sm">
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
                        <div className="bg-gray-50 rounded-xl p-5 border border-gray-200 shadow-sm">
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
                    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
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

                {/* Competitors Tab */}
                {resultsTab === 'competitors' && (
                  <CompetitorDashboard 
                    insights={sessionData.competitors || []} 
                    analysis={sessionData.competitor_analysis} 
                  />
                )}

                {/* Sentiment Tab */}
                {resultsTab === 'sentiment' && (
                  <SentimentDashboard 
                    analysis={sessionData.sentiment_analysis} 
                  />
                )}

                {/* BCG Tab */}
                {resultsTab === 'bcg' && sessionData.bcg_analysis && (
                  <div className="space-y-4 animate-in fade-in duration-500">
                    {/* Time Period Selector */}
                    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
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
                        {getAvailablePeriods(sessionData).map((period) => (
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

                {/* Predictions Tab */}
                {resultsTab === 'predictions' && (
                  <div className="text-center py-12 text-gray-500">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No hay predicciones disponibles para esta sesión.</p>
                    <p className="text-sm mt-2">Las predicciones requieren datos históricos de ventas.</p>
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
        </div>
      </section>
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
