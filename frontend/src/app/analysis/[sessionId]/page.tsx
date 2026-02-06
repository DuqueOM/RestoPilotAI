'use client';

import { DebateResult, MultiAgentDebatePanel } from '@/components/ai/MultiAgentDebatePanel';
import { QualityAssurancePanel } from '@/components/ai/QualityAssurancePanel';
import { ThoughtBubbleStream } from '@/components/ai/ThoughtBubbleStream';
import { DashboardSkeleton } from '@/components/ui/AnalysisSkeleton';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { useMarathonAgent } from '@/hooks/useMarathonAgent';
import { ArrowRight, BarChart3, CheckCircle2, Download, Loader2, MapPin, Megaphone, MessageSquare, RefreshCw, Shield, Sparkles, Star, Store, Target } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import { useSessionData } from './layout';

// Lazy load heavy components for better performance
const PipelineProgress = lazy(() => import('@/components/marathon-agent/PipelineProgress').then(mod => ({ default: mod.PipelineProgress })));
const StepTimeline = lazy(() => import('@/components/marathon-agent/StepTimeline').then(mod => ({ default: mod.StepTimeline })));

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const { sessionData, isLoading: loadingSession, refreshSession } = useSessionData();

  // Handle potential nested data structure from backend wrapper
  const unwrappedData = (sessionData as any)?.data || sessionData;
  const activeTaskId = unwrappedData?.active_task_id || unwrappedData?.marathon_agent_context?.active_task_id || sessionId;

  // Marathon Agent State
  const {
    taskState,
    isRunning,
    error: marathonError,
    cancelTask,
    recoverTask,
  } = useMarathonAgent(activeTaskId);

  // AI Transparency State
  const [showThoughtStream, setShowThoughtStream] = useState(true);
  const [debates, setDebates] = useState<DebateResult[]>([]);
  const [loadingDebates, setLoadingDebates] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<any>(null);

  // Calculate which analyses are complete
  const completedAnalyses = {
    bcg: !!(unwrappedData?.bcg_analysis?.items?.length || unwrappedData?.bcg?.items?.length),
    competitors: !!(unwrappedData?.competitor_analysis || unwrappedData?.competitors?.length || unwrappedData?.enriched_competitors?.length),
    sentiment: !!unwrappedData?.sentiment_analysis,
    campaigns: !!(
      Array.isArray(unwrappedData?.campaigns)
        ? unwrappedData.campaigns.length
        : unwrappedData?.campaigns?.campaigns?.length
    ),
  };
  
  const totalCompleted = Object.values(completedAnalyses).filter(Boolean).length;
  const progressPercentage = (totalCompleted / 4) * 100;

  // Business info from session
  const restaurantInfo = unwrappedData?.restaurant_info || {};
  const _businessContext = unwrappedData?.business_context || {};

  // Fetch debates when BCG data is available
  const fetchDebates = useCallback(async () => {
    if (!completedAnalyses.bcg || debates.length > 0) return;
    
    setLoadingDebates(true);
    try {
      const response = await fetch(`/api/v1/marathon/debates/bcg/${sessionId}?max_debates=3`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        setDebates(data.debates || []);
      }
    } catch (err) {
      console.error('Failed to fetch debates:', err instanceof Error ? err.message : err);
    } finally {
      setLoadingDebates(false);
    }
  }, [sessionId, completedAnalyses.bcg, debates.length]);

  useEffect(() => {
    if (completedAnalyses.bcg && debates.length === 0 && !loadingDebates) {
      fetchDebates();
    }
  }, [completedAnalyses.bcg, debates.length, loadingDebates, fetchDebates]);

  // Auto-refresh session data periodically while analysis is running
  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      refreshSession();
    }, 10000);
    return () => clearInterval(interval);
  }, [isRunning, refreshSession]);

  // Re-run a specific analysis section
  const _handleRerun = async (type: 'bcg' | 'competitors' | 'sentiment' | 'campaigns') => {
    try {
      const endpoints: Record<string, string> = {
        bcg: `/api/v1/analyze/bcg?session_id=${sessionId}`,
        competitors: `/api/v1/analyze/competitors?session_id=${sessionId}`,
        sentiment: `/api/v1/analyze/sentiment?session_id=${sessionId}`,
        campaigns: `/api/v1/campaigns/generate?session_id=${sessionId}`,
      };
      await fetch(endpoints[type], { method: 'POST' });
      setTimeout(() => refreshSession(), 3000);
    } catch (err) {
      console.error(`Failed to re-run ${type}:`, err);
    }
  };

  // Export session data as JSON
  const handleExport = async () => {
    try {
      const response = await fetch(`/api/v1/session/${sessionId}/export`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `restopilot-analysis-${sessionId.slice(0, 8)}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  if (loadingSession) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* Business Info Header with Background Image */}
      <div className="relative rounded-xl overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0">
          <img
            src="/images/dashboard-header.webp"
            alt=""
            className="w-full h-full object-cover"
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-blue-900/90 via-blue-800/85 to-purple-900/90" />
        </div>
        
        <div className="relative p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Store className="h-6 w-6" />
                {restaurantInfo.name || 'My Restaurant'}
              </h1>
              {restaurantInfo.location && (
                <p className="text-blue-100 text-sm mt-1 flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {restaurantInfo.location}
                </p>
              )}
              {restaurantInfo.rating && (
                <p className="text-blue-100 text-sm mt-1 flex items-center gap-1">
                  <Star className="h-4 w-4 text-yellow-300" />
                  {restaurantInfo.rating} ({restaurantInfo.user_ratings_total || 0} reviews)
                </p>
              )}
            </div>
            <div className="text-right">
              {isRunning ? (
                <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span className="font-medium">Analyzing...</span>
                </div>
              ) : totalCompleted === 4 ? (
                <div className="flex items-center gap-2 bg-green-500/30 backdrop-blur-sm px-4 py-2 rounded-lg">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="font-medium">Analysis Complete</span>
                </div>
              ) : (
                <div className="text-blue-200 text-sm">
                  {totalCompleted}/4 analyses completed
                </div>
              )}
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Analysis Progress</span>
              <span>{totalCompleted}/4</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-3">
              <div 
                className={`rounded-full h-3 transition-all duration-500 ${isRunning ? 'bg-yellow-300 animate-pulse' : 'bg-white'}`}
                style={{ width: `${Math.max(progressPercentage, isRunning ? 10 : 0)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* AI Thought Stream - Shows during active analysis */}
      {(showThoughtStream || isRunning) && activeTaskId && (
        <ThoughtBubbleStream
          taskId={activeTaskId}
          sessionId={sessionId}
          onComplete={() => {
            setShowThoughtStream(false);
            refreshSession();
          }}
          onError={(error) => {
            console.error('Thought stream error:', error);
            setShowThoughtStream(false);
          }}
        />
      )}

      {/* Pipeline Progress - Shows when task is running */}
      {taskState && (
        <Suspense fallback={
          <div className="flex items-center justify-center py-6">
            <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        }>
          <PipelineProgress
            taskState={taskState}
            onCancel={cancelTask}
            onRecover={() => recoverTask(taskState.task_id)}
          />
          <StepTimeline steps={taskState.steps} />
        </Suspense>
      )}

      {/* Quick Actions Bar */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          onClick={handleExport}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
        >
          <Download className="h-4 w-4" />
          Export Report
        </button>
        <button
          onClick={() => refreshSession()}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Data
        </button>
        {totalCompleted >= 1 && (
          <button
            onClick={async () => {
              setVerifying(true);
              try {
                const res = await fetch('/api/v1/grounding/verify', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    claim: `${restaurantInfo.name || 'This restaurant'} analysis is accurate based on current market data`,
                    context: `Restaurant at ${restaurantInfo.location || 'unknown location'}, session ${sessionId}`,
                  }),
                });
                if (res.ok) {
                  const data = await res.json();
                  setVerificationResult(data);
                }
              } catch (err) {
                console.warn('Grounding verification failed:', err);
              } finally {
                setVerifying(false);
              }
            }}
            disabled={verifying}
            className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors disabled:opacity-50"
          >
            {verifying ? <Loader2 className="h-4 w-4 animate-spin" /> : <Shield className="h-4 w-4" />}
            {verifying ? 'Verifying...' : verificationResult ? 'Verified ✓' : 'Verify with Sources'}
          </button>
        )}
        {totalCompleted >= 2 && (
          <button
            onClick={() => router.push(`/analysis/${sessionId}/campaigns`)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 border border-purple-200 rounded-lg text-sm font-medium text-purple-700 hover:bg-purple-100 transition-colors ml-auto"
          >
            <Sparkles className="h-4 w-4" />
            Creative Studio
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {/* Summary Sections - Show inline summaries of each analysis */}
      <div className="space-y-4">
        {/* BCG Summary */}
        <SummarySection
          title="BCG Matrix"
          icon={<BarChart3 className="w-5 h-5" />}
          completed={completedAnalyses.bcg}
          isRunning={isRunning}
        >
          {completedAnalyses.bcg ? (
            <BCGSummaryInline data={unwrappedData?.bcg_analysis || unwrappedData?.bcg} />
          ) : (
            <p className="text-sm text-gray-500">{isRunning ? 'Processing menu and BCG classification...' : 'Upload your menu and sales data to get BCG classification.'}</p>
          )}
        </SummarySection>

        {/* Competitors Summary */}
        <SummarySection
          title="Competitors"
          icon={<Target className="w-5 h-5" />}
          completed={completedAnalyses.competitors}
          isRunning={isRunning}
        >
          {completedAnalyses.competitors ? (
            <CompetitorsSummaryInline data={unwrappedData} />
          ) : (
            <p className="text-sm text-gray-500">{isRunning ? 'Analyzing nearby competitors...' : 'Competitor analysis will run automatically.'}</p>
          )}
        </SummarySection>

        {/* Sentiment Summary */}
        <SummarySection
          title="Sentiment"
          icon={<MessageSquare className="w-5 h-5" />}
          completed={completedAnalyses.sentiment}
          isRunning={isRunning}
        >
          {completedAnalyses.sentiment ? (
            <SentimentSummaryInline data={unwrappedData?.sentiment_analysis} />
          ) : (
            <p className="text-sm text-gray-500">{isRunning ? 'Analyzing reviews and sentiment...' : 'Sentiment analysis will run automatically.'}</p>
          )}
        </SummarySection>

        {/* Campaigns Summary */}
        <SummarySection
          title="Campaigns"
          icon={<Megaphone className="w-5 h-5" />}
          completed={completedAnalyses.campaigns}
          isRunning={isRunning}
        >
          {completedAnalyses.campaigns ? (
            <CampaignsSummaryInline data={unwrappedData?.campaigns} />
          ) : (
            <p className="text-sm text-gray-500">{isRunning ? 'Generating marketing campaigns...' : 'Campaigns will be generated after analysis.'}</p>
          )}
        </SummarySection>
      </div>

      {/* Multi-Agent Debates */}
      {debates.length > 0 && (
        <MultiAgentDebatePanel
          debates={debates}
          expanded={true}
          maxDebatesShown={3}
        />
      )}
      {loadingDebates && (
        <div className="flex items-center justify-center py-8 bg-indigo-50 rounded-lg border border-indigo-100">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-600 mr-2" />
          <span className="text-indigo-700">Generating AI agent debates...</span>
        </div>
      )}

      {/* Errors */}
      {marathonError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-900">Error</p>
          <p className="text-sm text-red-700">{marathonError}</p>
        </div>
      )}

      {/* Quality Assurance Panel */}
      {totalCompleted > 0 && (
        <QualityAssurancePanel
          sessionId={sessionId}
          section="overview"
          currentScore={0.78}
        />
      )}

      {/* What's Next CTA */}
      {totalCompleted > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            What's Next?
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {!completedAnalyses.bcg && (
              <WhatsNextCard
                title="Upload Menu Data"
                description="Add your menu for BCG Matrix analysis"
                action={() => router.push('/')}
                icon={<BarChart3 className="h-5 w-5 text-yellow-600" />}
              />
            )}
            {completedAnalyses.bcg && (
              <WhatsNextCard
                title="Explore BCG Matrix"
                description={`${(unwrappedData?.bcg_analysis?.items || unwrappedData?.bcg?.items || []).length} items classified`}
                action={() => router.push(`/analysis/${sessionId}/bcg`)}
                icon={<BarChart3 className="h-5 w-5 text-yellow-600" />}
              />
            )}
            {completedAnalyses.competitors && (
              <WhatsNextCard
                title="Review Competitors"
                description="See how you stack up against nearby rivals"
                action={() => router.push(`/analysis/${sessionId}/competitors`)}
                icon={<Target className="h-5 w-5 text-blue-600" />}
              />
            )}
            {completedAnalyses.campaigns && (
              <WhatsNextCard
                title="Launch a Campaign"
                description="AI-generated marketing campaigns ready to go"
                action={() => router.push(`/analysis/${sessionId}/campaigns`)}
                icon={<Megaphone className="h-5 w-5 text-purple-600" />}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function WhatsNextCard({ title, description, action, icon }: {
  title: string; description: string; action: () => void; icon: React.ReactNode;
}) {
  return (
    <button
      onClick={action}
      className="rp-card-interactive text-left p-4 flex items-start gap-3"
    >
      <div className="p-2 bg-white rounded-lg border shadow-sm flex-shrink-0">{icon}</div>
      <div>
        <p className="font-medium text-gray-900 text-sm">{title}</p>
        <p className="text-xs text-gray-500 mt-0.5">{description}</p>
      </div>
      <ArrowRight className="h-4 w-4 text-gray-400 ml-auto mt-1 flex-shrink-0" />
    </button>
  );
}

function SummarySection({ 
  title, icon, completed, isRunning, children 
}: { 
  title: string; 
  icon: React.ReactNode; 
  completed: boolean;
  isRunning: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className={`rounded-xl border p-5 transition-all ${
      completed ? 'border-green-200 bg-green-50/50' : 
      isRunning ? 'border-yellow-200 bg-yellow-50/30' : 
      'border-gray-200 bg-white'
    }`}>
      <div className="flex items-center gap-3 mb-3">
        <div className={completed ? 'text-green-600' : isRunning ? 'text-yellow-600' : 'text-gray-400'}>
          {icon}
        </div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <div className="ml-auto">
          {completed ? (
            <StatusBadge status="completed" size="sm" />
          ) : isRunning ? (
            <StatusBadge status="running" label="Analyzing..." size="sm" />
          ) : (
            <StatusBadge status="pending" size="sm" />
          )}
        </div>
      </div>
      {children}
    </div>
  );
}

// Inline summary components with actual data
function BCGSummaryInline({ data }: { data: any }) {
  if (!data) return null;
  const items = data.items || [];
  const stars = items.filter((i: any) => i.category_label === 'star' || i.category_label === 'Star').length;
  const plowhorses = items.filter((i: any) => i.category_label === 'plowhorse' || i.category_label === 'Plowhorse' || i.category_label === 'cash_cow').length;
  const puzzles = items.filter((i: any) => i.category_label === 'puzzle' || i.category_label === 'Puzzle' || i.category_label === 'question_mark').length;
  const dogs = items.filter((i: any) => i.category_label === 'dog' || i.category_label === 'Dog').length;
  
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-4 gap-2 text-sm">
        <div className="text-center p-2 bg-yellow-50 rounded-lg">
          <div className="text-lg font-bold text-yellow-700">{stars}</div>
          <div className="text-xs text-gray-600">Stars</div>
        </div>
        <div className="text-center p-2 bg-green-50 rounded-lg">
          <div className="text-lg font-bold text-green-700">{plowhorses}</div>
          <div className="text-xs text-gray-600">Plowhorses</div>
        </div>
        <div className="text-center p-2 bg-blue-50 rounded-lg">
          <div className="text-lg font-bold text-blue-700">{puzzles}</div>
          <div className="text-xs text-gray-600">Puzzles</div>
        </div>
        <div className="text-center p-2 bg-red-50 rounded-lg">
          <div className="text-lg font-bold text-red-700">{dogs}</div>
          <div className="text-xs text-gray-600">Dogs</div>
        </div>
      </div>
      <p className="text-sm text-gray-600">{items.length} products analyzed. Go to BCG Matrix tab for details.</p>
    </div>
  );
}

function CompetitorsSummaryInline({ data }: { data: any }) {
  const competitors = data?.competitor_analysis?.competitors || data?.enriched_competitors || data?.competitors || [];
  if (!competitors.length) return <p className="text-sm text-gray-500">No competitor data.</p>;
  
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {competitors.slice(0, 5).map((c: any, i: number) => (
          <div key={i} className="flex items-center gap-2 bg-white rounded-lg px-3 py-1.5 border text-sm">
            <span className="font-medium text-gray-900">{c.name}</span>
            {c.rating && (
              <span className="flex items-center gap-0.5 text-yellow-600 text-xs">
                <Star className="h-3 w-3" /> {c.rating}
              </span>
            )}
          </div>
        ))}
        {competitors.length > 5 && (
          <span className="text-sm text-gray-500 self-center">+{competitors.length - 5} more</span>
        )}
      </div>
      <p className="text-sm text-gray-600">{competitors.length} competitors identified. Go to Competitors tab for details.</p>
    </div>
  );
}

function SentimentSummaryInline({ data }: { data: any }) {
  if (!data) return null;
  
  return (
    <div className="space-y-2">
      {data.overall && (
        <div className="flex items-center gap-4">
          <div className={`text-2xl font-bold ${
            data.overall.score >= 0.7 ? 'text-green-600' :
            data.overall.score >= 0.5 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {(data.overall.score * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600">
            <p className="font-medium">{data.overall.label || 'Overall Sentiment'}</p>
            <p>{data.sources?.reduce((sum: number, s: any) => sum + s.count, 0) || 0} reviews analyzed</p>
          </div>
        </div>
      )}
      <p className="text-sm text-gray-600">Go to Sentiment tab for full details.</p>
    </div>
  );
}

function CampaignsSummaryInline({ data }: { data: any }) {
  const campaigns = Array.isArray(data) ? data : data?.campaigns;
  if (!campaigns?.length) return null;
  
  return (
    <div className="space-y-2">
      <div className="space-y-1">
        {campaigns.slice(0, 3).map((c: any, i: number) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            <span className="text-purple-500">→</span>
            <span className="font-medium text-gray-900">{c.title || c.name}</span>
          </div>
        ))}
        {campaigns.length > 3 && (
          <p className="text-xs text-gray-500">+{campaigns.length - 3} more campaigns</p>
        )}
      </div>
      <p className="text-sm text-gray-600">{campaigns.length} campaigns generated. Go to Campaigns tab for details.</p>
    </div>
  );
}
