'use client';

import { TaskMonitor } from '@/components/marathon-agent/TaskMonitor';
import { WebSocketIndicator } from '@/components/shared/WebSocketIndicator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AutoVerifyToggle } from '@/components/vibe-engineering/AutoVerifyToggle';
import { VerificationPanel } from '@/components/vibe-engineering/VerificationPanel';
import { useVibeEngineering } from '@/hooks/useVibeEngineering';
import { api } from '@/lib/api';
import { Brain, Sparkles, Target } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { use, useEffect, useState } from 'react';

interface OverviewPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function OverviewPage({ params }: OverviewPageProps) {
  const { sessionId } = use(params);
  const router = useRouter();
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [autoVerify, setAutoVerify] = useState(true);
  const [autoImprove, setAutoImprove] = useState(true);
  const [qualityThreshold, setQualityThreshold] = useState(0.85);
  const [maxIterations, setMaxIterations] = useState(3);

  // Vibe Engineering Hook
  const { 
    state: vibeState, 
    isVerifying: isVibeVerifying, 
    startVerification 
  } = useVibeEngineering(sessionId);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(sessionId);
        setSession(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load session');
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [sessionId]);

  // Auto-start verification when session is loaded if enabled
  useEffect(() => {
    if (session && autoVerify && !vibeState && !isVibeVerifying) {
      // Small delay to ensure UI is ready and prevent potential race conditions
      const timer = setTimeout(() => {
        startVerification(sessionId, 'bcg_classification', {
          auto_verify: autoVerify,
          auto_improve: autoImprove,
          quality_threshold: qualityThreshold,
          max_iterations: maxIterations
        });
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [session, autoVerify, autoImprove, qualityThreshold, maxIterations, vibeState, isVibeVerifying, startVerification, sessionId]);

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

  // Handle potential nested data structure from backend wrapper
  const sessionData = session?.data || session;
  
  const bcgData = sessionData?.bcg_analysis || sessionData?.bcg;
  const predictions = sessionData?.predictions;
  const campaigns = sessionData?.campaigns;
  const marathonContext = sessionData?.marathon_agent_context;
  const activeTaskId = sessionData?.active_task_id || marathonContext?.active_task_id;

  return (
    <div className="space-y-6">
      {/* Header with Status Indicators */}
      <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">Analysis Overview</h1>
          <WebSocketIndicator sessionId={sessionId} />
        </div>
        <div className="flex items-center space-x-4">
          <AutoVerifyToggle 
            autoVerify={autoVerify}
            autoImprove={autoImprove}
            qualityThreshold={qualityThreshold}
            maxIterations={maxIterations}
            onAutoVerifyChange={setAutoVerify}
            onAutoImproveChange={setAutoImprove}
            onQualityThresholdChange={setQualityThreshold}
            onMaxIterationsChange={setMaxIterations}
            disabled={isVibeVerifying}
          />
        </div>
      </div>

      {/* Executive Summary Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white shadow-md">
        <h2 className="text-xl font-bold mb-2">Executive Summary</h2>
        <p className="text-blue-100 text-sm mb-3">
          Complete analysis of {bcgData?.summary?.total_items || session?.menu?.items?.length || 0} products • 
          Portfolio Health: {((bcgData?.summary?.portfolio_health_score || 0) * 100).toFixed(0)}%
        </p>
        {bcgData?.summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div>
              <p className="text-blue-200">Total Revenue</p>
              <p className="font-semibold text-lg">
                ${(bcgData.summary.total_revenue || 0).toLocaleString('es-CO', {maximumFractionDigits: 0})}
              </p>
            </div>
            <div>
              <p className="text-blue-200">Total Units</p>
              <p className="font-semibold text-lg">
                {(bcgData.summary.total_units || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-blue-200">Profit Margin</p>
              <p className="font-semibold text-lg">
                {(bcgData.summary.profit_margin_pct || 0).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-blue-200">Food Cost</p>
              <p className="font-semibold text-lg">
                {(bcgData.summary.food_cost_pct || 0).toFixed(1)}%
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Active Task Monitor (Marathon Agent) */}
      {activeTaskId && (
        <div className="w-full">
          <TaskMonitor taskId={activeTaskId} />
        </div>
      )}

      {/* Main Grid: Key Metrics & Priority Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Metrics & Insights */}
        <div className="lg:col-span-2 space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
              <p className="text-xs text-amber-600 uppercase tracking-wide font-semibold">Stars</p>
              <p className="text-2xl font-bold text-amber-900 mt-1">
                {bcgData?.summary?.counts?.star || 0}
              </p>
              <p className="text-xs text-amber-600 mt-1">High growth</p>
            </div>
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
              <p className="text-xs text-emerald-600 uppercase tracking-wide font-semibold">Cash Cows</p>
              <p className="text-2xl font-bold text-emerald-900 mt-1">
                {bcgData?.summary?.counts?.cash_cow || 0}
              </p>
              <p className="text-xs text-emerald-600 mt-1">Stable revenue</p>
            </div>
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-4 border border-indigo-200">
              <p className="text-xs text-indigo-600 uppercase tracking-wide font-semibold">Questions</p>
              <p className="text-2xl font-bold text-indigo-900 mt-1">
                {bcgData?.summary?.counts?.question_mark || 0}
              </p>
              <p className="text-xs text-indigo-600 mt-1">Needs decision</p>
            </div>
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4 border border-red-200">
              <p className="text-xs text-red-600 uppercase tracking-wide font-semibold">Dogs</p>
              <p className="text-2xl font-bold text-red-900 mt-1">
                {bcgData?.summary?.counts?.dog || 0}
              </p>
              <p className="text-xs text-red-600 mt-1">Review/remove</p>
            </div>
          </div>

          {/* Verification Panel (Vibe Engineering) */}
          <VerificationPanel state={vibeState} isVerifying={isVibeVerifying} />

          {/* Priority Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-lg">
                <Target className="h-5 w-5 text-blue-500 mr-2" />
                Priority Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {bcgData?.classifications?.filter((c: any) => c.priority === 'high').slice(0, 3).map((item: any, idx: number) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors">
                    <span className={`px-2 py-1 text-xs font-medium rounded shrink-0 ${
                      item.bcg_class === 'star' ? 'bg-amber-100 text-amber-700' :
                      item.bcg_class === 'question_mark' ? 'bg-indigo-100 text-indigo-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>{item.bcg_label}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{item.name}</p>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">{item.strategy?.summary}</p>
                    </div>
                  </div>
                )) || <p className="text-gray-500 text-sm">Run BCG analysis to see actions</p>}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Agents & Context */}
        <div className="space-y-6">
          {/* Marathon Agent Context (if not monitored above) */}
          <Card className="bg-gradient-to-b from-violet-50 to-white border-violet-200">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-violet-500 rounded-lg shadow-sm">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-violet-900">Marathon Memory</h3>
                  <p className="text-xs text-violet-600">Long-term context window</p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {marathonContext ? (
                <>
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <div className="bg-white rounded-lg p-2 text-center border border-violet-100">
                      <p className="text-lg font-bold text-violet-700">{marathonContext.session_count}</p>
                      <p className="text-xs text-gray-500">Sessions</p>
                    </div>
                    <div className="bg-white rounded-lg p-2 text-center border border-violet-100">
                      <p className="text-lg font-bold text-violet-700">{marathonContext.total_analyses}</p>
                      <p className="text-xs text-gray-500">Analyses</p>
                    </div>
                    <div className="bg-white rounded-lg p-2 text-center border border-violet-100">
                      <p className="text-lg font-bold text-violet-700">{marathonContext.last_interaction}</p>
                      <p className="text-xs text-gray-500">Last</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-violet-800 uppercase">Latest Insights</p>
                    {marathonContext.long_term_insights?.slice(0, 3).map((insight: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-gray-700 bg-white p-2 rounded border border-violet-100">
                        <span className="text-violet-500 mt-0.5">●</span>
                        {insight}
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">Memory context builds with more analysis sessions.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-lg">
                <Sparkles className="h-5 w-5 text-amber-500 mr-2" />
                Quick Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                <p className="text-xs text-amber-600 font-medium mb-1 uppercase">Portfolio Balance</p>
                <p className="text-sm text-gray-700">
                  {bcgData?.ai_insights?.portfolio_assessment?.slice(0, 100) || 
                   `Portfolio ${bcgData?.summary?.is_balanced ? 'is balanced' : 'needs attention'}`}
                </p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                <p className="text-xs text-blue-600 font-medium mb-1 uppercase">Sales Forecast</p>
                <p className="text-sm text-gray-700">
                  {predictions?.insights?.[0]?.slice(0, 100) || 
                   'Run predictions to get future sales insights'}
                </p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
                <p className="text-xs text-purple-600 font-medium mb-1 uppercase">Marketing Opportunity</p>
                <p className="text-sm text-gray-700">
                  {campaigns?.[0]?.rationale?.slice(0, 100) || 
                   'Generate campaigns to get marketing recommendations'}
                </p>
              </div>
            </CardContent>
          </Card>
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
