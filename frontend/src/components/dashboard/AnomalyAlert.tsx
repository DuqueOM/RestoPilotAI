'use client';

import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
    AlertOctagon,
    AlertTriangle,
    Bell,
    CheckCircle2,
    ChevronRight,
    Clock,
    Info,
    TrendingDown,
    TrendingUp,
    X,
    Zap
} from 'lucide-react';
import { useState } from 'react';

export type AnomalySeverity = 'critical' | 'warning' | 'info';
export type AnomalyStatus = 'active' | 'acknowledged' | 'resolved' | 'investigating';

export interface Anomaly {
  id: string;
  severity: AnomalySeverity;
  status: AnomalyStatus;
  title: string;
  description: string;
  metric: {
    name: string;
    current: number;
    expected: number;
    deviation: number;
    unit?: string;
  };
  detectedAt: string;
  affectedItems?: string[];
  possibleCauses?: string[];
  suggestedActions?: string[];
  confidence: number;
  autoResolvable?: boolean;
}

interface AnomalyAlertProps {
  anomaly: Anomaly;
  onAcknowledge?: () => void;
  onResolve?: () => void;
  onInvestigate?: () => void;
  onDismiss?: () => void;
  compact?: boolean;
  className?: string;
}

const SEVERITY_CONFIG: Record<AnomalySeverity, {
  icon: typeof AlertOctagon;
  color: string;
  bgColor: string;
  borderColor: string;
  label: string;
  pulseColor: string;
}> = {
  critical: {
    icon: AlertOctagon,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-300',
    label: 'Critical',
    pulseColor: 'bg-red-500',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-300',
    label: 'Warning',
    pulseColor: 'bg-amber-500',
  },
  info: {
    icon: Info,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-300',
    label: 'Info',
    pulseColor: 'bg-blue-500',
  },
};

const STATUS_CONFIG: Record<AnomalyStatus, { label: string; color: string; icon: typeof Bell }> = {
  active: { label: 'Active', color: 'bg-red-100 text-red-700', icon: Bell },
  acknowledged: { label: 'Acknowledged', color: 'bg-amber-100 text-amber-700', icon: Clock },
  investigating: { label: 'Investigating', color: 'bg-blue-100 text-blue-700', icon: Zap },
  resolved: { label: 'Resolved', color: 'bg-green-100 text-green-700', icon: CheckCircle2 },
};

export function AnomalyAlert({
  anomaly,
  onAcknowledge,
  onResolve,
  onInvestigate,
  onDismiss,
  compact = false,
  className,
}: AnomalyAlertProps) {
  const [expanded, setExpanded] = useState(false);
  const severity = SEVERITY_CONFIG[anomaly.severity];
  const status = STATUS_CONFIG[anomaly.status];
  const Icon = severity.icon;
  const StatusIcon = status.icon;

  const isPositiveDeviation = anomaly.metric.deviation > 0;
  const deviationPercent = Math.abs(anomaly.metric.deviation);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      day: 'numeric',
      month: 'short',
    });
  };

  return (
    <div
      className={cn(
        'rounded-xl border-2 overflow-hidden transition-all',
        severity.borderColor,
        anomaly.status === 'active' && 'shadow-lg',
        className
      )}
    >
      {/* Header with pulse indicator */}
      <div className={cn('p-4', severity.bgColor)}>
        <div className="flex items-start gap-3">
          {/* Icon with pulse for active alerts */}
          <div className="relative">
            <div className={cn('p-2 rounded-lg', severity.bgColor, 'border', severity.borderColor)}>
              <Icon className={cn('h-5 w-5', severity.color)} />
            </div>
            {anomaly.status === 'active' && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className={cn(
                  'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
                  severity.pulseColor
                )} />
                <span className={cn('relative inline-flex rounded-full h-3 w-3', severity.pulseColor)} />
              </span>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className={cn('text-xs', severity.color, severity.borderColor)}>
                {severity.label}
              </Badge>
              <Badge className={cn('text-xs', status.color)}>
                <StatusIcon className="h-3 w-3 mr-1" />
                {status.label}
              </Badge>
            </div>

            <h4 className="font-semibold text-gray-900 mt-2">{anomaly.title}</h4>
            
            {!compact && (
              <p className="text-sm text-gray-600 mt-1">{anomaly.description}</p>
            )}

            {/* Timestamp */}
            <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Detected: {formatTime(anomaly.detectedAt)}
            </p>
          </div>

          {/* Confidence & Dismiss */}
          <div className="flex flex-col items-end gap-2">
            <ConfidenceIndicator value={anomaly.confidence} variant="badge" size="sm" />
            {onDismiss && anomaly.status !== 'active' && (
              <button
                onClick={onDismiss}
                className="p-1 hover:bg-black/10 rounded text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Metric Deviation */}
        <div className="mt-4 p-3 bg-white/60 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{anomaly.metric.name}</span>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-xs text-gray-500">Expected</p>
                <p className="font-medium text-gray-700">
                  {anomaly.metric.unit === '$' && '$'}
                  {anomaly.metric.expected.toLocaleString()}
                  {anomaly.metric.unit && anomaly.metric.unit !== '$' && ` ${anomaly.metric.unit}`}
                </p>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-400" />
              <div className="text-right">
                <p className="text-xs text-gray-500">Current</p>
                <p className={cn(
                  'font-bold',
                  isPositiveDeviation ? 'text-green-600' : 'text-red-600'
                )}>
                  {anomaly.metric.unit === '$' && '$'}
                  {anomaly.metric.current.toLocaleString()}
                  {anomaly.metric.unit && anomaly.metric.unit !== '$' && ` ${anomaly.metric.unit}`}
                </p>
              </div>
              <div className={cn(
                'flex items-center px-2 py-1 rounded',
                isPositiveDeviation ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              )}>
                {isPositiveDeviation ? (
                  <TrendingUp className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 mr-1" />
                )}
                <span className="font-bold">
                  {isPositiveDeviation ? '+' : '-'}{deviationPercent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Expandable Details */}
      {!compact && (anomaly.possibleCauses?.length || anomaly.suggestedActions?.length || anomaly.affectedItems?.length) && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full px-4 py-2 bg-white/40 border-t text-sm text-gray-600 flex items-center justify-center gap-1 hover:bg-white/60"
          >
            {expanded ? 'Hide Analysis' : 'View Gemini Analysis'}
            <ChevronRight className={cn('h-4 w-4 transition-transform', expanded && 'rotate-90')} />
          </button>

          {expanded && (
            <div className="p-4 space-y-4 bg-white/30 animate-in fade-in slide-in-from-top-2">
              {/* Affected Items */}
              {anomaly.affectedItems && anomaly.affectedItems.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-2">📦 Affected Items:</p>
                  <div className="flex flex-wrap gap-2">
                    {anomaly.affectedItems.map((item, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Possible Causes */}
              {anomaly.possibleCauses && anomaly.possibleCauses.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-2">🔍 Possible Causes:</p>
                  <ul className="space-y-1">
                    {anomaly.possibleCauses.map((cause, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-amber-500">•</span>
                        {cause}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Suggested Actions */}
              {anomaly.suggestedActions && anomaly.suggestedActions.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-2">💡 Suggested Actions:</p>
                  <ul className="space-y-1">
                    {anomaly.suggestedActions.map((action, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-green-500">{idx + 1}.</span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Actions */}
      {anomaly.status === 'active' && (onAcknowledge || onInvestigate || onResolve) && (
        <div className="p-4 bg-white/40 border-t flex items-center gap-2 flex-wrap">
          {onAcknowledge && (
            <Button variant="outline" size="sm" onClick={onAcknowledge}>
              Acknowledge
            </Button>
          )}
          {onInvestigate && (
            <Button variant="outline" size="sm" onClick={onInvestigate}>
              <Zap className="h-4 w-4 mr-1" />
              Investigate
            </Button>
          )}
          {onResolve && anomaly.autoResolvable && (
            <Button size="sm" onClick={onResolve}>
              <CheckCircle2 className="h-4 w-4 mr-1" />
              Auto-resolve
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

export default AnomalyAlert;
