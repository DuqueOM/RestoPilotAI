import { Checkpoint, MarathonTaskConfig, MarathonTaskState } from '@/types/marathon-agent';

export class MarathonAgentAPI {
  private baseURL: string;

  constructor(baseURL: string = '') {
    this.baseURL = baseURL;
  }

  /**
   * Starts a long-running task
   */
  async startTask(config: MarathonTaskConfig): Promise<{ task_id: string }> {
    const response = await fetch(`${this.baseURL}/api/v1/marathon/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      throw new Error(`Failed to start task: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Gets the current status of a task
   */
  async getTaskStatus(taskId: string): Promise<MarathonTaskState> {
    const response = await fetch(`${this.baseURL}/api/v1/marathon/status/${taskId}`);

    if (!response.ok) {
      throw new Error(`Failed to get task status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Recovers a task from the last checkpoint
   */
  async recoverTask(taskId: string): Promise<{ task_id: string }> {
    const response = await fetch(`${this.baseURL}/api/v1/marathon/recover/${taskId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to recover task: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Cancels a running task
   */
  async cancelTask(taskId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/v1/marathon/cancel/${taskId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to cancel task: ${response.statusText}`);
    }
  }

  /**
   * Lists all checkpoints for a task
   */
  async getCheckpoints(taskId: string): Promise<Checkpoint[]> {
    const response = await fetch(`${this.baseURL}/api/v1/marathon/checkpoints/${taskId}`);

    if (!response.ok) {
      throw new Error(`Failed to get checkpoints: ${response.statusText}`);
    }

    return response.json();
  }
}

export const marathonAPI = new MarathonAgentAPI();
