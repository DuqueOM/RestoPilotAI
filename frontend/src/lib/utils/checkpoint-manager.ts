import { Checkpoint, MarathonTaskState } from '@/types/marathon-agent';

export const getLatestCheckpoint = (task: MarathonTaskState): Checkpoint | null => {
  if (!task.checkpoints || task.checkpoints.length === 0) return null;
  
  return task.checkpoints.reduce((latest, current) => {
    return new Date(current.timestamp) > new Date(latest.timestamp) ? current : latest;
  });
};

export const formatCheckpointTime = (timestamp: string): string => {
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric',
    day: 'numeric',
    month: 'short'
  }).format(new Date(timestamp));
};

export const isRecoverable = (task: MarathonTaskState): boolean => {
  return task.status === 'failed' && task.checkpoints.length > 0;
};
