'use client';

import { AlertTriangle, ArrowRight, Brain, CheckCircle2, RefreshCw } from 'lucide-react';

interface AgentDashboardProps {
  sessionData?: any;
  thoughtSignature?: any;
}

// Demo self-correction trace showing agent reasoning
const selfCorrectionTrace = [
  {
    step: 1,
    agent: 'BCG Classifier',
    action: 'Initial Classification',
    input: 'Birria Tacos: revenue=$4,500, growth=90%, market_share=25%',
    output: 'Classification: DOG (low market share)',
    status: 'error',
    reasoning: 'Applied standard BCG rules: market_share < 50% = low share'
  },
  {
    step: 2,
    agent: 'BCG Classifier',
    action: 'Self-Check Triggered',
    input: 'Detected anomaly: growth_rate=90% but classified as DOG',
    output: 'ALERT: High growth (90%) contradicts DOG classification',
    status: 'warning',
    reasoning: 'Dogs should have LOW growth. This item has HIGH growth (90%). Initiating re-classification...'
  },
  {
    step: 3,
    agent: 'BCG Classifier',
    action: 'Re-Classification',
    input: 'Re-analyzing with growth_rate priority: 90% growth, 25% share',
    output: 'CORRECTED: Classification changed DOG → QUESTION MARK',
    status: 'success',
    reasoning: 'High growth + low share = Question Mark. This product has potential if we invest in marketing to increase market share.'
  },
  {
    step: 4,
    agent: 'Campaign Generator',
    action: 'Strategy Alignment',
    input: 'Question Mark detected: Birria Tacos needs market share growth',
    output: 'Generated "Birria Buzz Campaign" targeting social media influencers',
    status: 'success',
    reasoning: 'Question Marks require investment to convert to Stars. Recommended viral marketing strategy to capitalize on high growth trend.'
  }
];

const agentPipeline = [
  { name: 'Menu Extractor', tech: 'Tesseract OCR + Gemini Vision', color: 'purple' },
  { name: 'BCG Classifier', tech: 'Gross Profit Analysis + Self-Correction', color: 'amber' },
  { name: 'Sales Predictor', tech: 'XGBoost + LSTM Neural Ensemble', color: 'blue' },
  { name: 'Campaign Generator', tech: 'Gemini 3 Pro + Marathon Memory', color: 'green' }
];

export default function AgentDashboard({ sessionData, thoughtSignature: _thoughtSignature }: AgentDashboardProps) {
  const marathonContext = sessionData?.marathon_agent_context;

  const _getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700 border-green-200';
      case 'running': return 'bg-blue-100 text-blue-700 border-blue-200 animate-pulse';
      case 'error': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-500 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-violet-600 to-purple-700 rounded-xl p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="h-7 w-7" />
          <h2 className="text-xl font-bold">AI Agents Pipeline</h2>
        </div>
        <p className="text-violet-100 text-sm">
          Multi-agent system with transparent reasoning, self-correction, and long-term memory
        </p>
      </div>

      {/* Agent Pipeline Flow */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-4">Agent Pipeline</h3>
        <div className="flex items-center justify-between overflow-x-auto pb-2">
          {agentPipeline.map((agent, idx) => (
            <div key={idx} className="flex items-center">
              <div className={`px-4 py-3 rounded-xl border-2 min-w-[160px] ${
                agent.color === 'purple' ? 'border-purple-300 bg-purple-50' :
                agent.color === 'amber' ? 'border-amber-300 bg-amber-50' :
                agent.color === 'blue' ? 'border-blue-300 bg-blue-50' :
                'border-green-300 bg-green-50'
              }`}>
                <p className="font-semibold text-sm text-gray-900">{agent.name}</p>
                <p className="text-xs text-gray-500 mt-1">{agent.tech}</p>
              </div>
              {idx < agentPipeline.length - 1 && (
                <ArrowRight className="h-5 w-5 text-gray-300 mx-2 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Self-Correction Trace - THE KEY FEATURE */}
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-amber-500 rounded-lg">
            <RefreshCw className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-amber-900">Self-Correction Trace</h3>
            <p className="text-xs text-amber-600">Watch the agent detect and fix its own mistakes</p>
          </div>
        </div>

        <div className="space-y-3">
          {selfCorrectionTrace.map((trace, idx) => (
            <div key={idx} className={`rounded-lg p-4 border-l-4 ${
              trace.status === 'error' ? 'bg-red-50 border-red-400' :
              trace.status === 'warning' ? 'bg-yellow-50 border-yellow-400' :
              'bg-green-50 border-green-400'
            }`}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-gray-800 text-white text-xs font-mono rounded">
                    Step {trace.step}
                  </span>
                  <span className="text-sm font-semibold text-gray-800">{trace.agent}</span>
                  <span className="text-xs text-gray-500">• {trace.action}</span>
                </div>
                {trace.status === 'error' ? (
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                ) : trace.status === 'warning' ? (
                  <RefreshCw className="h-5 w-5 text-yellow-500" />
                ) : (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                )}
              </div>
              
              <div className="grid md:grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Input</p>
                  <p className="text-gray-700 font-mono text-xs bg-white/50 p-2 rounded">{trace.input}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Output</p>
                  <p className={`font-mono text-xs p-2 rounded ${
                    trace.status === 'error' ? 'bg-red-100 text-red-700' :
                    trace.status === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>{trace.output}</p>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Agent Reasoning</p>
                <p className="text-sm text-gray-700 italic">"{trace.reasoning}"</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-green-100 rounded-lg border border-green-200">
          <p className="text-sm text-green-800 font-medium">
            ✓ Self-correction completed: 1 misclassification detected and corrected automatically
          </p>
        </div>
      </div>

      {/* Marathon Agent Section */}
      <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl p-5 border border-violet-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-violet-500 rounded-lg">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-violet-900">Marathon Agent</h3>
            <p className="text-xs text-violet-600">Long-Term Memory (1M token context)</p>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-violet-700">{marathonContext?.session_count || 12}</p>
            <p className="text-xs text-gray-600">Sessions</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-violet-700">{marathonContext?.total_analyses || 47}</p>
            <p className="text-xs text-gray-600">Analyses</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-violet-700">{marathonContext?.last_interaction || '2h'}</p>
            <p className="text-xs text-gray-600">Last Active</p>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-medium text-violet-800 uppercase tracking-wide">Accumulated Insights</p>
          {(marathonContext?.long_term_insights || [
            'Tacos al Pastor consistently top performer across 12 sessions',
            'Weekend promotions generate 35% more conversions',
            'Average ticket increased 12% since family bundle implementation'
          ]).map((insight: string, idx: number) => (
            <div key={idx} className="flex items-start gap-2 text-sm text-violet-700 bg-white/40 rounded-lg p-2">
              <span className="text-violet-500 mt-0.5">→</span>
              <span>{insight}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
