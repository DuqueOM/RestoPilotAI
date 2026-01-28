'use client';

import { api } from '@/lib/api';
import { Brain, Sparkles, Target } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';


interface OverviewPageProps {
  params: { sessionId: string };
}

export default function OverviewPage({ params }: OverviewPageProps) {
  const router = useRouter();
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = params.sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(params.sessionId);
        setSession(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load session');
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [params.sessionId]);

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 text-lg mb-2">⚠️ Error</div>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  const bcgData = session?.bcg_analysis || session?.bcg;
  const predictions = session?.predictions;
  const campaigns = session?.campaigns;
  const marathonContext = session?.marathon_agent_context;

  return (
    <div className="space-y-6">
      {/* Executive Summary Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white">
        <h2 className="text-xl font-bold mb-2">Executive Summary</h2>
        <p className="text-blue-100 text-sm">
          Complete analysis of {bcgData?.summary?.total_items || session?.menu?.items?.length || 0} products • 
          Portfolio Health: {((bcgData?.summary?.portfolio_health_score || 0) * 100).toFixed(0)}%
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
          <p className="text-xs text-amber-600 uppercase tracking-wide">Stars</p>
          <p className="text-2xl font-bold text-amber-900">
            {bcgData?.summary?.counts?.star || 0}
          </p>
          <p className="text-xs text-amber-600">High growth</p>
        </div>
        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
          <p className="text-xs text-emerald-600 uppercase tracking-wide">Cash Cows</p>
          <p className="text-2xl font-bold text-emerald-900">
            {bcgData?.summary?.counts?.cash_cow || 0}
          </p>
          <p className="text-xs text-emerald-600">Stable revenue</p>
        </div>
        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-4 border border-indigo-200">
          <p className="text-xs text-indigo-600 uppercase tracking-wide">Question Marks</p>
          <p className="text-2xl font-bold text-indigo-900">
            {bcgData?.summary?.counts?.question_mark || 0}
          </p>
          <p className="text-xs text-indigo-600">Needs decision</p>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4 border border-red-200">
          <p className="text-xs text-red-600 uppercase tracking-wide">Dogs</p>
          <p className="text-2xl font-bold text-red-900">
            {bcgData?.summary?.counts?.dog || 0}
          </p>
          <p className="text-xs text-red-600">Review/remove</p>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
          <p className="text-xs text-blue-600 uppercase tracking-wide">14-day Forecast</p>
          <p className="text-2xl font-bold text-blue-900">
            {predictions?.scenario_totals?.baseline?.toLocaleString() || '--'}
          </p>
          <p className="text-xs text-blue-600">baseline units</p>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200">
          <p className="text-xs text-purple-600 uppercase tracking-wide">Campaigns</p>
          <p className="text-2xl font-bold text-purple-900">
            {campaigns?.length || 0}
          </p>
          <p className="text-xs text-purple-600">AI proposals</p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Priority Actions */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-500" />
            Priority Actions
          </h3>
          <div className="space-y-3">
            {bcgData?.classifications?.filter((c: any) => c.priority === 'high').slice(0, 3).map((item: any, idx: number) => (
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

        {/* Marathon Agent */}
        {marathonContext ? (
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
                <p className="text-lg font-bold text-violet-700">{marathonContext.session_count}</p>
                <p className="text-xs text-gray-500">Sessions</p>
              </div>
              <div className="bg-white/60 rounded-lg p-2 text-center">
                <p className="text-lg font-bold text-violet-700">{marathonContext.total_analyses}</p>
                <p className="text-xs text-gray-500">Analyses</p>
              </div>
              <div className="bg-white/60 rounded-lg p-2 text-center">
                <p className="text-lg font-bold text-violet-700">{marathonContext.last_interaction}</p>
                <p className="text-xs text-gray-500">Last</p>
              </div>
            </div>
            <div className="space-y-1">
              {marathonContext.long_term_insights?.slice(0, 2).map((insight: string, idx: number) => (
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
                <p className="text-xs text-gray-500">Long-term memory</p>
              </div>
            </div>
            <p className="text-sm text-gray-500">Memory context builds with more analysis sessions.</p>
          </div>
        )}
      </div>

      {/* Quick Insights */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-blue-500" />
          Key Insights (All Sources)
        </h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
            <p className="text-xs text-amber-600 font-medium mb-1">BCG Matrix</p>
            <p className="text-sm text-gray-700">
              {bcgData?.ai_insights?.portfolio_assessment?.slice(0, 100) || 
               `Portfolio ${bcgData?.summary?.is_balanced ? 'is balanced' : 'needs attention'}`}
            </p>
          </div>
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
            <p className="text-xs text-blue-600 font-medium mb-1">Predictions</p>
            <p className="text-sm text-gray-700">
              {predictions?.insights?.[0]?.slice(0, 100) || 
               'Run predictions to get future sales insights'}
            </p>
          </div>
          <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
            <p className="text-xs text-purple-600 font-medium mb-1">Campaigns</p>
            <p className="text-sm text-gray-700">
              {campaigns?.[0]?.rationale?.slice(0, 100) || 
               'Generate campaigns to get marketing recommendations'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-24 bg-blue-100 rounded-xl"></div>
      <div className="grid grid-cols-6 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-xl"></div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="h-48 bg-gray-100 rounded-xl"></div>
        <div className="h-48 bg-gray-100 rounded-xl"></div>
      </div>
    </div>
  );
}
