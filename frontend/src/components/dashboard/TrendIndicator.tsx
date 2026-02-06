'use client';

import { cn } from '@/lib/utils';
import {
    ArrowDown,
    ArrowRight,
    ArrowUp,
    Minus,
    TrendingDown,
    TrendingUp,
} from 'lucide-react';

export type TrendDirection = 'up' | 'down' | 'stable' | 'volatile';

export interface TrendData {
  current: number;
  previous: number;
  change: number;
  changePercent: number;
  direction: TrendDirection;
  period?: string;
  forecast?: number;
  forecastConfidence?: number;
}

interface TrendIndicatorProps {
  value: number;
  previousValue?: number;
  changePercent?: number;
  direction?: TrendDirection;
  period?: string;
  forecast?: number;
  unit?: string;
  prefix?: string;
  positiveIsGood?: boolean;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'badge' | 'inline' | 'detailed';
  showValue?: boolean;
  showPercentage?: boolean;
  showForecast?: boolean;
  className?: string;
}

const SIZE_CONFIG = {
  xs: { icon: 'h-3 w-3', text: 'text-xs', value: 'text-sm' },
  sm: { icon: 'h-4 w-4', text: 'text-sm', value: 'text-base' },
  md: { icon: 'h-5 w-5', text: 'text-base', value: 'text-lg' },
  lg: { icon: 'h-6 w-6', text: 'text-lg', value: 'text-2xl' },
};

export function TrendIndicator({
  value,
  previousValue,
  changePercent,
  direction,
  period,
  forecast,
  unit = '',
  prefix = '',
  positiveIsGood = true,
  size = 'md',
  variant = 'default',
  showValue = true,
  showPercentage = true,
  showForecast = false,
  className,
}: TrendIndicatorProps) {
  // Calculate change if not provided
  const calculatedChange = changePercent ?? (
    previousValue !== undefined && previousValue !== 0
      ? ((value - previousValue) / Math.abs(previousValue)) * 100
      : 0
  );

  // Determine direction if not provided
  const calculatedDirection = direction ?? (
    calculatedChange > 1 ? 'up' :
    calculatedChange < -1 ? 'down' :
    'stable'
  );

  const sizeConfig = SIZE_CONFIG[size];

  // Determine if the change is positive (good or bad based on context)
  const isPositive = calculatedDirection === 'up';
  const isNegative = calculatedDirection === 'down';
  const isGood = positiveIsGood ? isPositive : isNegative;
  const isBad = positiveIsGood ? isNegative : isPositive;

  const colorClass = isGood ? 'text-green-600' : isBad ? 'text-red-600' : 'text-gray-500';
  const bgColorClass = isGood ? 'bg-green-100' : isBad ? 'bg-red-100' : 'bg-gray-100';

  const TrendIcon = calculatedDirection === 'up' ? TrendingUp :
                    calculatedDirection === 'down' ? TrendingDown :
                    Minus;

  const ArrowIcon = calculatedDirection === 'up' ? ArrowUp :
                    calculatedDirection === 'down' ? ArrowDown :
                    ArrowRight;

  const formatValue = (v: number) => {
    if (Math.abs(v) >= 1000000) {
      return `${(v / 1000000).toFixed(1)}M`;
    }
    if (Math.abs(v) >= 1000) {
      return `${(v / 1000).toFixed(1)}K`;
    }
    return v.toLocaleString();
  };

  if (variant === 'badge') {
    return (
      <span
        className={cn(
          'inline-flex items-center gap-1 px-2 py-0.5 rounded-full',
          bgColorClass,
          colorClass,
          sizeConfig.text,
          'font-medium',
          className
        )}
      >
        <ArrowIcon className={sizeConfig.icon} />
        {showPercentage && (
          <span>{calculatedChange >= 0 ? '+' : ''}{calculatedChange.toFixed(1)}%</span>
        )}
      </span>
    );
  }

  if (variant === 'inline') {
    return (
      <span className={cn('inline-flex items-center gap-1', colorClass, sizeConfig.text, className)}>
        <TrendIcon className={sizeConfig.icon} />
        {showPercentage && (
          <span className="font-medium">
            {calculatedChange >= 0 ? '+' : ''}{calculatedChange.toFixed(1)}%
          </span>
        )}
        {period && <span className="text-gray-400 ml-1">vs {period}</span>}
      </span>
    );
  }

  if (variant === 'detailed') {
    return (
      <div className={cn('space-y-2', className)}>
        {/* Current Value */}
        {showValue && (
          <div className="flex items-baseline gap-2">
            <span className={cn('font-bold', sizeConfig.value)}>
              {prefix}{formatValue(value)}{unit}
            </span>
            <span className={cn('flex items-center gap-1', colorClass, sizeConfig.text)}>
              <ArrowIcon className={sizeConfig.icon} />
              {showPercentage && (
                <span className="font-medium">
                  {calculatedChange >= 0 ? '+' : ''}{calculatedChange.toFixed(1)}%
                </span>
              )}
            </span>
          </div>
        )}

        {/* Comparison */}
        {previousValue !== undefined && (
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>Previous: {prefix}{formatValue(previousValue)}{unit}</span>
            {period && <span className="text-gray-400">({period})</span>}
          </div>
        )}

        {/* Forecast */}
        {showForecast && forecast !== undefined && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-500">Forecast:</span>
            <span className="font-medium text-purple-600">
              {prefix}{formatValue(forecast)}{unit}
            </span>
            <TrendingUp className="h-4 w-4 text-purple-400" />
          </div>
        )}
      </div>
    );
  }

  // Default variant
  return (
    <div className={cn('flex items-center gap-2', className)}>
      {showValue && (
        <span className={cn('font-bold', sizeConfig.value)}>
          {prefix}{formatValue(value)}{unit}
        </span>
      )}
      <div className={cn('flex items-center gap-1', colorClass, sizeConfig.text)}>
        <TrendIcon className={sizeConfig.icon} />
        {showPercentage && (
          <span className="font-medium">
            {calculatedChange >= 0 ? '+' : ''}{calculatedChange.toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  );
}

export function TrendSparkline({
  data,
  width = 100,
  height = 30,
  color = 'currentColor',
  showDots = false,
  className,
}: {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  showDots?: boolean;
  className?: string;
}) {
  if (data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return { x, y, value };
  });

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ');

  const trend = data[data.length - 1] > data[0] ? 'up' : data[data.length - 1] < data[0] ? 'down' : 'stable';
  const trendColor = trend === 'up' ? '#22c55e' : trend === 'down' ? '#ef4444' : '#6b7280';

  return (
    <svg
      width={width}
      height={height}
      className={className}
      viewBox={`0 0 ${width} ${height}`}
    >
      <path
        d={pathD}
        fill="none"
        stroke={color === 'currentColor' ? trendColor : color}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {showDots && points.map((p, i) => (
        <circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={i === points.length - 1 ? 3 : 2}
          fill={color === 'currentColor' ? trendColor : color}
          className={i === points.length - 1 ? 'opacity-100' : 'opacity-50'}
        />
      ))}
    </svg>
  );
}

export default TrendIndicator;
