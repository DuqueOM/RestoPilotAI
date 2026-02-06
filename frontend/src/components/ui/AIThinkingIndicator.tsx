'use client';

import { cn } from '@/lib/utils';
import { Brain, Sparkles } from 'lucide-react';

interface AIThinkingIndicatorProps {
  active?: boolean;
  label?: string;
  variant?: 'dot' | 'bar' | 'full';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function AIThinkingIndicator({
  active = true,
  label,
  variant = 'dot',
  size = 'md',
  className,
}: AIThinkingIndicatorProps) {
  if (!active) return null;

  const sizeConfig = {
    sm: { dot: 'h-2 w-2', icon: 'h-3 w-3', text: 'text-xs', bar: 'h-1', padding: 'px-2 py-1' },
    md: { dot: 'h-2.5 w-2.5', icon: 'h-4 w-4', text: 'text-sm', bar: 'h-1.5', padding: 'px-3 py-1.5' },
    lg: { dot: 'h-3 w-3', icon: 'h-5 w-5', text: 'text-base', bar: 'h-2', padding: 'px-4 py-2' },
  }[size];

  if (variant === 'dot') {
    return (
      <span className={cn('relative inline-flex', className)} title={label || 'AI is processing'}>
        <span className={cn('rounded-full bg-purple-500', sizeConfig.dot)} />
        <span className={cn('absolute rounded-full bg-purple-400 animate-ping', sizeConfig.dot)} />
      </span>
    );
  }

  if (variant === 'bar') {
    return (
      <div className={cn('w-full rounded-full overflow-hidden bg-purple-100', sizeConfig.bar, className)}>
        <div
          className={cn('h-full bg-gradient-to-r from-purple-500 via-indigo-500 to-purple-500 rounded-full')}
          style={{
            width: '40%',
            animation: 'rp-shimmer 1.5s ease-in-out infinite',
          }}
        />
      </div>
    );
  }

  // variant === 'full'
  return (
    <div className={cn(
      'inline-flex items-center gap-2 rounded-full bg-purple-50 border border-purple-200',
      sizeConfig.padding,
      className,
    )}>
      <div className="relative">
        <Brain className={cn('text-purple-600', sizeConfig.icon)} />
        <span className="absolute -top-0.5 -right-0.5 h-1.5 w-1.5 rounded-full bg-purple-500 animate-ping" />
      </div>
      <span className={cn('font-medium text-purple-700', sizeConfig.text)}>
        {label || 'AI Thinking...'}
      </span>
      <Sparkles className={cn('text-purple-400 animate-pulse', sizeConfig.icon)} />
    </div>
  );
}

export default AIThinkingIndicator;
