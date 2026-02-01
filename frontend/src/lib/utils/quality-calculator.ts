import { VerificationResult } from '@/types/vibe-engineering';

export const calculateOverallQuality = (metrics: Partial<VerificationResult>): number => {
  const weights = {
    precision_score: 0.3,
    completeness_score: 0.2,
    applicability_score: 0.3,
    clarity_score: 0.2,
  };

  let totalScore = 0;
  let totalWeight = 0;

  if (metrics.precision_score !== undefined) {
    totalScore += metrics.precision_score * weights.precision_score;
    totalWeight += weights.precision_score;
  }
  if (metrics.completeness_score !== undefined) {
    totalScore += metrics.completeness_score * weights.completeness_score;
    totalWeight += weights.completeness_score;
  }
  if (metrics.applicability_score !== undefined) {
    totalScore += metrics.applicability_score * weights.applicability_score;
    totalWeight += weights.applicability_score;
  }
  if (metrics.clarity_score !== undefined) {
    totalScore += metrics.clarity_score * weights.clarity_score;
    totalWeight += weights.clarity_score;
  }

  return totalWeight > 0 ? Number((totalScore / totalWeight).toFixed(2)) : 0;
};

export const getQualityColor = (score: number): string => {
  if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
  if (score >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  return 'text-red-600 bg-red-50 border-red-200';
};
