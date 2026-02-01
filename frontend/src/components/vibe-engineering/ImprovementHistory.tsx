'use client';

import React from 'react';
import { ImprovementIteration } from '@/types/vibe-engineering';
import { ArrowRight, CheckCircle2 } from 'lucide-react';

interface ImprovementHistoryProps {
  iterations: ImprovementIteration[];
}

export function ImprovementHistory({ iterations }: ImprovementHistoryProps) {
  return (
    <div className="space-y-4">
      <h4 className="font-semibold text-sm text-gray-900">Improvement Timeline</h4>
      <div className="space-y-3">
        {iterations.map((iteration, idx) => (
          <div
            key={iteration.iteration}
            className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-600">
                  Iteration {iteration.iteration}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(iteration.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <span className="text-xs text-gray-600">
                {iteration.duration_ms}ms
              </span>
            </div>

            {/* Quality Improvement Visualization */}
            <div className="flex items-center gap-3 mb-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-900">
                  {(iteration.quality_before * 100).toFixed(1)}%
                </span>
                <ArrowRight className="h-4 w-4 text-gray-400" />
                <span className="text-sm font-medium text-green-600">
                  {(iteration.quality_after * 100).toFixed(1)}%
                </span>
              </div>
              <span className="text-xs text-green-600 font-medium">
                +{((iteration.quality_after - iteration.quality_before) * 100).toFixed(1)}%
              </span>
            </div>

            {/* Issues Fixed */}
            {iteration.issues_fixed.length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-700 mb-1">Issues Fixed:</p>
                <ul className="space-y-1">
                  {iteration.issues_fixed.map((issue, issueIdx) => (
                    <li key={issueIdx} className="flex items-start gap-2 text-xs text-gray-600">
                      <CheckCircle2 className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
