"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Brain, CheckCircle2, AlertCircle, TrendingUp, BarChart3 } from 'lucide-react';

// ==================== Types ====================

type ThoughtType = 
  | 'initialization'
  | 'data_quality'
  | 'calculation'
  | 'classification'
  | 'reasoning'
  | 'recommendation'
  | 'uncertainty'
  | 'completion'
  | 'error';

interface StreamingThought {
  type: ThoughtType;
  step: string;
  content: string;
  confidence?: number;
  data?: any;
  timestamp: string;
}

interface StreamingAnalysisProps {
  salesData: any[];
  menuData: any[];
  marketContext?: any;
  onComplete?: (analysis: any) => void;
}

// ==================== Thought Bubble Component ====================

const ThoughtBubble: React.FC<{ thought: StreamingThought; isLatest: boolean }> = ({ 
  thought, 
  isLatest 
}) => {
  const getIcon = () => {
    switch (thought.type) {
      case 'initialization':
        return <Brain className="w-5 h-5 text-blue-500" />;
      case 'data_quality':
        return <BarChart3 className="w-5 h-5 text-purple-500" />;
      case 'calculation':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'classification':
        return <BarChart3 className="w-5 h-5 text-orange-500" />;
      case 'reasoning':
        return <Brain className="w-5 h-5 text-indigo-500" />;
      case 'recommendation':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'uncertainty':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'completion':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Brain className="w-5 h-5 text-gray-500" />;
    }
  };

  const getBackgroundColor = () => {
    switch (thought.type) {
      case 'initialization':
        return 'bg-blue-50 border-blue-200';
      case 'data_quality':
        return 'bg-purple-50 border-purple-200';
      case 'calculation':
        return 'bg-green-50 border-green-200';
      case 'classification':
        return 'bg-orange-50 border-orange-200';
      case 'reasoning':
        return 'bg-indigo-50 border-indigo-200';
      case 'recommendation':
        return 'bg-green-50 border-green-200';
      case 'uncertainty':
        return 'bg-yellow-50 border-yellow-200';
      case 'completion':
        return 'bg-green-100 border-green-300';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div
      className={`
        thought-bubble
        ${isLatest ? 'animate-slide-in' : ''}
        ${thought.type === 'completion' ? 'scale-105' : ''}
      `}
    >
      <Card className={`p-4 border-2 ${getBackgroundColor()} transition-all duration-300`}>
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className="flex-shrink-0 mt-1">
            {getIcon()}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Step title */}
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-sm text-gray-700">
                {thought.step}
              </span>
              {thought.confidence !== undefined && thought.confidence !== null && (
                <Badge 
                  variant={thought.confidence > 0.8 ? "default" : "secondary"}
                  className="text-xs"
                >
                  {(thought.confidence * 100).toFixed(0)}% confidence
                </Badge>
              )}
            </div>

            {/* Main content */}
            <p className="text-sm text-gray-600 leading-relaxed">
              {thought.content}
            </p>

            {/* Additional data */}
            {thought.data && (
              <div className="mt-2 space-y-1">
                {/* Data quality details */}
                {thought.type === 'data_quality' && thought.data.issues && (
                  <div className="text-xs text-gray-500">
                    {thought.data.issues.length > 0 && (
                      <div>Issues: {thought.data.issues.join(', ')}</div>
                    )}
                  </div>
                )}

                {/* Classification details */}
                {thought.type === 'classification' && thought.data.reasoning && (
                  <div className="text-xs text-gray-500 italic">
                    {thought.data.reasoning}
                  </div>
                )}

                {/* Recommendation details */}
                {thought.type === 'recommendation' && thought.data.recommendations && (
                  <ul className="text-xs text-gray-600 space-y-1 mt-2">
                    {thought.data.recommendations.slice(0, 3).map((rec: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1">
                        <span className="text-green-500">→</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                )}

                {/* Uncertainty details */}
                {thought.type === 'uncertainty' && thought.data.assumptions && (
                  <div className="text-xs text-gray-500 mt-2">
                    <div className="font-medium">Key assumptions:</div>
                    <ul className="list-disc list-inside">
                      {thought.data.assumptions.map((assumption: string, idx: number) => (
                        <li key={idx}>{assumption}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Completion summary */}
                {thought.type === 'completion' && thought.data && (
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                    {thought.data.stars > 0 && (
                      <div className="flex items-center gap-1">
                        <span>⭐</span>
                        <span>{thought.data.stars} Stars</span>
                      </div>
                    )}
                    {thought.data.cash_cows > 0 && (
                      <div className="flex items-center gap-1">
                        <span>💰</span>
                        <span>{thought.data.cash_cows} Cash Cows</span>
                      </div>
                    )}
                    {thought.data.question_marks > 0 && (
                      <div className="flex items-center gap-1">
                        <span>❓</span>
                        <span>{thought.data.question_marks} Question Marks</span>
                      </div>
                    )}
                    {thought.data.dogs > 0 && (
                      <div className="flex items-center gap-1">
                        <span>🐕</span>
                        <span>{thought.data.dogs} Dogs</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Pulsing indicator for latest thought */}
          {isLatest && thought.type !== 'completion' && thought.type !== 'error' && (
            <div className="flex-shrink-0">
              <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

// ==================== Main Streaming Analysis Component ====================

export const StreamingAnalysis: React.FC<StreamingAnalysisProps> = ({
  salesData,
  menuData,
  marketContext,
  onComplete
}) => {
  const [thoughts, setThoughts] = useState<StreamingThought[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finalAnalysis, setFinalAnalysis] = useState<any>(null);
  
  const thoughtsEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Auto-scroll to latest thought
  useEffect(() => {
    thoughtsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [thoughts]);

  // Start streaming analysis
  useEffect(() => {
    if (!salesData || !menuData) return;

    const startStreaming = async () => {
      setIsStreaming(true);
      setError(null);
      setThoughts([]);

      try {
        // Send POST request to initiate streaming
        const response = await fetch('/api/v1/streaming/analysis/bcg', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            sales_data: salesData,
            menu_data: menuData,
            market_context: marketContext,
            enable_multi_perspective: true
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Set up EventSource for SSE
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No reader available');
        }

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                const thought = data as StreamingThought;
                
                setThoughts(prev => [...prev, thought]);

                // Check for completion
                if (thought.type === 'completion' && thought.data?.analysis) {
                  setFinalAnalysis(thought.data.analysis);
                  onComplete?.(thought.data.analysis);
                }

                // Check for error
                if (thought.type === 'error') {
                  setError(thought.content);
                }
              } catch (e) {
                console.error('Failed to parse thought:', e);
              }
            }
          }
        }
      } catch (err) {
        console.error('Streaming error:', err);
        setError(err instanceof Error ? err.message : 'Streaming failed');
      } finally {
        setIsStreaming(false);
      }
    };

    startStreaming();

    // Cleanup
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [salesData, menuData, marketContext, onComplete]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          🧠 AI Analysis in Progress
        </h2>
        {isStreaming && (
          <Badge variant="default" className="animate-pulse">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Thinking...
          </Badge>
        )}
      </div>

      {/* Thought Stream */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
        {thoughts.map((thought, index) => (
          <ThoughtBubble
            key={`${thought.timestamp}-${index}`}
            thought={thought}
            isLatest={index === thoughts.length - 1}
          />
        ))}
        <div ref={thoughtsEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <Card className="p-4 bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Completion Message */}
      {finalAnalysis && !isStreaming && (
        <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <div className="text-center">
            <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-3" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Analysis Complete!
            </h3>
            <p className="text-gray-600">
              Your strategic BCG analysis is ready. Scroll up to review the insights.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default StreamingAnalysis;
