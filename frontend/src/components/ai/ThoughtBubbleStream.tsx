'use client';

import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
    Brain,
    CheckCircle2,
    ChevronDown,
    ChevronUp,
    Clock,
    Loader2,
    Sparkles,
    Target,
    TrendingUp,
    Zap,
} from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

export interface ThoughtBubble {
  id: string;
  step: number;
  type: 'analyzing' | 'calculating' | 'comparing' | 'searching' | 'generating' | 'verifying' | 'concluding';
  title: string;
  details: string[];
  confidence?: number;
  timestamp: number;
  status: 'active' | 'completed' | 'pending';
  thinkingLevel?: 'QUICK' | 'STANDARD' | 'DEEP' | 'EXHAUSTIVE';
  model?: string;
  tokensUsed?: number;
  groundingSources?: string[];
}

export interface ThoughtStreamData {
  taskId: string;
  totalSteps: number;
  currentStep: number;
  overallProgress: number;
  thoughts: ThoughtBubble[];
  status: 'idle' | 'running' | 'completed' | 'error';
  estimatedTimeRemaining?: number;
}

interface ThoughtBubbleStreamProps {
  taskId: string;
  sessionId: string;
  onComplete?: (results: Record<string, unknown>) => void;
  onError?: (error: string) => void;
  className?: string;
  compact?: boolean;
}

const TYPE_CONFIG: Record<ThoughtBubble['type'], { icon: typeof Brain; color: string; bgColor: string; label: string }> = {
  analyzing: { icon: Brain, color: 'text-purple-600', bgColor: 'bg-purple-50', label: 'Analyzing' },
  calculating: { icon: TrendingUp, color: 'text-blue-600', bgColor: 'bg-blue-50', label: 'Calculating' },
  comparing: { icon: Target, color: 'text-orange-600', bgColor: 'bg-orange-50', label: 'Comparing' },
  searching: { icon: Sparkles, color: 'text-green-600', bgColor: 'bg-green-50', label: 'Searching' },
  generating: { icon: Zap, color: 'text-yellow-600', bgColor: 'bg-yellow-50', label: 'Generating' },
  verifying: { icon: CheckCircle2, color: 'text-emerald-600', bgColor: 'bg-emerald-50', label: 'Verifying' },
  concluding: { icon: Target, color: 'text-indigo-600', bgColor: 'bg-indigo-50', label: 'Concluding' },
};

const THINKING_LEVEL_CONFIG: Record<string, { label: string; color: string }> = {
  QUICK: { label: 'Quick', color: 'bg-green-100 text-green-800' },
  STANDARD: { label: 'Standard', color: 'bg-blue-100 text-blue-800' },
  DEEP: { label: 'Deep', color: 'bg-purple-100 text-purple-800' },
  EXHAUSTIVE: { label: 'Exhaustive', color: 'bg-red-100 text-red-800' },
};

export function ThoughtBubbleStream({
  taskId,
  sessionId,
  onComplete,
  onError,
  className,
  compact = false,
}: ThoughtBubbleStreamProps) {
  const [streamData, setStreamData] = useState<ThoughtStreamData>({
    taskId,
    totalSteps: 0,
    currentStep: 0,
    overallProgress: 0,
    thoughts: [],
    status: 'idle',
  });
  const [expanded, setExpanded] = useState(true);
  const [expandedThoughts, setExpandedThoughts] = useState<Set<string>>(new Set());

  const toggleThought = (id: string) => {
    setExpandedThoughts(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const connectToStream = useCallback(async () => {
    const API_URL = '';
    
    try {
      setStreamData(prev => ({ ...prev, status: 'running' }));
      
      const eventSource = new EventSource(
        `${API_URL}/api/v1/marathon/stream/${taskId}?session_id=${sessionId}`
      );

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'thought') {
            const thought: ThoughtBubble = {
              id: data.id || `thought-${Date.now()}`,
              step: data.step || streamData.currentStep + 1,
              type: data.thought_type || 'analyzing',
              title: data.title || 'Processing...',
              details: data.details || [],
              confidence: data.confidence,
              timestamp: Date.now(),
              status: 'active',
              thinkingLevel: data.thinking_level,
              model: data.model,
              tokensUsed: data.tokens_used,
              groundingSources: data.grounding_sources,
            };

            setStreamData(prev => ({
              ...prev,
              currentStep: thought.step,
              thoughts: [...prev.thoughts.map(t => 
                t.status === 'active' ? { ...t, status: 'completed' as const } : t
              ), thought],
            }));

            // Auto-expand new thoughts
            setExpandedThoughts(prev => new Set([...prev, thought.id]));
          } else if (data.type === 'progress') {
            setStreamData(prev => ({
              ...prev,
              overallProgress: data.progress || prev.overallProgress,
              totalSteps: data.total_steps || prev.totalSteps,
              currentStep: data.current_step || prev.currentStep,
              estimatedTimeRemaining: data.eta_seconds,
            }));
          } else if (data.type === 'complete') {
            setStreamData(prev => ({
              ...prev,
              status: 'completed',
              overallProgress: 1,
              thoughts: prev.thoughts.map(t => ({ ...t, status: 'completed' as const })),
            }));
            eventSource.close();
            onComplete?.(data.results || {});
          } else if (data.type === 'error') {
            setStreamData(prev => ({ ...prev, status: 'error' }));
            eventSource.close();
            onError?.(data.error || 'Unknown error');
          }
        } catch (parseErr) {
          console.error('Failed to parse SSE message:', parseErr);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        // Don't set error if already completed
        setStreamData(prev => {
          if (prev.status === 'completed') return prev;
          return { ...prev, status: 'error' };
        });
      };

      return () => eventSource.close();
    } catch (err) {
      console.error('Failed to connect to stream:', err);
      setStreamData(prev => ({ ...prev, status: 'error' }));
      onError?.(err instanceof Error ? err.message : 'Connection failed');
    }
  }, [taskId, sessionId, onComplete, onError]);

  useEffect(() => {
    if (taskId && sessionId) {
      connectToStream();
    }
  }, [taskId, sessionId, connectToStream]);

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  if (compact && streamData.status === 'completed') {
    return null;
  }

  return (
    <div className={cn('rounded-xl border border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50 overflow-hidden', className)}>
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-purple-100/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <div className="relative">
            <Brain className={cn(
              'h-6 w-6 text-purple-600',
              streamData.status === 'running' && 'animate-pulse'
            )} />
            {streamData.status === 'running' && (
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-green-500 rounded-full animate-ping" />
            )}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              �� Gemini is analyzing
              {streamData.status === 'running' && (
                <Loader2 className="h-4 w-4 animate-spin text-purple-600" />
              )}
              {streamData.status === 'completed' && (
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              )}
            </h3>
            <p className="text-sm text-gray-600">
              {streamData.status === 'running' && `Step ${streamData.currentStep} of ${streamData.totalSteps || '?'}`}
              {streamData.status === 'completed' && 'Analysis complete'}
              {streamData.status === 'idle' && 'Waiting...'}
              {streamData.status === 'error' && 'Analysis error'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {streamData.estimatedTimeRemaining && streamData.status === 'running' && (
            <div className="flex items-center gap-1 text-sm text-gray-600">
              <Clock className="h-4 w-4" />
              <span>~{formatTime(streamData.estimatedTimeRemaining)}</span>
            </div>
          )}
          {expanded ? (
            <ChevronUp className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="px-4 pb-2">
        <Progress 
          value={streamData.overallProgress * 100} 
          className="h-2 bg-purple-100"
        />
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>{(streamData.overallProgress * 100).toFixed(0)}% complete</span>
          <span>{streamData.thoughts.filter(t => t.status === 'completed').length} steps completed</span>
        </div>
      </div>

      {/* Thought Bubbles */}
      {expanded && (
        <div className="p-4 pt-2 space-y-3 max-h-96 overflow-y-auto">
          {streamData.thoughts.length === 0 && streamData.status === 'running' && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <Loader2 className="h-5 w-5 animate-spin mr-2" />
              <span>Starting analysis...</span>
            </div>
          )}
          
          {streamData.thoughts.map((thought) => {
            const config = TYPE_CONFIG[thought.type];
            const Icon = config.icon;
            const isExpanded = expandedThoughts.has(thought.id);
            const thinkingConfig = thought.thinkingLevel ? THINKING_LEVEL_CONFIG[thought.thinkingLevel] : null;

            return (
              <div
                key={thought.id}
                className={cn(
                  'rounded-lg border transition-all duration-300',
                  thought.status === 'active' 
                    ? `${config.bgColor} border-l-4 ${config.color.replace('text-', 'border-')} shadow-sm animate-in fade-in slide-in-from-bottom-2`
                    : 'bg-white border-gray-200',
                  thought.status === 'completed' && 'opacity-80'
                )}
              >
                <div 
                  className="flex items-start gap-3 p-3 cursor-pointer"
                  onClick={() => toggleThought(thought.id)}
                >
                  <div className={cn(
                    'p-2 rounded-lg',
                    thought.status === 'active' ? config.bgColor : 'bg-gray-100'
                  )}>
                    {thought.status === 'active' ? (
                      <Loader2 className={cn('h-4 w-4 animate-spin', config.color)} />
                    ) : (
                      <Icon className={cn('h-4 w-4', thought.status === 'completed' ? 'text-green-600' : config.color)} />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={cn(
                        'font-medium text-sm',
                        thought.status === 'active' ? 'text-gray-900' : 'text-gray-700'
                      )}>
                        {thought.status === 'completed' && '✅ '}
                        Step {thought.step}: {thought.title}
                      </span>
                      {thinkingConfig && (
                        <Badge variant="secondary" className={cn('text-xs', thinkingConfig.color)}>
                          {thinkingConfig.label}
                        </Badge>
                      )}
                      {thought.model && (
                        <Badge variant="outline" className="text-xs">
                          {thought.model}
                        </Badge>
                      )}
                    </div>
                    
                    {thought.details.length > 0 && (
                      <div className={cn(
                        'mt-2 space-y-1 text-sm text-gray-600',
                        !isExpanded && 'line-clamp-2'
                      )}>
                        {(isExpanded ? thought.details : thought.details.slice(0, 2)).map((detail, idx) => (
                          <p key={idx} className="flex items-start gap-2">
                            <span className="text-gray-400">→</span>
                            <span>{detail}</span>
                          </p>
                        ))}
                        {!isExpanded && thought.details.length > 2 && (
                          <p className="text-purple-600 text-xs">
                            +{thought.details.length - 2} more details...
                          </p>
                        )}
                      </div>
                    )}

                    {/* Confidence & Grounding */}
                    {(thought.confidence || thought.groundingSources) && isExpanded && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {thought.confidence !== undefined && (
                          <div className="flex items-center gap-1 text-xs">
                            <span className="text-gray-500">Confidence:</span>
                            <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className={cn(
                                  'h-full rounded-full',
                                  thought.confidence > 0.8 ? 'bg-green-500' : 
                                  thought.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                                )}
                                style={{ width: `${thought.confidence * 100}%` }}
                              />
                            </div>
                            <span className="font-medium">{(thought.confidence * 100).toFixed(0)}%</span>
                          </div>
                        )}
                        {thought.groundingSources && thought.groundingSources.length > 0 && (
                          <Badge variant="outline" className="text-xs text-green-600 border-green-300">
                            ✓ {thought.groundingSources.length} verified sources
                          </Badge>
                        )}
                        {thought.tokensUsed && (
                          <span className="text-xs text-gray-400">
                            {thought.tokensUsed.toLocaleString()} tokens
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {thought.details.length > 2 && (
                    <button className="p-1 hover:bg-gray-100 rounded">
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default ThoughtBubbleStream;
