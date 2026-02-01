export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  RECOVERING = 'recovering'
}

export enum StepStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped'
}

export interface PipelineStep {
  step_id: string;
  name: string;
  description: string;
  status: StepStatus;
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  error_message?: string;
  result?: any;
  retry_count: number;
  max_retries: number;
}

export interface Checkpoint {
  checkpoint_id: string;
  task_id: string;
  step_index: number;
  timestamp: string;
  accumulated_results: Record<string, any>;
  state_snapshot: any;
}

export interface MarathonTaskConfig {
  task_type: 'full_analysis' | 'competitive_intel' | 'campaign_generation';
  session_id: string;
  input_data: any;
  enable_checkpoints: boolean;
  checkpoint_interval_seconds: number;
  max_retries_per_step: number;
}

export interface MarathonTaskState {
  task_id: string;
  status: TaskStatus;
  progress: number; // 0-1
  current_step: number;
  total_steps: number;
  current_step_name: string;
  started_at: string;
  estimated_completion?: string;
  completed_at?: string;
  steps: PipelineStep[];
  checkpoints: Checkpoint[];
  accumulated_results: Record<string, any>;
  error?: string;
  can_recover: boolean;
}

export interface ProgressUpdate {
  task_id: string;
  progress: number;
  current_step: string;
  status: TaskStatus;
  timestamp: string;
  message?: string;
}

export interface RecoveryOption {
  checkpoint_id: string;
  timestamp: string;
  description: string;
}
