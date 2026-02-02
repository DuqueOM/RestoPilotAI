'use client';

import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AutoVerifyToggle } from '@/components/vibe-engineering/AutoVerifyToggle';
import { useMarathonAgent } from '@/hooks/useMarathonAgent';
import { useVibeEngineering } from '@/hooks/useVibeEngineering';
import { api } from '@/lib/api';
import { Loader2, PlayCircle } from 'lucide-react';
import { useParams } from 'next/navigation';
import { useEffect, useState, lazy, Suspense } from 'react';

// Lazy load heavy components for better performance
const VerificationPanel = lazy(() => import('@/components/vibe-engineering/VerificationPanel').then(mod => ({ default: mod.VerificationPanel })));
const CheckpointViewer = lazy(() => import('@/components/marathon-agent/CheckpointViewer').then(mod => ({ default: mod.CheckpointViewer })));
const PipelineProgress = lazy(() => import('@/components/marathon-agent/PipelineProgress').then(mod => ({ default: mod.PipelineProgress })));
const StepTimeline = lazy(() => import('@/components/marathon-agent/StepTimeline').then(mod => ({ default: mod.StepTimeline })));

export default function AnalysisPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  // Session State (to recover active task ID)
  const [session, setSession] = useState<any>(null);
  const [loadingSession, setLoadingSession] = useState(true);

  // Fetch session on mount to get active task ID
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(sessionId);
        setSession(data);
      } catch (err) {
        console.error('Failed to load session:', err);
      } finally {
        setLoadingSession(false);
      }
    };
    if (sessionId) fetchSession();
  }, [sessionId]);

  // Handle potential nested data structure from backend wrapper
  const sessionData = session?.data || session;
  const activeTaskId = sessionData?.active_task_id || sessionData?.marathon_agent_context?.active_task_id;

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

  if (loadingSession) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Session: <code className="text-sm bg-gray-100 px-2 py-1 rounded">{sessionId}</code>
          </p>
        </div>
        <Button onClick={handleStartAnalysis} disabled={isRunning} size="lg">
          <PlayCircle className="h-5 w-5 mr-2" />
          {isRunning ? 'Running...' : 'Start Full Analysis'}
        </Button>
      </div>

      {/* Configuration Panel */}
      <AutoVerifyToggle
        autoVerify={autoVerify}
        autoImprove={autoImprove}
        qualityThreshold={qualityThreshold}
        maxIterations={maxIterations}
        onAutoVerifyChange={setAutoVerify}
        onAutoImproveChange={setAutoImprove}
        onQualityThresholdChange={setQualityThreshold}
        onMaxIterationsChange={setMaxIterations}
        disabled={isRunning}
      />

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
