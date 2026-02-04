import { Checkpoint, MarathonTaskConfig, MarathonTaskState } from '@/types/marathon-agent';

export class MarathonAgentAPI {
  private baseURL: string;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || '') {
    this.baseURL = baseURL;
  }

  /**
   * Inicia una tarea de larga duración
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
   * Obtiene el estado actual de una tarea
   */
  async getTaskStatus(taskId: string): Promise<MarathonTaskState> {
    const response = await fetch(`${this.baseURL}/api/v1/marathon/status/${taskId}`);

    if (!response.ok) {
      throw new Error(`Failed to get task status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Recupera una tarea desde el último checkpoint
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
   * Cancela una tarea en ejecución
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
   * Lista todos los checkpoints de una tarea
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
