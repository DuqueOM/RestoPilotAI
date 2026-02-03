export enum QualityDimension {
  PRECISION = 'precision',
  COMPLETENESS = 'completeness',
  APPLICABILITY = 'applicability',
  CLARITY = 'clarity'
}

export enum IssueSeverity {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

export interface QualityIssue {
  issue: string;
  severity: IssueSeverity;
  category: QualityDimension;
  suggestion: string;
}

export interface VerificationResult {
  quality_score: number;
  precision_score: number;
  completeness_score: number;
  applicability_score: number;
  clarity_score: number;
  identified_issues: QualityIssue[];
  strengths: string[];
  overall_assessment: string;
  timestamp?: string;
}

export interface ImprovementIteration {
  iteration: number;
  timestamp: string;
  quality_before: number;
  quality_after: number;
  issues_fixed: string[];
  duration_ms: number;
}

export interface VibeEngineeringState {
  final_analysis: Record<string, unknown>;
  verification_history: VerificationResult[];
  iterations_required: number;
  quality_achieved: number;
  auto_improved: boolean;
  improvement_iterations: ImprovementIteration[];
  total_duration_ms: number;
}

export interface VibeEngineeringConfig {
  auto_verify: boolean;
  auto_improve: boolean;
  quality_threshold: number; // 0-1
  max_iterations: number;
}
