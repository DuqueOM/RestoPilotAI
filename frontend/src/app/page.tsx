'use client'

import AnalysisPanel from '@/components/AnalysisPanel'
import BCGChart from '@/components/BCGChart'
import CampaignCards from '@/components/CampaignCards'
import FileUpload from '@/components/FileUpload'
import ThoughtSignature from '@/components/ThoughtSignature'
import { api } from '@/lib/api'
import { BarChart3, ChefHat, Megaphone, Sparkles, TrendingUp, Upload } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

type Step = 'upload' | 'analysis' | 'results'

export default function Home() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState<Step>('upload')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionData, setSessionData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [thoughtSignature, setThoughtSignature] = useState<any>(null)
  const [demoLoading, setDemoLoading] = useState(false)

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
          <div className="space-y-8">
            {/* Thought Signature */}
            {thoughtSignature && (
              <ThoughtSignature signature={thoughtSignature} />
            )}

            {/* BCG Analysis */}
            {sessionData.bcg_analysis && (
              <div className="card">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-primary-500" />
                  BCG Matrix Analysis
                </h2>
                <BCGChart data={sessionData.bcg_analysis} />
              </div>
            )}

            {/* Predictions */}
            {sessionData.predictions && (
              <div className="card">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary-500" />
                  Sales Predictions
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(sessionData.predictions.scenario_totals || {}).map(([name, total]: [string, any]) => (
                    <div key={name} className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-500 capitalize">{name.replace('_', ' ')}</p>
                      <p className="text-2xl font-bold text-gray-900">{total} units</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Campaigns */}
            {sessionData.campaigns && sessionData.campaigns.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Megaphone className="h-5 w-5 text-primary-500" />
                  Generated Campaign Proposals
                </h2>
                <CampaignCards campaigns={sessionData.campaigns} />
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
