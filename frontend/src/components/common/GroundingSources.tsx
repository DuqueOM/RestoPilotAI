'use client';

import { Badge } from '@/components/ui/badge';
import { GroundingSource } from '@/lib/api';
import { cn } from '@/lib/utils';
import { CheckCircle2, ExternalLink, Globe, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface GroundingSourcesProps {
  sources: GroundingSource[];
  isGrounded: boolean;
  variant?: 'card' | 'inline' | 'compact';
  maxVisible?: number;
  className?: string;
}

export function GroundingSources({
  sources,
  isGrounded,
  variant = 'card',
  maxVisible = 5,
  className,
}: GroundingSourcesProps) {
  const [showAll, setShowAll] = useState(false);
  if (!sources || sources.length === 0) return null;

  const visibleSources = showAll ? sources : sources.slice(0, maxVisible);

  if (variant === 'inline') {
    return (
      <div className={cn('inline-flex items-center gap-1.5 text-xs', className)}>
        <ShieldCheck className="h-3.5 w-3.5 text-green-600" />
        <span className="text-green-700 font-medium">Verified by Google Search</span>
        <span className="text-gray-400">({sources.length} source{sources.length !== 1 ? 's' : ''})</span>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={cn('flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg border border-green-200', className)}>
        <ShieldCheck className="h-4 w-4 text-green-600 flex-shrink-0" />
        <span className="text-xs text-green-700 font-medium">Google Search Grounded</span>
        <div className="flex items-center gap-1 ml-auto">
          {sources.slice(0, 3).map((source, idx) => (
            <a
              key={idx}
              href={source.uri}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[10px] px-1.5 py-0.5 bg-white rounded border border-green-200 text-green-700 hover:bg-green-50 truncate max-w-[100px]"
              title={source.title || source.uri}
            >
              {source.title?.slice(0, 20) || new URL(source.uri).hostname}
            </a>
          ))}
          {sources.length > 3 && (
            <span className="text-[10px] text-green-600">+{sources.length - 3}</span>
          )}
        </div>
      </div>
    );
  }

  // Default: card variant
  return (
    <div className={cn('rounded-xl border border-green-200 bg-gradient-to-br from-green-50/50 to-emerald-50/30 overflow-hidden', className)}>
      <div className="flex items-center gap-2.5 px-4 py-3 border-b border-green-100">
        <div className="p-1.5 bg-green-100 rounded-lg">
          <Globe className="w-4 h-4 text-green-600" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-gray-900">Verified Sources</h4>
          <p className="text-[10px] text-gray-500">Google Search Grounding — real-time data verification</p>
        </div>
        {isGrounded && (
          <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">
            <ShieldCheck className="w-3 h-3 mr-1" />
            Verified
          </Badge>
        )}
      </div>
      <div className="px-4 py-3">
        <ul className="space-y-2">
          {visibleSources.map((source, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm group">
              <ExternalLink className="w-3.5 h-3.5 mt-0.5 text-green-500 group-hover:text-green-700 flex-shrink-0 transition-colors" />
              <a
                href={source.uri}
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-700 hover:text-green-900 hover:underline break-all text-xs leading-relaxed"
              >
                {source.title || source.uri}
              </a>
            </li>
          ))}
        </ul>
        {sources.length > maxVisible && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="text-xs text-green-600 hover:text-green-800 mt-2 font-medium"
          >
            Show {sources.length - maxVisible} more sources
          </button>
        )}
        <p className="text-[10px] text-gray-400 mt-3 flex items-center gap-1">
          <CheckCircle2 className="h-3 w-3" />
          Analysis enriched with real-time data from Google Search
        </p>
      </div>
    </div>
  );
}
