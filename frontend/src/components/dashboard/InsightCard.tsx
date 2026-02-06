'use client';

import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { GroundingSource, VerifiedSourceBadge } from '@/components/ai/VerifiedSourceBadge';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    AlertTriangle,
    ArrowRight,
    ChevronDown,
    ChevronUp,
    DollarSign,
    Lightbulb,
    Rocket,
    Sparkles,
    Target,
    TrendingDown,
    TrendingUp,
    Zap,
} from 'lucide-react';
import { useState } from 'react';

export type InsightType = 'opportunity' | 'warning' | 'trend' | 'action' | 'anomaly';
export type InsightPriority = 'high' | 'medium' | 'low';

export interface Insight {
  id: string;
  type: InsightType;
  priority: InsightPriority;
  title: string;
  description: string;
  metric?: {
    name: string;
    value: number;
    change?: number;
    unit?: string;
  };
  impact?: {
    type: 'revenue' | 'cost' | 'engagement' | 'satisfaction';
    estimatedValue?: number;
    timeframe?: string;
  };
  action?: {
    label: string;
    onClick?: () => void;
    href?: string;
  };
  relatedItems?: string[];
  confidence: number;
  sources?: GroundingSource[];
  isGrounded?: boolean;
  timestamp?: string;
}

interface InsightCardProps {
  insight: Insight;
  compact?: boolean;
  onDismiss?: () => void;
  onAction?: () => void;
  className?: string;
}

const TYPE_CONFIG: Record<InsightType, {
  icon: typeof Lightbulb;
  color: string;
  bgColor: string;
  borderColor: string;
  label: string;
}> = {
  opportunity: {
    icon: Rocket,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Opportunity',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    label: 'Warning',
  },
  trend: {
    icon: TrendingUp,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    label: 'Trend',
  },
  action: {
    icon: Zap,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    label: 'Recommended Action',
  },
  anomaly: {
    icon: Target,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Anomaly',
  },
};

const PRIORITY_CONFIG: Record<InsightPriority, { label: string; color: string }> = {
  high: { label: 'High', color: 'bg-red-100 text-red-700' },
  medium: { label: 'Medium', color: 'bg-amber-100 text-amber-700' },
  low: { label: 'Low', color: 'bg-green-100 text-green-700' },
};

export function InsightCard({
  insight,
  compact = false,
  onDismiss: _onDismiss,
  onAction,
  className,
}: InsightCardProps) {
  const [expanded, setExpanded] = useState(false);
  const config = TYPE_CONFIG[insight.type];
  const priorityConfig = PRIORITY_CONFIG[insight.priority];
  const Icon = config.icon;

  const hasDetails = insight.relatedItems?.length || insight.sources?.length || insight.impact;

  return (
    <div
      className={cn(
        'rounded-xl border-2 overflow-hidden transition-all',
        config.borderColor,
        config.bgColor,
        'hover:shadow-md',
        className
      )}
    >
      {/* Header */}
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={cn('p-2 rounded-lg', config.bgColor, 'border', config.borderColor)}>
            <Icon className={cn('h-5 w-5', config.color)} />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className={cn('text-xs', config.color, config.borderColor)}>
                {config.label}
              </Badge>
              <Badge variant="secondary" className={cn('text-xs', priorityConfig.color)}>
                Priority {priorityConfig.label}
              </Badge>
              {insight.isGrounded && (
                <Badge variant="outline" className="text-xs text-green-600 border-green-300">
                  ✓ Verified
                </Badge>
              )}
            </div>

            <h4 className="font-semibold text-gray-900 mt-2">{insight.title}</h4>
            
            {!compact && (
              <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
            )}
          </div>

          {/* Confidence */}
          <div className="flex-shrink-0">
            <ConfidenceIndicator value={insight.confidence} variant="circular" size="sm" />
          </div>
        </div>

        {/* Metric */}
        {insight.metric && (
          <div className="mt-4 p-3 bg-white/60 rounded-lg flex items-center justify-between">
            <span className="text-sm text-gray-600">{insight.metric.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-gray-900">
                {insight.metric.unit === '$' && '$'}
                {insight.metric.value.toLocaleString()}
                {insight.metric.unit && insight.metric.unit !== '$' && ` ${insight.metric.unit}`}
              </span>
              {insight.metric.change !== undefined && (
                <span className={cn(
                  'flex items-center text-sm font-medium',
                  insight.metric.change >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {insight.metric.change >= 0 ? (
                    <TrendingUp className="h-4 w-4 mr-1" />
                  ) : (
                    <TrendingDown className="h-4 w-4 mr-1" />
                  )}
                  {insight.metric.change >= 0 ? '+' : ''}{insight.metric.change}%
                </span>
              )}
            </div>
          </div>
        )}

        {/* Impact Estimate */}
        {insight.impact && (
          <div className="mt-3 p-3 bg-gradient-to-r from-green-100/50 to-emerald-100/50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-800">
                Estimated Impact: 
                <span className="font-bold ml-1">
                  {insight.impact.estimatedValue !== undefined 
                    ? `$${insight.impact.estimatedValue.toLocaleString()}`
                    : 'Significant'}
                </span>
                {insight.impact.timeframe && (
                  <span className="text-green-600 ml-1">/ {insight.impact.timeframe}</span>
                )}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Expandable Details */}
      {hasDetails && !compact && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full px-4 py-2 bg-white/40 border-t border-b text-sm text-gray-600 flex items-center justify-center gap-1 hover:bg-white/60"
          >
            {expanded ? 'Hide Details' : 'View Details'}
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>

          {expanded && (
            <div className="p-4 space-y-4 animate-in fade-in slide-in-from-top-2">
              {/* Related Items */}
              {insight.relatedItems && insight.relatedItems.length > 0 && (
                <div>
                  <p className="text-xs text-gray-500 mb-2">Related Items:</p>
                  <div className="flex flex-wrap gap-2">
                    {insight.relatedItems.map((item, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Sources */}
              {insight.sources && insight.sources.length > 0 && (
                <VerifiedSourceBadge
                  sources={insight.sources}
                  isGrounded={insight.isGrounded || false}
                  showInline
                />
              )}
            </div>
          )}
        </>
      )}

      {/* Action */}
      {insight.action && (
        <div className="p-4 bg-white/40 border-t">
          <Button
            onClick={insight.action.onClick || onAction}
            className="w-full"
            variant="default"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            {insight.action.label}
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      )}
    </div>
  );
}

export default InsightCard;
