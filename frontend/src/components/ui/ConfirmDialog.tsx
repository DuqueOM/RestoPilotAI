'use client';

import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle2, Sparkles, X } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { Button } from './button';

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children?: React.ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel?: () => void;
  variant?: 'default' | 'destructive' | 'ai';
  loading?: boolean;
}

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  children,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  variant = 'default',
  loading = false,
}: ConfirmDialogProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  const handleClose = useCallback(() => {
    if (loading) return;
    onOpenChange(false);
    onCancel?.();
  }, [loading, onOpenChange, onCancel]);

  useEffect(() => {
    if (!open) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [open, handleClose]);

  if (!open) return null;

  const iconMap = {
    default: <CheckCircle2 className="h-6 w-6 text-blue-600" />,
    destructive: <AlertTriangle className="h-6 w-6 text-red-600" />,
    ai: <Sparkles className="h-6 w-6 text-purple-600" />,
  };

  const confirmBtnClass = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white',
    destructive: 'bg-red-600 hover:bg-red-700 text-white',
    ai: 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white',
  };

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === overlayRef.current) handleClose();
      }}
      style={{ animation: 'rp-fade-in 0.15s ease-out' }}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden"
        style={{ animation: 'rp-slide-up 0.2s ease-out' }}
      >
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className={cn(
              'p-2.5 rounded-xl flex-shrink-0',
              variant === 'default' && 'bg-blue-50',
              variant === 'destructive' && 'bg-red-50',
              variant === 'ai' && 'bg-purple-50',
            )}>
              {iconMap[variant]}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              {description && (
                <p className="text-sm text-gray-600 mt-1">{description}</p>
              )}
            </div>
            <button
              onClick={handleClose}
              className="p-1 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {children && (
            <div className="mt-4 pl-[52px]">{children}</div>
          )}
        </div>

        <div className="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 border-t">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={loading}
          >
            {cancelLabel}
          </Button>
          <Button
            onClick={onConfirm}
            disabled={loading}
            className={cn(confirmBtnClass[variant])}
          >
            {loading && (
              <span className="mr-2 h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block" />
            )}
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
