'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import {
    CheckCircle2,
    ExternalLink,
    Globe,
    Info,
    ShieldCheck,
    XCircle,
} from 'lucide-react';

export interface GroundingSource {
  url: string;
  title: string;
  domain?: string;
  snippet?: string;
  accessDate?: string;
  relevanceScore?: number;
  verified?: boolean;
}

interface VerifiedSourceBadgeProps {
  sources: GroundingSource[];
  isGrounded: boolean;
  groundingScore?: number;
  showInline?: boolean;
  maxSourcesInline?: number;
  className?: string;
}

export function VerifiedSourceBadge({
  sources,
  isGrounded,
  groundingScore,
  showInline = false,
  maxSourcesInline = 2,
  className,
}: VerifiedSourceBadgeProps) {
  if (!sources || sources.length === 0) {
    return (
      <Badge 
        variant="outline" 
        className={cn('text-gray-500 border-gray-300', className)}
      >
        <Info className="w-3 h-3 mr-1" />
        No verified sources
      </Badge>
    );
  }

  const getDomainFromUrl = (url: string): string => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Inline display for compact mode
  if (showInline) {
    const displayedSources = sources.slice(0, maxSourcesInline);
    const remainingCount = sources.length - maxSourcesInline;

    return (
      <div className={cn('flex flex-wrap items-center gap-2', className)}>
        <Badge 
          variant="outline" 
          className={cn(
            'text-green-600 border-green-300 bg-green-50',
            isGrounded && 'border-green-400'
          )}
        >
          {isGrounded ? (
            <ShieldCheck className="w-3 h-3 mr-1" />
          ) : (
            <CheckCircle2 className="w-3 h-3 mr-1" />
          )}
          {sources.length} source{sources.length !== 1 ? 's' : ''}
        </Badge>
        
        {displayedSources.map((source, idx) => (
          <a
            key={idx}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
          >
            <Globe className="w-3 h-3" />
            {source.domain || getDomainFromUrl(source.url)}
          </a>
        ))}
        
        {remainingCount > 0 && (
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                +{remainingCount} more
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <SourcesList sources={sources} />
            </PopoverContent>
          </Popover>
        )}
      </div>
    );
  }

  // Full popover display
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Badge 
          variant="outline" 
          className={cn(
            'cursor-pointer transition-colors',
            isGrounded 
              ? 'text-green-600 border-green-400 bg-green-50 hover:bg-green-100' 
              : 'text-blue-600 border-blue-300 hover:bg-blue-50',
            className
          )}
        >
          {isGrounded ? (
            <ShieldCheck className="w-3 h-3 mr-1" />
          ) : (
            <Globe className="w-3 h-3 mr-1" />
          )}
          ✓ Verified with {sources.length} source{sources.length !== 1 ? 's' : ''}
          {groundingScore !== undefined && (
            <span className={cn('ml-1', getScoreColor(groundingScore))}>
              ({(groundingScore * 100).toFixed(0)}%)
            </span>
          )}
        </Badge>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="start">
        <div className="p-4 border-b bg-gradient-to-r from-green-50 to-emerald-50">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck className="w-5 h-5 text-green-600" />
            <h4 className="font-semibold text-green-800">Verified Sources</h4>
          </div>
          <p className="text-sm text-gray-600">
            This analysis is backed by information from Google Search Grounding.
          </p>
          
          {groundingScore !== undefined && (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-xs text-gray-600">Verification score:</span>
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={cn('h-full rounded-full', getScoreBg(groundingScore))}
                  style={{ width: `${groundingScore * 100}%` }}
                />
              </div>
              <span className={cn('text-xs font-medium', getScoreColor(groundingScore))}>
                {(groundingScore * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
        
        <SourcesList sources={sources} />
        
        <div className="p-3 bg-gray-50 border-t">
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Info className="w-3 h-3" />
            Data enriched in real-time with Gemini 3 + Google Search
          </p>
        </div>
      </PopoverContent>
    </Popover>
  );
}

function SourcesList({ sources }: { sources: GroundingSource[] }) {
  const getDomainFromUrl = (url: string): string => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  return (
    <div className="max-h-64 overflow-y-auto">
      <ul className="divide-y divide-gray-100">
        {sources.map((source, idx) => (
          <li key={idx} className="p-3 hover:bg-gray-50 transition-colors">
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block group"
            >
              <div className="flex items-start gap-2">
                <ExternalLink className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0 group-hover:text-blue-700" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-blue-600 group-hover:text-blue-800 group-hover:underline truncate">
                    {source.title || getDomainFromUrl(source.url)}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {source.domain || getDomainFromUrl(source.url)}
                  </p>
                  
                  {source.snippet && (
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {source.snippet}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-3 mt-2">
                    {source.verified !== undefined && (
                      <span className={cn(
                        'inline-flex items-center gap-1 text-xs',
                        source.verified ? 'text-green-600' : 'text-gray-500'
                      )}>
                        {source.verified ? (
                          <CheckCircle2 className="w-3 h-3" />
                        ) : (
                          <XCircle className="w-3 h-3" />
                        )}
                        {source.verified ? 'Verified' : 'Unverified'}
                      </span>
                    )}
                    
                    {source.relevanceScore !== undefined && (
                      <span className="text-xs text-gray-500">
                        Relevance: {(source.relevanceScore * 100).toFixed(0)}%
                      </span>
                    )}
                    
                    {source.accessDate && (
                      <span className="text-xs text-gray-400">
                        {new Date(source.accessDate).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default VerifiedSourceBadge;
