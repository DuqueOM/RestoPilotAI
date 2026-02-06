'use client';

import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
    ArrowRight,
    BarChart3,
    Check,
    ChevronDown,
    ChevronUp,
    Crown,
    Eye,
    MousePointer,
    Percent,
    Sparkles,
    TrendingUp,
    Users,
    Zap,
} from 'lucide-react';
import { useState } from 'react';

export interface ABVariant {
  id: string;
  name: string;
  label: 'A' | 'B' | 'C';
  headline: string;
  body: string;
  imageUrl?: string;
  metrics?: {
    impressions?: number;
    clicks?: number;
    conversions?: number;
    ctr?: number;
    conversionRate?: number;
    costPerClick?: number;
    costPerConversion?: number;
  };
  isWinner?: boolean;
  confidenceScore?: number;
  aiInsight?: string;
}

export interface ABTest {
  id: string;
  name: string;
  status: 'draft' | 'running' | 'completed' | 'paused';
  startDate?: string;
  endDate?: string;
  objective: string;
  targetMetric: 'ctr' | 'conversion' | 'engagement';
  variants: ABVariant[];
  sampleSize?: number;
  statisticalSignificance?: number;
  recommendation?: string;
}

interface ABTestingPanelProps {
  test: ABTest;
  onSelectWinner?: (variantId: string) => void;
  onStartTest?: () => void;
  onStopTest?: () => void;
  onGenerateVariant?: () => void;
  className?: string;
}

function VariantCard({
  variant,
  comparisonVariant,
  targetMetric,
  isSelected,
  onSelect,
}: {
  variant: ABVariant;
  comparisonVariant?: ABVariant;
  targetMetric: string;
  isSelected?: boolean;
  onSelect?: () => void;
}) {
  const [expanded, setExpanded] = useState(false);

  const getMetricValue = (v: ABVariant) => {
    if (!v.metrics) return 0;
    switch (targetMetric) {
      case 'ctr': return v.metrics.ctr || 0;
      case 'conversion': return v.metrics.conversionRate || 0;
      case 'engagement': return (v.metrics.clicks || 0) / Math.max(v.metrics.impressions || 1, 1) * 100;
      default: return 0;
    }
  };

  const currentValue = getMetricValue(variant);
  const comparisonValue = comparisonVariant ? getMetricValue(comparisonVariant) : 0;
  const improvement = comparisonVariant && comparisonValue > 0
    ? ((currentValue - comparisonValue) / comparisonValue * 100)
    : 0;

  return (
    <div
      className={cn(
        'rounded-xl border-2 overflow-hidden transition-all',
        variant.isWinner && 'border-green-500 bg-green-50/30',
        isSelected && !variant.isWinner && 'border-purple-500',
        !variant.isWinner && !isSelected && 'border-gray-200'
      )}
    >
      {/* Header */}
      <div className="p-4 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white">
        <div className="flex items-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg',
            variant.label === 'A' && 'bg-blue-100 text-blue-700',
            variant.label === 'B' && 'bg-purple-100 text-purple-700',
            variant.label === 'C' && 'bg-orange-100 text-orange-700'
          )}>
            {variant.label}
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 flex items-center gap-2">
              {variant.name}
              {variant.isWinner && (
                <Badge className="bg-green-500 text-white">
                  <Crown className="h-3 w-3 mr-1" />
                  Winner
                </Badge>
              )}
            </h4>
            {variant.confidenceScore !== undefined && (
              <p className="text-sm text-gray-500">
                Confidence: {(variant.confidenceScore * 100).toFixed(1)}%
              </p>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {improvement !== 0 && comparisonVariant && (
            <Badge
              variant="outline"
              className={cn(
                improvement > 0 ? 'text-green-700 border-green-300' : 'text-red-700 border-red-300'
              )}
            >
              {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
            </Badge>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            {expanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Preview */}
      <div className="p-4 border-t">
        <div className="flex gap-4">
          {variant.imageUrl && (
            <img
              src={variant.imageUrl}
              alt={variant.name}
              className="w-24 h-24 rounded-lg object-cover flex-shrink-0"
            />
          )}
          <div className="flex-1 min-w-0">
            <h5 className="font-medium text-gray-900 line-clamp-2">{variant.headline}</h5>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{variant.body}</p>
          </div>
        </div>
      </div>

      {/* Metrics */}
      {variant.metrics && (
        <div className="px-4 py-3 bg-gray-50 border-t grid grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-xs text-gray-500 flex items-center justify-center gap-1">
              <Eye className="h-3 w-3" />
              Impressions
            </p>
            <p className="font-semibold text-gray-900">
              {variant.metrics.impressions?.toLocaleString() || '-'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500 flex items-center justify-center gap-1">
              <MousePointer className="h-3 w-3" />
              Clicks
            </p>
            <p className="font-semibold text-gray-900">
              {variant.metrics.clicks?.toLocaleString() || '-'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500 flex items-center justify-center gap-1">
              <Percent className="h-3 w-3" />
              CTR
            </p>
            <p className={cn(
              'font-semibold',
              targetMetric === 'ctr' && 'text-purple-600'
            )}>
              {variant.metrics.ctr?.toFixed(2) || '-'}%
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500 flex items-center justify-center gap-1">
              <TrendingUp className="h-3 w-3" />
              Conv.
            </p>
            <p className={cn(
              'font-semibold',
              targetMetric === 'conversion' && 'text-purple-600'
            )}>
              {variant.metrics.conversionRate?.toFixed(2) || '-'}%
            </p>
          </div>
        </div>
      )}

      {/* Expanded AI Insight */}
      {expanded && variant.aiInsight && (
        <div className="px-4 py-3 border-t bg-purple-50">
          <p className="text-xs text-purple-600 mb-1 flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            Gemini Insight:
          </p>
          <p className="text-sm text-purple-800">{variant.aiInsight}</p>
        </div>
      )}

      {/* Select Button */}
      {onSelect && !variant.isWinner && (
        <div className="p-3 border-t">
          <Button
            variant={isSelected ? 'default' : 'outline'}
            className="w-full"
            onClick={onSelect}
          >
            {isSelected ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Selected
              </>
            ) : (
              'Select as Winner'
            )}
          </Button>
        </div>
      )}
    </div>
  );
}

export function ABTestingPanel({
  test,
  onSelectWinner,
  onStartTest,
  onStopTest,
  onGenerateVariant,
  className,
}: ABTestingPanelProps) {
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null);

  const completionPercentage = test.sampleSize && test.variants[0]?.metrics?.impressions
    ? Math.min((test.variants[0].metrics.impressions / test.sampleSize) * 100, 100)
    : 0;

  const baseVariant = test.variants.find(v => v.label === 'A');

  return (
    <div className={cn('rounded-xl border bg-white overflow-hidden', className)}>
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <BarChart3 className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{test.name}</h3>
              <p className="text-sm text-gray-600">{test.objective}</p>
            </div>
          </div>
          <Badge
            variant="outline"
            className={cn(
              test.status === 'running' && 'border-green-500 text-green-700 bg-green-50',
              test.status === 'completed' && 'border-blue-500 text-blue-700 bg-blue-50',
              test.status === 'paused' && 'border-amber-500 text-amber-700 bg-amber-50',
              test.status === 'draft' && 'border-gray-500 text-gray-700'
            )}
          >
            {test.status === 'running' && '● In Progress'}
            {test.status === 'completed' && '✓ Completed'}
            {test.status === 'paused' && '⏸ Paused'}
            {test.status === 'draft' && 'Draft'}
          </Badge>
        </div>

        {/* Progress */}
        {test.status === 'running' && test.sampleSize && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 flex items-center gap-1">
                <Users className="h-4 w-4" />
                Test Progress
              </span>
              <span className="font-medium text-gray-900">{completionPercentage.toFixed(0)}%</span>
            </div>
            <Progress value={completionPercentage} className="h-2" />
            <p className="text-xs text-gray-500 text-right">
              {test.variants[0]?.metrics?.impressions?.toLocaleString() || 0} / {test.sampleSize?.toLocaleString()} samples
            </p>
          </div>
        )}

        {/* Statistical Significance */}
        {test.statisticalSignificance !== undefined && (
          <div className="mt-3 p-3 bg-white/60 rounded-lg flex items-center justify-between">
            <span className="text-sm text-gray-700">Statistical Significance:</span>
            <ConfidenceIndicator value={test.statisticalSignificance} variant="badge" size="sm" />
          </div>
        )}
      </div>

      {/* Variants */}
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-gray-900">
            Variants ({test.variants.length})
          </h4>
          {onGenerateVariant && test.variants.length < 3 && (
            <Button variant="outline" size="sm" onClick={onGenerateVariant}>
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Variant
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {test.variants.map((variant) => (
            <VariantCard
              key={variant.id}
              variant={variant}
              comparisonVariant={variant.label !== 'A' ? baseVariant : undefined}
              targetMetric={test.targetMetric}
              isSelected={selectedVariant === variant.id}
              onSelect={onSelectWinner ? () => {
                setSelectedVariant(variant.id);
                onSelectWinner(variant.id);
              } : undefined}
            />
          ))}
        </div>
      </div>

      {/* Recommendation */}
      {test.recommendation && (
        <div className="px-4 pb-4">
          <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
            <div className="flex items-start gap-3">
              <Zap className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h5 className="font-medium text-green-800">Gemini Recommendation</h5>
                <p className="text-sm text-green-700 mt-1">{test.recommendation}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="p-4 bg-gray-50 border-t flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Target Metric: <span className="font-medium">{test.targetMetric.toUpperCase()}</span>
        </div>
        <div className="flex items-center gap-2">
          {test.status === 'draft' && onStartTest && (
            <Button onClick={onStartTest}>
              <ArrowRight className="h-4 w-4 mr-2" />
              Start Test
            </Button>
          )}
          {test.status === 'running' && onStopTest && (
            <Button variant="outline" onClick={onStopTest}>
              Stop Test
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ABTestingPanel;
