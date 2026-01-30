'use client';

import {
    AlertTriangle,
    ArrowRight,
    Brain,
    CheckCircle,
    DollarSign,
    Lightbulb,
    Loader2,
    RefreshCw,
    Star,
    Target,
    TrendingDown,
    TrendingUp,
    Users
} from 'lucide-react';
import { useEffect, useState } from 'react';

interface FeedbackSummaryProps {
  sessionId: string;
  sessionData: any;
}

interface AIFeedback {
  overall_score: number;
  health_status: 'excellent' | 'good' | 'needs_attention' | 'critical';
  key_strengths: string[];
  areas_for_improvement: string[];
  immediate_actions: Array<{
    action: string;
    impact: 'high' | 'medium' | 'low';
    effort: 'easy' | 'moderate' | 'complex';
  }>;
  revenue_opportunities: Array<{
    description: string;
    potential: string;
  }>;
  competitive_position: string;
  ai_recommendation: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function FeedbackSummary({ sessionId, sessionData }: FeedbackSummaryProps) {
  const [feedback, setFeedback] = useState<AIFeedback | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateFeedback = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);

      const response = await fetch(`${API_BASE}/api/v1/analyze/feedback`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed to generate feedback');

      const data = await response.json();
      setFeedback(data);
    } catch (err) {
      console.error('Feedback error:', err);
      setError('Could not generate feedback. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/session/${sessionId}/export?format=json`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `menupilot_report_${sessionId.substring(0, 8)}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      // Optional: show toast or alert
    }
  };

  const handlePrint = () => {
    window.print();
  };

  useEffect(() => {
    if (sessionId && !feedback) {
      generateFeedback();
    }
  }, [sessionId]);

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'from-emerald-500 to-green-600';
      case 'good': return 'from-blue-500 to-indigo-600';
      case 'needs_attention': return 'from-yellow-500 to-orange-600';
      case 'critical': return 'from-red-500 to-rose-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'excellent': return <Star className="w-6 h-6" />;
      case 'good': return <CheckCircle className="w-6 h-6" />;
      case 'needs_attention': return <AlertTriangle className="w-6 h-6" />;
      case 'critical': return <AlertTriangle className="w-6 h-6" />;
      default: return <Brain className="w-6 h-6" />;
    }
  };

  const getImpactBadge = (impact: string) => {
    switch (impact) {
      case 'high': return 'bg-green-100 text-green-700 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-gray-100 text-gray-700 border-gray-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getEffortBadge = (effort: string) => {
    switch (effort) {
      case 'easy': return 'bg-emerald-100 text-emerald-700';
      case 'moderate': return 'bg-blue-100 text-blue-700';
      case 'complex': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="flex flex-col items-center justify-center">
          <div className="relative">
            <Brain className="w-16 h-16 text-primary-200" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
            </div>
          </div>
          <p className="mt-4 text-gray-600 font-medium">Analyzing your restaurant...</p>
          <p className="text-sm text-gray-500">AI is generating personalized feedback</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-gray-700 font-medium">{error}</p>
          <button
            onClick={generateFeedback}
            className="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!feedback) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="text-center">
          <Brain className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Click to generate AI feedback</p>
          <button
            onClick={generateFeedback}
            className="mt-4 px-6 py-3 bg-gradient-to-r from-primary-500 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all"
          >
            Generate Feedback
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <div className={`bg-gradient-to-r ${getHealthColor(feedback.health_status)} rounded-xl p-6 text-white`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-xl">
              {getHealthIcon(feedback.health_status)}
            </div>
            <div>
              <h2 className="text-2xl font-bold">Business Health Score</h2>
              <p className="text-white/80 capitalize">{feedback.health_status.replace('_', ' ')}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold">{feedback.overall_score}</div>
            <div className="text-white/80">/100</div>
          </div>
        </div>

        {/* AI Recommendation */}
        <div className="mt-6 p-4 bg-white/10 rounded-lg backdrop-blur-sm">
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <p className="text-sm">{feedback.ai_recommendation}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={generateFeedback}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Analysis
          </button>
          
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm text-white transition-colors"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm text-white transition-colors"
          >
            <Printer className="w-4 h-4" />
            Print Report
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Strengths */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-emerald-500" />
            Key Strengths
          </h3>
          <div className="space-y-2">
            {feedback.key_strengths.map((strength, idx) => (
              <div key={idx} className="flex items-start gap-2 p-2 bg-emerald-50 rounded-lg">
                <TrendingUp className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-gray-700">{strength}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Areas for Improvement */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-orange-500" />
            Areas for Improvement
          </h3>
          <div className="space-y-2">
            {feedback.areas_for_improvement.map((area, idx) => (
              <div key={idx} className="flex items-start gap-2 p-2 bg-orange-50 rounded-lg">
                <TrendingDown className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-gray-700">{area}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Immediate Actions */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
          <ArrowRight className="w-5 h-5 text-primary-500" />
          Recommended Actions
        </h3>
        <div className="space-y-3">
          {feedback.immediate_actions.map((action, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">
                  {idx + 1}
                </div>
                <span className="text-sm text-gray-700">{action.action}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs rounded-full border ${getImpactBadge(action.impact)}`}>
                  {action.impact} impact
                </span>
                <span className={`px-2 py-1 text-xs rounded-full ${getEffortBadge(action.effort)}`}>
                  {action.effort}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Revenue Opportunities */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
          <DollarSign className="w-5 h-5 text-green-500" />
          Revenue Opportunities
        </h3>
        <div className="grid md:grid-cols-2 gap-3">
          {feedback.revenue_opportunities.map((opp, idx) => (
            <div key={idx} className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
              <p className="text-sm text-gray-700">{opp.description}</p>
              <p className="mt-2 text-lg font-bold text-green-600">{opp.potential}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Competitive Position */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-200 p-5">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-3">
          <Users className="w-5 h-5 text-indigo-500" />
          Competitive Position
        </h3>
        <p className="text-gray-700">{feedback.competitive_position}</p>
      </div>
    </div>
  );
}
