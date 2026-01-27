'use client'

import axios from 'axios'
import { BarChart3, CheckCircle, Loader2, Megaphone, Play, TrendingUp } from 'lucide-react'
import { useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AnalysisPanelProps {
  sessionId: string
  onComplete: (data: any) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function AnalysisPanel({ sessionId, onComplete, isLoading, setIsLoading }: AnalysisPanelProps) {
  const [bcgDone, setBcgDone] = useState(false)
  const [predictionsDone, setPredictionsDone] = useState(false)
  const [campaignsDone, setCampaignsDone] = useState(false)
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [results, setResults] = useState<any>({})

  const runBCGAnalysis = async () => {
    setCurrentStep('bcg')
    setIsLoading(true)
    try {
      const res = await axios.post(`${API_URL}/api/v1/analyze/bcg?session_id=${sessionId}`)
      setResults((prev: any) => ({ ...prev, bcg_analysis: res.data }))
      setBcgDone(true)
    } catch (err: any) {
      alert(`BCG Analysis failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const runPredictions = async () => {
    setCurrentStep('predictions')
    setIsLoading(true)
    try {
      const res = await axios.post(`${API_URL}/api/v1/predict/sales?session_id=${sessionId}&horizon_days=14`)
      setResults((prev: any) => ({ ...prev, predictions: res.data }))
      setPredictionsDone(true)
    } catch (err: any) {
      alert(`Predictions failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsLoading(false)
      setCurrentStep(null)
    }
  }

  const generateCampaigns = async () => {
    setCurrentStep('campaigns')
    setIsLoading(true)
    try {
      const res = await axios.post(`${API_URL}/api/v1/campaigns/generate?session_id=${sessionId}&num_campaigns=3`)
      setResults((prev: any) => ({ ...prev, campaigns: res.data.campaigns, thought_signature: res.data.thought_signature }))
      setCampaignsDone(true)
    } catch (err: any) {
      alert(`Campaign generation failed: ${err.response?.data?.detail || err.message}`)
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

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Run Analysis</h2>
        <p className="text-gray-600 mt-2">Execute BCG classification, sales prediction, and campaign generation.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* BCG Analysis */}
        <div className="card">
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
            onClick={runBCGAnalysis}
            disabled={isLoading || bcgDone}
            className={`w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
              bcgDone ? 'bg-green-100 text-green-700' : 'btn-primary'
            }`}
          >
            {currentStep === 'bcg' ? <Loader2 className="h-4 w-4 animate-spin" /> : bcgDone ? 'Completed' : 'Run BCG'}
          </button>
        </div>

        {/* Predictions */}
        <div className="card">
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
            onClick={runPredictions}
            disabled={isLoading || predictionsDone || !bcgDone}
            className={`w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
              predictionsDone ? 'bg-green-100 text-green-700' : !bcgDone ? 'bg-gray-200 text-gray-500' : 'btn-primary'
            }`}
          >
            {currentStep === 'predictions' ? <Loader2 className="h-4 w-4 animate-spin" /> : predictionsDone ? 'Completed' : 'Run Predictions'}
          </button>
        </div>

        {/* Campaigns */}
        <div className="card">
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
            onClick={generateCampaigns}
            disabled={isLoading || campaignsDone || !bcgDone}
            className={`w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
              campaignsDone ? 'bg-green-100 text-green-700' : !bcgDone ? 'bg-gray-200 text-gray-500' : 'btn-primary'
            }`}
          >
            {currentStep === 'campaigns' ? <Loader2 className="h-4 w-4 animate-spin" /> : campaignsDone ? 'Completed' : 'Generate'}
          </button>
        </div>
      </div>

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
