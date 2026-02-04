import { marathonAPI } from '@/lib/api/marathon-agent';
import { MarathonTaskConfig, MarathonTaskState, TaskStatus } from '@/types/marathon-agent';
import { useCallback, useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';

interface UseMarathonAgentResult {
  taskState: MarathonTaskState | null;
  isRunning: boolean;
  error: string | null;
  startTask: (config: MarathonTaskConfig) => Promise<string>;
  cancelTask: () => Promise<void>;
  recoverTask: (taskId: string) => Promise<void>;
  refreshStatus: () => Promise<void>;
}

export function useMarathonAgent(initialTaskId?: string | null): UseMarathonAgentResult {
  const [taskState, setTaskState] = useState<MarathonTaskState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(initialTaskId || null);

  const isRunning = taskState?.status === TaskStatus.RUNNING || taskState?.status === TaskStatus.RECOVERING;

  // WebSocket for real-time progress updates
  const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = typeof window !== 'undefined' ? window.location.host : 'localhost:3000';
  const defaultWsUrl = `${wsProtocol}//${wsHost}/api/v1`;
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || defaultWsUrl;

  const { lastMessage, isConnected } = useWebSocket(
    currentTaskId ? `${wsUrl}/ws/marathon/${currentTaskId}` : null
  );

  useEffect(() => {
    if (initialTaskId) {
      setCurrentTaskId(initialTaskId);
    }
  }, [initialTaskId]);

  const refreshStatus = useCallback(async () => {
    if (!currentTaskId) return;

    try {
      const status = await marathonAPI.getTaskStatus(currentTaskId);
      setTaskState(status);
    } catch (err) {
      console.error('Failed to refresh status:', err);
    }
  }, [currentTaskId]);

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    try {
      const update = JSON.parse(lastMessage);
      
      if (update.type === 'progress_update' && update.data) {
        setTaskState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            progress: update.data.progress,
            current_step_name: update.data.current_step,
            status: update.data.status,
          };
        });
      } else if (update.type === 'task_complete') {
        refreshStatus();
      } else if (update.type === 'task_error') {
        setError(update.data?.error || 'Unknown error');
        refreshStatus();
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
    }
  }, [lastMessage, refreshStatus]);

  const startTask = useCallback(async (config: MarathonTaskConfig): Promise<string> => {
    setError(null);

    try {
      const { task_id } = await marathonAPI.startTask(config);
      setCurrentTaskId(task_id);

      // Wait a bit for the background task to initialize
      await new Promise(resolve => setTimeout(resolve, 500));

      // Initial status fetch - tolerate 404 as task may still be initializing
      try {
        const status = await marathonAPI.getTaskStatus(task_id);
        setTaskState(status);
      } catch (statusErr) {
        console.warn('Initial status fetch failed, will retry via WebSocket:', statusErr);
      }

      return task_id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start task');
      throw err;
    }
  }, []);

  const cancelTask = useCallback(async () => {
    if (!currentTaskId) return;

    try {
      await marathonAPI.cancelTask(currentTaskId);
      await refreshStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel task');
    }
  }, [currentTaskId, refreshStatus]);

  const recoverTask = useCallback(async (taskId: string) => {
    setError(null);

    try {
      const { task_id } = await marathonAPI.recoverTask(taskId);
      setCurrentTaskId(task_id);

      const status = await marathonAPI.getTaskStatus(task_id);
      setTaskState(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to recover task');
    }
  }, []);

  // Poll for status when not using WebSocket
  useEffect(() => {
    if (!isRunning || isConnected) return;

    const interval = setInterval(refreshStatus, 3000);
    return () => clearInterval(interval);
  }, [isRunning, isConnected, refreshStatus]);

  return {
    taskState,
    isRunning,
    error,
    startTask,
    cancelTask,
    recoverTask,
    refreshStatus,
  };
}
