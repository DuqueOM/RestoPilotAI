'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
    Briefcase,
    ChevronDown,
    ChevronUp,
    Heart,
    Lightbulb,
    MessageSquare,
    TrendingUp,
    Users,
} from 'lucide-react';
import { useState } from 'react';

export type AgentId = 'cfo' | 'strategist' | 'marketer' | 'customer_centric';
export type Position = 'agree' | 'disagree' | 'partial' | 'neutral';

export interface AgentPerspective {
  agentId: AgentId;
  agentName: string;
  agentRole: string;
  position: Position;
  reasoning: string;
  keyPoints: string[];
  confidence: number;
  suggestedAction?: string;
}

export interface DebateResult {
  id: string;
  topic: string;
  context?: string;
  itemName?: string;
  category?: string;
  primaryRecommendation: string;
  perspectives: AgentPerspective[];
  consensus: string;
  consensusConfidence: number;
  dissent?: string;
  timestamp: string;
}

interface MultiAgentDebatePanelProps {
  debates: DebateResult[];
  expanded?: boolean;
  showAllDebates?: boolean;
  maxDebatesShown?: number;
  className?: string;
}

const AGENT_CONFIG: Record<AgentId, { 
  icon: typeof Briefcase; 
  color: string; 
  bgColor: string; 
  borderColor: string;
  emoji: string;
}> = {
  cfo: { 
    icon: Briefcase, 
    color: 'text-blue-700', 
    bgColor: 'bg-blue-50', 
    borderColor: 'border-blue-200',
    emoji: '👔'
  },
  strategist: { 
    icon: TrendingUp, 
    color: 'text-emerald-700', 
    bgColor: 'bg-emerald-50', 
    borderColor: 'border-emerald-200',
    emoji: '📈'
  },
  marketer: { 
    icon: Lightbulb, 
    color: 'text-amber-700', 
    bgColor: 'bg-amber-50', 
    borderColor: 'border-amber-200',
    emoji: '💡'
  },
  customer_centric: { 
    icon: Heart, 
    color: 'text-rose-700', 
    bgColor: 'bg-rose-50', 
    borderColor: 'border-rose-200',
    emoji: '❤️'
  },
};

const POSITION_CONFIG: Record<Position, { label: string; color: string; bgColor: string }> = {
  agree: { label: 'Agree', color: 'text-green-700', bgColor: 'bg-green-100' },
  disagree: { label: 'Disagree', color: 'text-red-700', bgColor: 'bg-red-100' },
  partial: { label: 'Partially', color: 'text-amber-700', bgColor: 'bg-amber-100' },
  neutral: { label: 'Neutral', color: 'text-gray-700', bgColor: 'bg-gray-100' },
};

function AgentCard({ perspective }: { perspective: AgentPerspective }) {
  const [expanded, setExpanded] = useState(false);
  const config = AGENT_CONFIG[perspective.agentId];
  const positionConfig = POSITION_CONFIG[perspective.position];
  const Icon = config.icon;

  return (
    <div className={cn(
      'rounded-lg border-2 p-4 transition-all duration-200 hover:shadow-md',
      config.borderColor,
      config.bgColor
    )}>
      {/* Agent Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={cn('p-2 rounded-full', config.bgColor)}>
            <span className="text-xl">{config.emoji}</span>
          </div>
          <div>
            <h4 className={cn('font-semibold text-sm', config.color)}>
              {perspective.agentName}
            </h4>
            <p className="text-xs text-gray-500">{perspective.agentRole}</p>
          </div>
        </div>
        <Badge className={cn('text-xs', positionConfig.bgColor, positionConfig.color)}>
          {positionConfig.label}
        </Badge>
      </div>

      {/* Main Reasoning */}
      <div className="mb-3">
        <p className={cn(
          'text-sm font-medium',
          config.color
        )}>
          "{perspective.reasoning}"
        </p>
      </div>

      {/* Confidence Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-600">Confidence</span>
          <span className={cn('font-medium', config.color)}>
            {(perspective.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <Progress 
          value={perspective.confidence * 100} 
          className="h-2"
        />
      </div>

      {/* Expandable Key Points */}
      {perspective.keyPoints && perspective.keyPoints.length > 0 && (
        <div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900"
          >
            {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            {expanded ? 'Hide details' : `View ${perspective.keyPoints.length} key points`}
          </button>
          
          {expanded && (
            <ul className="mt-2 space-y-1 text-xs text-gray-600 pl-4">
              {perspective.keyPoints.map((point, idx) => (
                <li key={idx} className="flex items-start gap-1">
                  <span className="text-gray-400">•</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Suggested Action */}
      {perspective.suggestedAction && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs">
            <span className="font-medium text-gray-700">Suggested Action: </span>
            <span className="text-gray-600">{perspective.suggestedAction}</span>
          </p>
        </div>
      )}
    </div>
  );
}

function DebateCard({ debate, initialExpanded = false }: { debate: DebateResult; initialExpanded?: boolean }) {
  const [expanded, setExpanded] = useState(initialExpanded);

  return (
    <Card className="border-indigo-100 bg-gradient-to-br from-white to-indigo-50/30 overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <MessageSquare className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                🤔 AI Debate: {debate.topic}
              </CardTitle>
              {debate.itemName && (
                <p className="text-sm text-gray-500 mt-1">
                  Product: <span className="font-medium">{debate.itemName}</span>
                  {debate.category && (
                    <Badge variant="outline" className="ml-2 text-xs">
                      {debate.category}
                    </Badge>
                  )}
                </p>
              )}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Quick Summary - Always Visible */}
        <div className="flex items-center gap-3 mb-4 p-3 bg-white rounded-lg border border-gray-100">
          <Users className="h-5 w-5 text-indigo-500" />
          <div className="flex-1">
            <p className="text-sm text-gray-600">
              <span className="font-medium">{debate.perspectives.length} agents</span> debated this topic
            </p>
          </div>
          <div className="flex -space-x-2">
            {debate.perspectives.map((p) => (
              <div
                key={p.agentId}
                className={cn(
                  'w-8 h-8 rounded-full flex items-center justify-center border-2 border-white',
                  AGENT_CONFIG[p.agentId].bgColor
                )}
                title={p.agentName}
              >
                <span className="text-sm">{AGENT_CONFIG[p.agentId].emoji}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Agent Perspectives Grid - Expandable */}
        {expanded && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 animate-in fade-in slide-in-from-top-2 duration-300">
            {debate.perspectives.map((perspective) => (
              <AgentCard key={perspective.agentId} perspective={perspective} />
            ))}
          </div>
        )}

        {/* Consensus Box - Always Visible */}
        <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-green-100 rounded-full">
              <span className="text-lg">✅</span>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-green-800 mb-1">CONSENSUS</h4>
              <p className="text-sm text-green-700">{debate.consensus}</p>
              
              <div className="flex items-center gap-4 mt-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-600">Confidence:</span>
                  <div className="w-20 h-2 bg-green-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${debate.consensusConfidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-green-700">
                    {(debate.consensusConfidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Dissent Note */}
              {debate.dissent && (
                <div className="mt-3 pt-3 border-t border-green-200">
                  <p className="text-xs text-amber-700">
                    <span className="font-medium">⚠️ Dissenting Note:</span> {debate.dissent}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Primary Recommendation */}
        {debate.primaryRecommendation && (
          <div className="mt-4 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
            <p className="text-sm">
              <span className="font-semibold text-indigo-700">🎯 Primary Recommendation: </span>
              <span className="text-gray-700">{debate.primaryRecommendation}</span>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function MultiAgentDebatePanel({
  debates,
  expanded = true,
  showAllDebates = false,
  maxDebatesShown = 3,
  className,
}: MultiAgentDebatePanelProps) {
  const [showAll, setShowAll] = useState(showAllDebates);

  if (!debates || debates.length === 0) {
    return null;
  }

  const debatesToShow = showAll ? debates : debates.slice(0, maxDebatesShown);
  const hasMore = debates.length > maxDebatesShown;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <MessageSquare className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI Agent Debates</h3>
            <p className="text-sm text-gray-500">
              Multiple perspectives analyzed by Gemini 3
            </p>
          </div>
        </div>
        <Badge variant="secondary" className="bg-indigo-100 text-indigo-700">
          {debates.length} debate{debates.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      {/* Debates List */}
      <div className="space-y-4">
        {debatesToShow.map((debate, idx) => (
          <DebateCard 
            key={debate.id} 
            debate={debate} 
            initialExpanded={idx === 0 && expanded}
          />
        ))}
      </div>

      {/* Show More Button */}
      {hasMore && !showAll && (
        <Button
          variant="outline"
          className="w-full"
          onClick={() => setShowAll(true)}
        >
          View {debates.length - maxDebatesShown} more debates
          <ChevronDown className="h-4 w-4 ml-2" />
        </Button>
      )}
    </div>
  );
}

export default MultiAgentDebatePanel;
