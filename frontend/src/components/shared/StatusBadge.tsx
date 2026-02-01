import { cn } from '@/lib/utils';
import { AlertCircle, BadgeCheck, Clock, PauseCircle, PlayCircle, XCircle } from 'lucide-react';

export type StatusType = 'pending' | 'running' | 'completed' | 'failed' | 'paused' | 'verified' | 'rejected' | 'skipped';

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
  showIcon?: boolean;
}

const config: Record<StatusType, { color: string; icon: any; label: string }> = {
  pending: { color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300', icon: Clock, label: 'Pending' },
  running: { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 animate-pulse', icon: PlayCircle, label: 'Running' },
  completed: { color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', icon: BadgeCheck, label: 'Completed' },
  failed: { color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200', icon: XCircle, label: 'Failed' },
  paused: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', icon: PauseCircle, label: 'Paused' },
  verified: { color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200', icon: BadgeCheck, label: 'Verified' },
  rejected: { color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200', icon: AlertCircle, label: 'Rejected' },
  skipped: { color: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-500', icon: AlertCircle, label: 'Skipped' },
};

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
  const { color, icon: Icon, label } = config[status] || config.pending;

  return (
    <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium", color, className)}>
      {showIcon && <Icon className="w-3 h-3 mr-1" />}
      {label}
    </span>
  );
}
