'use client';

import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useMarathonAgent } from '@/hooks/useMarathonAgent';
import { useVibeEngineering } from '@/hooks/useVibeEngineering';
import { BarChart3, CheckCircle2, Clock, Loader2, Megaphone, MessageSquare, PlayCircle, Target } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { lazy, Suspense, useState } from 'react';
import { useSessionData } from './layout';

// Lazy load heavy components for better performance
const VerificationPanel = lazy(() => import('@/components/vibe-engineering/VerificationPanel').then(mod => ({ default: mod.VerificationPanel })));
const CheckpointViewer = lazy(() => import('@/components/marathon-agent/CheckpointViewer').then(mod => ({ default: mod.CheckpointViewer })));
const PipelineProgress = lazy(() => import('@/components/marathon-agent/PipelineProgress').then(mod => ({ default: mod.PipelineProgress })));
const StepTimeline = lazy(() => import('@/components/marathon-agent/StepTimeline').then(mod => ({ default: mod.StepTimeline })));
const AutoVerifyToggle = lazy(() => import('@/components/vibe-engineering/AutoVerifyToggle').then(mod => ({ default: mod.AutoVerifyToggle })));

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const { sessionData, isLoading: loadingSession } = useSessionData();

  // Handle potential nested data structure from backend wrapper
  const unwrappedData = (sessionData as any)?.data || sessionData;
  const activeTaskId = unwrappedData?.active_task_id || unwrappedData?.marathon_agent_context?.active_task_id || sessionId;

  // Vibe Engineering State
  const {
    state: vibeState,
    isVerifying,
    error: vibeError,
    startVerification,
  } = useVibeEngineering(sessionId);

  // Marathon Agent State
  const {
    taskState,
    isRunning,
    error: marathonError,
    startTask,
    cancelTask,
    recoverTask,
  } = useMarathonAgent(activeTaskId);

  // Config State
  const [autoVerify, setAutoVerify] = useState(true);
  const [autoImprove, setAutoImprove] = useState(true);
  const [qualityThreshold, setQualityThreshold] = useState(0.85);
  const [maxIterations, setMaxIterations] = useState(3);

  const handleStartAnalysis = async () => {
    try {
      // Start Marathon Agent pipeline
      const taskId = await startTask({
        task_type: 'full_analysis',
        session_id: sessionId,
        input_data: {},
        enable_checkpoints: true,
        checkpoint_interval_seconds: 60,
        max_retries_per_step: 3,
      });

      console.log('Started task:', taskId);

      // If auto-verify is enabled, logic would go here.
      // Typically verification starts after task completion.
    } catch (err) {
      console.error('Failed to start analysis:', err);
    }
  };

  // Calculate which analyses are complete
  const completedAnalyses = {
    bcg: !!(unwrappedData?.bcg_analysis?.items?.length || unwrappedData?.bcg?.items?.length),
    competitors: !!unwrappedData?.competitor_analysis,
    sentiment: !!unwrappedData?.sentiment_analysis,
    campaigns: !!(
      Array.isArray(unwrappedData?.campaigns)
        ? unwrappedData.campaigns.length
        : unwrappedData?.campaigns?.campaigns?.length
    ),
  };
  
  const totalCompleted = Object.values(completedAnalyses).filter(Boolean).length;
  const progressPercentage = (totalCompleted / 4) * 100;

  if (loadingSession) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with general progress */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">Analysis Overview</h1>
            <p className="text-blue-100 text-sm mt-1">
              Session: {sessionId.slice(0, 12)}...
            </p>
          </div>
          <Button 
            onClick={handleStartAnalysis} 
            disabled={isRunning}
            variant="secondary"
            size="lg"
          >
            <PlayCircle className="h-5 w-5 mr-2" />
            {isRunning ? 'Running...' : 'Start Full Analysis'}
          </Button>
        </div>
        
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Analysis Progress</span>
            <span>{totalCompleted}/4 Complete</span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-3">
            <div 
              className="bg-white rounded-full h-3 transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Completed Analysis Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnalysisCard
          title="BCG Matrix"
          icon={<BarChart3 className="w-6 h-6" />}
          completed={completedAnalyses.bcg}
          onClick={() => router.push(`/analysis/${sessionId}/bcg`)}
          description={completedAnalyses.bcg ? `${unwrappedData?.bcg_analysis?.items?.length || unwrappedData?.bcg?.items?.length || 0} products analyzed` : 'Not started'}
        />
        <AnalysisCard
          title="Competitors"
          icon={<Target className="w-6 h-6" />}
          completed={completedAnalyses.competitors}
          onClick={() => router.push(`/analysis/${sessionId}/competitors`)}
          description={completedAnalyses.competitors ? 'Analysis complete' : 'Not started'}
        />
        <AnalysisCard
          title="Sentiment"
          icon={<MessageSquare className="w-6 h-6" />}
          completed={completedAnalyses.sentiment}
          onClick={() => router.push(`/analysis/${sessionId}/sentiment`)}
          description={completedAnalyses.sentiment ? 'Analysis complete' : 'Not started'}
        />
        <AnalysisCard
          title="Campaigns"
          icon={<Megaphone className="w-6 h-6" />}
          completed={completedAnalyses.campaigns}
          onClick={() => router.push(`/analysis/${sessionId}/campaigns`)}
          description={completedAnalyses.campaigns ? `${unwrappedData?.campaigns?.campaigns?.length || 0} campaigns` : 'Not started'}
        />
      </div>

      {/* Detailed Analysis Summary */}
      {totalCompleted > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold">Detailed Results</h2>
          
          {completedAnalyses.bcg && (
            <SummaryCard 
              title="BCG Matrix Analysis"
              icon={<BarChart3 className="w-5 h-5" />}
              href={`/analysis/${sessionId}/bcg`}
            >
              <BCGSummaryMini data={unwrappedData?.bcg_analysis || unwrappedData?.bcg} />
            </SummaryCard>
          )}
          
          {completedAnalyses.competitors && (
            <SummaryCard 
              title="Competitor Analysis"
              icon={<Target className="w-5 h-5" />}
              href={`/analysis/${sessionId}/competitors`}
            >
              <CompetitorsSummaryMini data={unwrappedData?.competitor_analysis} />
            </SummaryCard>
          )}
          
          {completedAnalyses.sentiment && (
            <SummaryCard 
              title="Sentiment Analysis"
              icon={<MessageSquare className="w-5 h-5" />}
              href={`/analysis/${sessionId}/sentiment`}
            >
              <SentimentSummaryMini data={unwrappedData?.sentiment_analysis} />
            </SummaryCard>
          )}
          
          {completedAnalyses.campaigns && (
            <SummaryCard 
              title="Marketing Campaigns"
              icon={<Megaphone className="w-5 h-5" />}
              href={`/analysis/${sessionId}/campaigns`}
            >
              <CampaignsSummaryMini data={unwrappedData?.campaigns} />
            </SummaryCard>
          )}
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="progress" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="progress">Pipeline Progress</TabsTrigger>
          <TabsTrigger value="verification">Quality Verification</TabsTrigger>
          <TabsTrigger value="checkpoints">Checkpoints</TabsTrigger>
        </TabsList>

        {/* Pipeline Progress Tab */}
        <TabsContent value="progress" className="space-y-6">
          {taskState ? (
            <Suspense fallback={
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            }>
              <PipelineProgress
                taskState={taskState}
                onCancel={cancelTask}
                onRecover={() => recoverTask(taskState.task_id)}
              />
              <StepTimeline steps={taskState.steps} />
            </Suspense>
          ) : (
            <div className="text-center py-12 text-gray-500 border-2 border-dashed rounded-lg">
              No active pipeline. Click "Start Full Analysis" to begin.
            </div>
          )}
        </TabsContent>

        {/* Verification Tab */}
        <TabsContent value="verification">
          <Suspense fallback={
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          }>
            <VerificationPanel state={vibeState} isVerifying={isVerifying} />
          </Suspense>
          {!vibeState && !isVerifying && (
            <div className="text-center py-12 text-gray-500 border-2 border-dashed rounded-lg">
              No verification data available yet.
            </div>
          )}
        </TabsContent>

        {/* Checkpoints Tab */}
        <TabsContent value="checkpoints">
          {taskState ? (
            <Suspense fallback={
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            }>
              <CheckpointViewer
                checkpoints={taskState.checkpoints}
                onRestore={(checkpointId) => {
                  console.log('Restore from checkpoint:', checkpointId);
                  // Currently triggering general recovery for the task
                  recoverTask(taskState.task_id);
                }}
              />
            </Suspense>
          ) : (
            <div className="text-center py-12 text-gray-500 border-2 border-dashed rounded-lg">
              No checkpoints available yet.
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Errors */}
      {(vibeError || marathonError) && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-900">Error</p>
          <p className="text-sm text-red-700">{vibeError || marathonError}</p>
        </div>
      )}
    </div>
  );
}

// Component for analysis cards
function AnalysisCard({ 
  title, 
  icon, 
  completed, 
  onClick, 
  description 
}: { 
  title: string; 
  icon: React.ReactNode; 
  completed: boolean; 
  onClick: () => void;
  description: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-lg border-2 transition-all text-left hover:shadow-md ${
        completed 
          ? 'border-green-500 bg-green-50' 
          : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className={completed ? 'text-green-600' : 'text-gray-400'}>
          {icon}
        </div>
        {completed && <CheckCircle2 className="w-5 h-5 text-green-600" />}
        {!completed && <Clock className="w-5 h-5 text-gray-400" />}
      </div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="text-xs text-gray-600 mt-1">{description}</p>
    </button>
  );
}

// Component for summary cards
function SummaryCard({ 
  title, 
  icon, 
  href, 
  children 
}: { 
  title: string; 
  icon: React.ReactNode; 
  href: string;
  children: React.ReactNode;
}) {
  const router = useRouter();
  
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="text-blue-600">{icon}</div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
        </div>
        <button
          onClick={() => router.push(href)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View Details →
        </button>
      </div>
      {children}
    </div>
  );
}

// Mini summary components
function BCGSummaryMini({ data }: { data: any }) {
  if (!data) return null;
  
  return (
    <div className="grid grid-cols-4 gap-2 text-sm">
      <div className="text-center p-2 bg-yellow-50 rounded">
        <div className="text-2xl">⭐</div>
        <div className="font-bold">{data.summary?.categories?.find((c: any) => c.category === 'star')?.count || 0}</div>
        <div className="text-xs text-gray-600">Stars</div>
      </div>
      <div className="text-center p-2 bg-green-50 rounded">
        <div className="text-2xl">🐴</div>
        <div className="font-bold">{data.summary?.categories?.find((c: any) => c.category === 'plowhorse')?.count || 0}</div>
        <div className="text-xs text-gray-600">Plowhorses</div>
      </div>
      <div className="text-center p-2 bg-blue-50 rounded">
        <div className="text-2xl">🧩</div>
        <div className="font-bold">{data.summary?.categories?.find((c: any) => c.category === 'puzzle')?.count || 0}</div>
        <div className="text-xs text-gray-600">Puzzles</div>
      </div>
      <div className="text-center p-2 bg-red-50 rounded">
        <div className="text-2xl">🐕</div>
        <div className="font-bold">{data.summary?.categories?.find((c: any) => c.category === 'dog')?.count || 0}</div>
        <div className="text-xs text-gray-600">Dogs</div>
      </div>
    </div>
  );
}

function CompetitorsSummaryMini({ data }: { data: any }) {
  if (!data) return null;
  
  return (
    <div className="text-sm text-gray-700">
      <p>Competitors analyzed with strategic insights and recommendations.</p>
    </div>
  );
}

function SentimentSummaryMini({ data }: { data: any }) {
  if (!data) return null;
  
  return (
    <div className="text-sm text-gray-700">
      <p>Customer sentiment analysis complete with actionable insights.</p>
    </div>
  );
}

function CampaignsSummaryMini({ data }: { data: any }) {
  const campaigns = Array.isArray(data) ? data : data?.campaigns;
  if (!campaigns?.length) return null;
  
  return (
    <div className="text-sm text-gray-700">
      <p>{campaigns.length} AI-generated marketing campaigns ready to deploy.</p>
    </div>
  );
}
