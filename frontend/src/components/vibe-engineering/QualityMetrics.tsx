'use client';

import React from 'react';
import { VibeEngineeringState, QualityDimension } from '@/types/vibe-engineering';
import { Progress } from '@/components/ui/progress';

interface QualityMetricsProps {
  state: VibeEngineeringState;
}

export function QualityMetrics({ state }: QualityMetricsProps) {
  if (!state.verification_history.length) return null;

  const latestVerification = state.verification_history[state.verification_history.length - 1];

  const metrics = [
    {
      name: 'Precision',
      score: latestVerification.precision_score,
      description: 'Factual accuracy and logical correctness',
      color: 'bg-blue-500',
    },
    {
      name: 'Completeness',
      score: latestVerification.completeness_score,
      description: 'Coverage of all relevant aspects',
      color: 'bg-green-500',
    },
    {
      name: 'Applicability',
      score: latestVerification.applicability_score,
      description: 'Actionable and practical recommendations',
      color: 'bg-purple-500',
    },
    {
      name: 'Clarity',
      score: latestVerification.clarity_score,
      description: 'Understandability and explanation quality',
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="space-y-4">
      <h4 className="font-semibold text-sm text-gray-900">Quality Dimensions</h4>
      <div className="space-y-3">
        {metrics.map((metric) => (
          <div key={metric.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{metric.name}</p>
                <p className="text-xs text-gray-600">{metric.description}</p>
              </div>
              <span className="text-sm font-semibold text-gray-900">
                {(metric.score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="relative">
              <Progress value={metric.score * 100} className="h-2" />
              <div
                className={`absolute top-0 left-0 h-2 rounded-full ${metric.color} transition-all duration-500`}
                style={{ width: `${metric.score * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Overall Score - Large Display */}
      <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-200">
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Overall Quality Score</p>
          <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            {(latestVerification.quality_score * 100).toFixed(1)}%
          </div>
          {state.auto_improved && (
            <p className="text-sm text-green-600 mt-2 font-medium">
              ✨ Improved from{' '}
              {state.verification_history[0]
                ? (state.verification_history[0].quality_score * 100).toFixed(1)
                : 'N/A'}
              %
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
