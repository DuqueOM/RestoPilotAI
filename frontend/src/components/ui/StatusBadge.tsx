'use client';

import { cn } from '@/lib/utils';
import { CheckCircle2, AlertCircle, Clock, Loader2, XCircle, Sparkles } from 'lucide-react';
import React from 'react';

export type StatusType = 'completed' | 'running' | 'pending' | 'error' | 'ai_active' | 'idle';

interface StatusBadgeProps {
  status: StatusType;
  label?: string;
  showIcon?: boolean;
  showDot?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const STATUS_CONFIG: Record<StatusType, {
  bg: string;
  text: string;
  border: string;
  dotClass: string;
  icon: React.ReactNode;
  defaultLabel: string;
}> = {
  completed: {
    bg: 'bg-green-50',
    text: 'text-green-700',
    border: 'border-green-200',
    dotClass: 'rp-status-dot rp-status-dot-active',
    icon: <CheckCircle2 className="h-3.5 w-3.5" />,
    defaultLabel: 'Completed',
  },
  running: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    dotClass: 'rp-status-dot rp-status-dot-running',
    icon: <Loader2 className="h-3.5 w-3.5 animate-spin" />,
    defaultLabel: 'Running',
  },
  pending: {
    bg: 'bg-gray-50',
    text: 'text-gray-600',
    border: 'border-gray-200',
    dotClass: 'rp-status-dot bg-gray-300',
    icon: <Clock className="h-3.5 w-3.5" />,
    defaultLabel: 'Pending',
  },
  error: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    dotClass: 'rp-status-dot rp-status-dot-error',
    icon: <XCircle className="h-3.5 w-3.5" />,
    defaultLabel: 'Error',
  },
  ai_active: {
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    border: 'border-purple-200',
    dotClass: 'rp-status-dot rp-status-dot-running',
    icon: <Sparkles className="h-3.5 w-3.5" />,
    defaultLabel: 'AI Processing',
  },
  idle: {
    bg: 'bg-gray-50',
    text: 'text-gray-500',
    border: 'border-gray-100',
    dotClass: 'rp-status-dot bg-gray-300',
    icon: <AlertCircle className="h-3.5 w-3.5" />,
    defaultLabel: 'Idle',
  },
};

const SIZE_CONFIG = {
  sm: 'px-2 py-0.5 text-xs gap-1',
  md: 'px-2.5 py-1 text-xs gap-1.5',
  lg: 'px-3 py-1.5 text-sm gap-2',
};

export function StatusBadge({ 
  status, 
  label, 
  showIcon = true, 
  showDot = false, 
  size = 'md',
  className 
}: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const displayLabel = label || config.defaultLabel;

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-medium',
        config.bg,
        config.text,
        config.border,
        SIZE_CONFIG[size],
        className
      )}
    >
      {showDot && <span className={config.dotClass} />}
      {showIcon && !showDot && config.icon}
      {displayLabel}
    </span>
  );
}

export default StatusBadge;
