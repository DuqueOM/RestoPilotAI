'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { VibeEngineeringState } from '@/types/vibe-engineering';
import { AlertTriangle, CheckCircle2, Loader2, XCircle } from 'lucide-react';
import { ImprovementHistory } from './ImprovementHistory';
import { QualityMetrics } from './QualityMetrics';

interface VerificationPanelProps {
  state: VibeEngineeringState | null;
  isVerifying: boolean;
}

export function VerificationPanel({ state, isVerifying }: VerificationPanelProps) {
  if (!state && !isVerifying) {
    return null;
  }

  const getQualityStatus = (score: number) => {
    if (score >= 0.85) return { icon: CheckCircle2, color: 'text-green-600', label: 'Excellent' };
    if (score >= 0.70) return { icon: AlertTriangle, color: 'text-yellow-600', label: 'Good' };
    return { icon: XCircle, color: 'text-red-600', label: 'Needs Improvement' };
  };

  const status = state ? getQualityStatus(state.quality_achieved) : null;
  const StatusIcon = status?.icon || Loader2;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <StatusIcon 
                className={`h-5 w-5 ${status?.color || 'text-gray-400'} ${isVerifying ? 'animate-spin' : ''}`} 
              />
              Vibe Engineering - Quality Assurance
            </CardTitle>
            <CardDescription>
              Autonomous verification and improvement loop
            </CardDescription>
          </div>
          {state && (
            <Badge variant={state.auto_improved ? 'default' : 'outline'}>
              {state.auto_improved ? 'Auto-Improved' : 'Original Analysis'}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {isVerifying && (
          <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
            <div>
              <p className="font-medium text-blue-900">Verifying analysis quality...</p>
              <p className="text-sm text-blue-700">
                The AI is reviewing its own work and improving it automatically
              </p>
            </div>
          </div>
        )}

        {state && (
          <>
            {/* Quality Metrics */}
            <QualityMetrics state={state} />

            {/* Improvement History */}
            {state.improvement_iterations && state.improvement_iterations.length > 0 && (
              <ImprovementHistory iterations={state.improvement_iterations} />
            )}

            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Iterations</p>
                <p className="text-2xl font-bold text-gray-900">{state.iterations_required}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Quality Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {((state.quality_achieved || 0) * 100).toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Duration</p>
                <p className="text-2xl font-bold text-gray-900">
                  {((state.total_duration_ms || 0) / 1000).toFixed(1)}s
                </p>
              </div>
            </div>

            {/* Latest Verification Details */}
            {state.verification_history && state.verification_history.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold text-sm text-gray-900">Latest Assessment</h4>
                <p className="text-sm text-gray-700">
                  {state.verification_history[state.verification_history.length - 1].overall_assessment}
                </p>

                {/* Strengths */}
                {state.verification_history[state.verification_history.length - 1].strengths?.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-green-800 mb-2">Strengths:</p>
                    <ul className="space-y-1">
                      {state.verification_history[state.verification_history.length - 1].strengths.map(
                        (strength, idx) => (
                          <li key={idx} className="text-sm text-green-700 flex items-start gap-2">
                            <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                            <span>{strength}</span>
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                {/* Issues */}
                {state.verification_history[state.verification_history.length - 1].identified_issues?.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-red-800 mb-2">Issues Identified:</p>
                    <ul className="space-y-2">
                      {state.verification_history[state.verification_history.length - 1].identified_issues.map(
                        (issue, idx) => (
                          <li key={idx} className="text-sm">
                            <div className="flex items-start gap-2">
                              <Badge
                                variant={
                                  issue.severity === 'high'
                                    ? 'destructive'
                                    : issue.severity === 'medium'
                                    ? 'default'
                                    : 'secondary'
                                }
                                className="mt-0.5"
                              >
                                {issue.severity}
                              </Badge>
                              <div className="flex-1">
                                <p className="font-medium text-gray-900">{issue.issue}</p>
                                <p className="text-xs text-gray-600 mt-1">
                                  Suggestion: {issue.suggestion}
                                </p>
                              </div>
                            </div>
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
