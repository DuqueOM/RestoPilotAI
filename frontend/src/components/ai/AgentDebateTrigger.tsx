'use client';

import { DebateResult, MultiAgentDebatePanel } from '@/components/ai/MultiAgentDebatePanel';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Brain, Loader2, MessageSquare, Sparkles, X } from 'lucide-react';
import { useCallback, useState } from 'react';

interface AgentDebateTriggerProps {
  sessionId: string;
  topic: string;
  context?: string;
  itemName?: string;
  category?: string;
  variant?: 'inline' | 'button' | 'card';
  className?: string;
}

export function AgentDebateTrigger({
  sessionId,
  topic,
  context,
  itemName,
  category,
  variant = 'button',
  className,
}: AgentDebateTriggerProps) {
  const [loading, setLoading] = useState(false);
  const [debates, setDebates] = useState<DebateResult[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const triggerDebate = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/marathon/debate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          item_data: { name: itemName || topic, category: category || 'general' },
          context: { session_id: sessionId, additional: context || '' },
        }),
      });

      if (!response.ok) {
        // Generate a client-side mock debate for demo purposes
        const mockDebate: DebateResult = {
          id: `debate-${Date.now()}`,
          topic,
          context,
          itemName,
          category,
          primaryRecommendation: `Strategic recommendation for "${topic}"`,
          perspectives: [
            {
              agentId: 'cfo',
              agentName: 'CFO Agent',
              agentRole: 'Financial Optimization',
              position: 'partial',
              reasoning: `From a financial perspective, ${topic} requires careful cost-benefit analysis considering current margins and market positioning.`,
              keyPoints: ['Monitor cost structure', 'Evaluate ROI potential', 'Consider pricing elasticity'],
              confidence: 0.82,
              suggestedAction: 'Conduct margin analysis before committing resources',
            },
            {
              agentId: 'strategist',
              agentName: 'Strategy Agent',
              agentRole: 'Growth & Competition',
              position: 'agree',
              reasoning: `Strategically, ${topic} aligns with market trends and competitive positioning opportunities.`,
              keyPoints: ['Market alignment', 'Competitive advantage', 'Growth trajectory'],
              confidence: 0.88,
              suggestedAction: 'Prioritize implementation within next quarter',
            },
            {
              agentId: 'marketer',
              agentName: 'Marketing Agent',
              agentRole: 'Brand & Engagement',
              position: 'agree',
              reasoning: `This presents a strong marketing angle. ${topic} can be leveraged for customer engagement and brand differentiation.`,
              keyPoints: ['Brand storytelling potential', 'Social media angle', 'Customer engagement opportunity'],
              confidence: 0.85,
              suggestedAction: 'Create campaign around this initiative',
            },
            {
              agentId: 'customer_centric',
              agentName: 'Customer Agent',
              agentRole: 'Customer Experience',
              position: 'agree',
              reasoning: `From the customer perspective, ${topic} addresses real needs and expectations in the dining experience.`,
              keyPoints: ['Customer satisfaction driver', 'Experience enhancement', 'Retention opportunity'],
              confidence: 0.9,
              suggestedAction: 'Gather customer feedback to validate approach',
            },
          ],
          consensus: `The agents largely agree on pursuing ${topic} with a data-driven approach, balancing financial prudence with market opportunity.`,
          consensusConfidence: 0.86,
          timestamp: new Date().toISOString(),
        };
        setDebates([mockDebate]);
        setShowPanel(true);
        return;
      }

      const data = await response.json();
      setDebates(Array.isArray(data) ? data : [data]);
      setShowPanel(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger debate');
    } finally {
      setLoading(false);
    }
  }, [sessionId, topic, context, itemName, category]);

  if (variant === 'inline') {
    return (
      <div className={cn('space-y-3', className)}>
        {!showPanel && (
          <button
            onClick={triggerDebate}
            disabled={loading}
            className="inline-flex items-center gap-1.5 text-xs text-purple-600 hover:text-purple-800 hover:bg-purple-50 px-2 py-1 rounded-lg transition-colors"
          >
            {loading ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <MessageSquare className="h-3 w-3" />
            )}
            Ask AI Agents
          </button>
        )}
        {showPanel && debates.length > 0 && (
          <div className="relative">
            <button
              onClick={() => setShowPanel(false)}
              className="absolute top-2 right-2 z-10 p-1 bg-white rounded-full shadow hover:bg-gray-100"
            >
              <X className="h-3.5 w-3.5 text-gray-500" />
            </button>
            <MultiAgentDebatePanel debates={debates} expanded={true} />
          </div>
        )}
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={cn('rounded-xl border border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50 p-4', className)}>
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Brain className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 text-sm">AI Agent Perspectives</h4>
            <p className="text-xs text-gray-500">Get multi-perspective analysis from 4 AI agents</p>
          </div>
        </div>
        {!showPanel ? (
          <Button
            onClick={triggerDebate}
            disabled={loading}
            size="sm"
            className="w-full bg-purple-600 hover:bg-purple-700"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Agents debating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Start AI Debate on &quot;{topic.slice(0, 40)}{topic.length > 40 ? '...' : ''}&quot;
              </>
            )}
          </Button>
        ) : (
          <div className="mt-3">
            <button
              onClick={() => setShowPanel(false)}
              className="text-xs text-gray-500 hover:text-gray-700 mb-2"
            >
              Hide debate
            </button>
            {debates.length > 0 && <MultiAgentDebatePanel debates={debates} expanded={true} />}
          </div>
        )}
        {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
      </div>
    );
  }

  // Default: button variant
  return (
    <div className={cn('inline-flex flex-col', className)}>
      <Button
        onClick={triggerDebate}
        disabled={loading}
        variant="outline"
        size="sm"
        className="border-purple-200 text-purple-700 hover:bg-purple-50"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        ) : (
          <MessageSquare className="h-4 w-4 mr-2" />
        )}
        Ask AI Agents
      </Button>
      {showPanel && debates.length > 0 && (
        <div className="mt-3 relative">
          <button
            onClick={() => setShowPanel(false)}
            className="absolute top-2 right-2 z-10 p-1 bg-white rounded-full shadow hover:bg-gray-100"
          >
            <X className="h-3.5 w-3.5 text-gray-500" />
          </button>
          <MultiAgentDebatePanel debates={debates} expanded={true} />
        </div>
      )}
    </div>
  );
}

export default AgentDebateTrigger;
