import { vibeAPI } from '@/lib/api/vibe-engineering';
import { VibeEngineeringConfig, VibeEngineeringState } from '@/types/vibe-engineering';
import { useCallback, useEffect, useState } from 'react';

interface UseVibeEngineeringResult {
  state: VibeEngineeringState | null;
  isVerifying: boolean;
  error: string | null;
  startVerification: (
    sessionId: string,
    analysisType: 'bcg_classification' | 'competitive_analysis' | 'campaign_generation',
    config?: Partial<VibeEngineeringConfig>
  ) => Promise<void>;
  cancelVerification: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

export function useVibeEngineering(sessionId: string): UseVibeEngineeringResult {
  const [state, setState] = useState<VibeEngineeringState | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshStatus = useCallback(async () => {
    try {
      const status = await vibeAPI.getVerificationStatus(sessionId);
      setState(status);
    } catch (err) {
      console.error('Failed to refresh status:', err);
    }
  }, [sessionId]);

  const startVerification = useCallback(
    async (
      sessionId: string,
      analysisType: 'bcg_classification' | 'competitive_analysis' | 'campaign_generation',
      configOverrides?: Partial<VibeEngineeringConfig>
    ) => {
      const defaultConfig: VibeEngineeringConfig = {
        auto_verify: true,
        auto_improve: true,
        quality_threshold: 0.85,
        max_iterations: 3,
      };
      setIsVerifying(true);
      setError(null);

      try {
        const config = { ...defaultConfig, ...configOverrides };
        const result = await vibeAPI.verifyAndImproveAnalysis(sessionId, analysisType, config);
        setState(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Verification failed');
      } finally {
        setIsVerifying(false);
      }
    },
    [defaultConfig]
  );

  const cancelVerification = useCallback(async () => {
    try {
      await vibeAPI.cancelVerification(sessionId);
      setIsVerifying(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel');
    }
  }, [sessionId]);

  // Poll for status updates every 2 seconds when verifying
  useEffect(() => {
    if (!isVerifying) return;

    const interval = setInterval(refreshStatus, 2000);
    return () => clearInterval(interval);
  }, [isVerifying, refreshStatus]);

  return {
    state,
    isVerifying,
    error,
    startVerification,
    cancelVerification,
    refreshStatus,
  };
}
