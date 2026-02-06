'use client';

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle2, HelpCircle, Info, ShieldAlert, ShieldCheck } from 'lucide-react';

interface ConfidenceIndicatorProps {
  value: number; // 0-1
  label?: string;
  showTooltip?: boolean;
  showLabel?: boolean;
  showPercentage?: boolean;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'bar' | 'circular' | 'badge' | 'minimal';
  className?: string;
}

const SIZE_CONFIG = {
  xs: { bar: 'h-1', text: 'text-xs', icon: 'w-3 h-3', circular: 'w-8 h-8' },
  sm: { bar: 'h-1.5', text: 'text-xs', icon: 'w-3.5 h-3.5', circular: 'w-10 h-10' },
  md: { bar: 'h-2', text: 'text-sm', icon: 'w-4 h-4', circular: 'w-12 h-12' },
  lg: { bar: 'h-3', text: 'text-base', icon: 'w-5 h-5', circular: 'w-16 h-16' },
};

const getConfidenceConfig = (value: number) => {
  if (value >= 0.85) {
    return {
      level: 'high',
      label: 'High Confidence',
      description: 'Analysis is strongly supported by verified data.',
      color: 'text-green-600',
      bgColor: 'bg-green-500',
      bgLight: 'bg-green-100',
      borderColor: 'border-green-500',
      icon: ShieldCheck,
      emoji: '✅',
    };
  }
  if (value >= 0.7) {
    return {
      level: 'good',
      label: 'Good Confidence',
      description: 'Analysis is well supported, with some estimated data.',
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-500',
      bgLight: 'bg-emerald-100',
      borderColor: 'border-emerald-500',
      icon: CheckCircle2,
      emoji: '👍',
    };
  }
  if (value >= 0.5) {
    return {
      level: 'moderate',
      label: 'Moderate Confidence',
      description: 'Analysis includes some estimates. Consider manual verification.',
      color: 'text-amber-600',
      bgColor: 'bg-amber-500',
      bgLight: 'bg-amber-100',
      borderColor: 'border-amber-500',
      icon: Info,
      emoji: '⚠️',
    };
  }
  if (value >= 0.3) {
    return {
      level: 'low',
      label: 'Low Confidence',
      description: 'Limited data available. Manual verification recommended.',
      color: 'text-orange-600',
      bgColor: 'bg-orange-500',
      bgLight: 'bg-orange-100',
      borderColor: 'border-orange-500',
      icon: AlertTriangle,
      emoji: '⚡',
    };
  }
  return {
    level: 'very_low',
    label: 'Very Low Confidence',
    description: 'Preliminary analysis with very limited data. Use with caution.',
    color: 'text-red-600',
    bgColor: 'bg-red-500',
    bgLight: 'bg-red-100',
    borderColor: 'border-red-500',
    icon: ShieldAlert,
    emoji: '🔴',
  };
};

function BarVariant({
  value,
  config,
  sizeConfig,
  showPercentage,
  label,
}: {
  value: number;
  config: ReturnType<typeof getConfidenceConfig>;
  sizeConfig: typeof SIZE_CONFIG.md;
  showPercentage?: boolean;
  label?: string;
}) {
  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-1">
          {label && (
            <span className={cn('font-medium', sizeConfig.text, config.color)}>
              {label}
            </span>
          )}
          {showPercentage && (
            <span className={cn('font-medium', sizeConfig.text, config.color)}>
              {(value * 100).toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div className={cn('w-full rounded-full overflow-hidden', sizeConfig.bar, config.bgLight)}>
        <div
          className={cn('h-full rounded-full transition-all duration-500', config.bgColor)}
          style={{ width: `${Math.max(value * 100, 2)}%` }}
        />
      </div>
    </div>
  );
}

function CircularVariant({
  value,
  config,
  sizeConfig,
  showPercentage,
}: {
  value: number;
  config: ReturnType<typeof getConfidenceConfig>;
  sizeConfig: typeof SIZE_CONFIG.md;
  showPercentage?: boolean;
}) {
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDashoffset = circumference - (value * circumference);

  return (
    <div className={cn('relative', sizeConfig.circular)}>
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          className={config.bgLight}
          strokeWidth="8"
          stroke="currentColor"
        />
        {/* Progress circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          className={config.color}
          strokeWidth="8"
          stroke="currentColor"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
      </svg>
      {showPercentage && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn('font-bold', sizeConfig.text, config.color)}>
            {(value * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  );
}

function BadgeVariant({
  value,
  config,
  sizeConfig,
}: {
  value: number;
  config: ReturnType<typeof getConfidenceConfig>;
  sizeConfig: typeof SIZE_CONFIG.md;
}) {
  const Icon = config.icon;

  return (
    <div className={cn(
      'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border',
      config.bgLight,
      config.borderColor,
      config.color
    )}>
      <Icon className={sizeConfig.icon} />
      <span className={cn('font-medium', sizeConfig.text)}>
        {(value * 100).toFixed(0)}%
      </span>
    </div>
  );
}

function MinimalVariant({
  value,
  config,
  sizeConfig,
}: {
  value: number;
  config: ReturnType<typeof getConfidenceConfig>;
  sizeConfig: typeof SIZE_CONFIG.md;
}) {
  const Icon = config.icon;

  return (
    <div className={cn('inline-flex items-center gap-1', config.color)}>
      <Icon className={sizeConfig.icon} />
      <span className={cn('font-medium', sizeConfig.text)}>
        {(value * 100).toFixed(0)}%
      </span>
    </div>
  );
}

export function ConfidenceIndicator({
  value,
  label,
  showTooltip = true,
  showLabel = false,
  showPercentage = true,
  size = 'md',
  variant = 'bar',
  className,
}: ConfidenceIndicatorProps) {
  // Clamp value between 0 and 1
  const clampedValue = Math.max(0, Math.min(1, value));
  const config = getConfidenceConfig(clampedValue);
  const sizeConfig = SIZE_CONFIG[size];

  const renderVariant = () => {
    switch (variant) {
      case 'circular':
        return (
          <CircularVariant
            value={clampedValue}
            config={config}
            sizeConfig={sizeConfig}
            showPercentage={showPercentage}
          />
        );
      case 'badge':
        return (
          <BadgeVariant
            value={clampedValue}
            config={config}
            sizeConfig={sizeConfig}
          />
        );
      case 'minimal':
        return (
          <MinimalVariant
            value={clampedValue}
            config={config}
            sizeConfig={sizeConfig}
          />
        );
      default:
        return (
          <BarVariant
            value={clampedValue}
            config={config}
            sizeConfig={sizeConfig}
            showPercentage={showPercentage}
            label={showLabel ? (label || config.label) : undefined}
          />
        );
    }
  };

  if (!showTooltip) {
    return <div className={className}>{renderVariant()}</div>;
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className={cn('cursor-help', className)}>{renderVariant()}</div>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <config.icon className={cn('w-4 h-4', config.color)} />
              <span className={cn('font-semibold', config.color)}>
                {config.label}
              </span>
            </div>
            <p className="text-sm text-gray-600">{config.description}</p>
            <p className="text-xs text-gray-500 pt-1 border-t border-gray-100">
              Score: {(clampedValue * 100).toFixed(1)}%
            </p>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export function ConfidenceLabel({
  value,
  showIcon = true,
  className,
}: {
  value: number;
  showIcon?: boolean;
  className?: string;
}) {
  const config = getConfidenceConfig(Math.max(0, Math.min(1, value)));
  const Icon = config.icon;

  return (
    <span className={cn('inline-flex items-center gap-1', config.color, className)}>
      {showIcon && <Icon className="w-4 h-4" />}
      <span className="font-medium">{config.label}</span>
    </span>
  );
}

export default ConfidenceIndicator;
