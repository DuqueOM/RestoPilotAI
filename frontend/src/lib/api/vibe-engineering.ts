import { VibeEngineeringConfig, VibeEngineeringState } from '@/types/vibe-engineering';

export class VibeEngineeringAPI {
  private baseURL: string;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || '') {
    this.baseURL = baseURL;
  }

  /**
   * Inicia verificación y mejora autónoma de un análisis
   */
  async verifyAndImproveAnalysis(
    sessionId: string,
    analysisType: 'bcg_classification' | 'competitive_analysis' | 'campaign_generation',
    config: VibeEngineeringConfig
  ): Promise<VibeEngineeringState> {
    const response = await fetch(`${this.baseURL}/api/v1/vibe-engineering/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        analysis_type: analysisType,
        auto_verify: config.auto_verify,
        auto_improve: config.auto_improve,
        quality_threshold: config.quality_threshold,
        max_iterations: config.max_iterations,
      }),
    });

    if (!response.ok) {
      throw new Error(`Verification failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Obtiene el estado actual de verificación
   */
  async getVerificationStatus(sessionId: string): Promise<VibeEngineeringState | null> {
    const response = await fetch(
      `${this.baseURL}/api/v1/vibe-engineering/status?session_id=${sessionId}` 
    );

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Failed to get status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Cancela un proceso de verificación en curso
   */
  async cancelVerification(sessionId: string): Promise<void> {
    const response = await fetch(
      `${this.baseURL}/api/v1/vibe-engineering/cancel?session_id=${sessionId}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      throw new Error(`Failed to cancel: ${response.statusText}`);
    }
  }
}

export const vibeAPI = new VibeEngineeringAPI();
