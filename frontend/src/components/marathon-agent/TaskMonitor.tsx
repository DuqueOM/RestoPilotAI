import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useMarathonAgent } from '@/hooks/useMarathonAgent';
import { cn } from '@/lib/utils';
import { Activity, Pause } from 'lucide-react';
import { CheckpointViewer } from './CheckpointViewer';
import { PipelineProgress } from './PipelineProgress';
import { RecoveryPanel } from './RecoveryPanel';
import { StepTimeline } from './StepTimeline';

interface TaskMonitorProps {
  taskId: string | null;
  className?: string;
  onTaskComplete?: () => void;
}

export function TaskMonitor({ taskId, className, onTaskComplete }: TaskMonitorProps) {
  const { 
    taskState, 
    isRunning, 
    error, 
    recoverTask, 
    cancelTask 
  } = useMarathonAgent(taskId);

  if (!taskId) return null;

  if (!taskState && !error) {
    return (
      <Card className={className}>
        <CardContent className="p-8 flex justify-center">
          <LoadingSpinner size="lg" label="Loading task status..." />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className={className}>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!taskState) return null;

  const isFailed = taskState.status === 'failed';
  
  // Create recovery options from checkpoints if failed
  const recoveryOptions = isFailed && taskState.checkpoints ? 
    taskState.checkpoints.map(cp => ({
      checkpoint_id: cp.checkpoint_id,
      timestamp: cp.timestamp,
      description: `Recover from Step ${cp.step_index + 1}`
    })) : [];

  // Wrap recoverTask to handle the argument mismatch (components pass checkpointId, hook expects taskId)
  // Currently backend only supports recovering the task generally (resuming), so we ignore the specific checkpointId for now
  const handleRecover = () => {
    if (taskId) {
      recoverTask(taskId);
    }
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <CardTitle>Marathon Agent Monitor</CardTitle>
          </div>
          <div className="flex space-x-2">
            {isRunning && (
              <Button size="sm" variant="destructive" onClick={cancelTask}>
                <Pause className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            )}
          </div>
        </div>
        <CardDescription>
          Long-running task execution with state persistence and recovery
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <PipelineProgress task={taskState} />
        
        {isFailed && (
          <RecoveryPanel 
            options={recoveryOptions} 
            onRecover={handleRecover} 
            isRecovering={false} // Hook doesn't expose recovering state explicitly distinct from running
          />
        )}

        <div className="grid gap-6 md:grid-cols-2">
          <StepTimeline 
            steps={taskState.steps} 
            currentStepIndex={taskState.current_step - 1} 
          />
          <CheckpointViewer 
            checkpoints={taskState.checkpoints} 
            onRecover={handleRecover}
          />
        </div>
      </CardContent>
    </Card>
  );
}
