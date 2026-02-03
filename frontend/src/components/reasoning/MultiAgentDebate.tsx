"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  AlertCircle, 
  CheckCircle2, 
  TrendingUp,
  Brain,
  Target,
  AlertTriangle,
  Lightbulb,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

// ==================== Types ====================

type ConsensusLevel = 'unanimous' | 'strong' | 'moderate' | 'weak' | 'split';

interface PerspectiveAnalysis {
  perspective_name: string;
  disagreements: string[];
  alternative_recommendations: {
    [key: string]: string[];
  };
  risks_identified: string[];
  opportunities_identified: string[];
  confidence_adjustments?: {
    [key: string]: number;
  };
}

interface StrategicRecommendation {
  category: string;
  recommendations: string[];
  consensus_level: ConsensusLevel;
  confidence: number;
  key_assumptions: string[];
  alternative_views: string[];
  risks: string[];
}

interface BCGAnalysis {
  products: any[];
  strategic_recommendations: {
    [key: string]: StrategicRecommendation;
  };
  overall_confidence: number;
  assumptions_made: string[];
  alternative_interpretations: string[];
  limitations: string[];
  reasoning_chain?: string[];
}

interface MultiAgentDebateProps {
  analysis: BCGAnalysis;
  perspectives?: PerspectiveAnalysis[];
  showDebate?: boolean;
}

// ==================== Helper Components ====================

const ConsensusIndicator: React.FC<{ level: ConsensusLevel }> = ({ level }) => {
  const getConfig = () => {
    switch (level) {
      case 'unanimous':
        return { color: 'bg-green-600', text: 'Unanimous', icon: CheckCircle2, width: 'w-full' };
      case 'strong':
        return { color: 'bg-blue-600', text: 'Strong Consensus', icon: CheckCircle2, width: 'w-4/5' };
      case 'moderate':
        return { color: 'bg-yellow-600', text: 'Moderate', icon: AlertCircle, width: 'w-3/5' };
      case 'weak':
        return { color: 'bg-orange-600', text: 'Weak', icon: AlertTriangle, width: 'w-2/5' };
      case 'split':
        return { color: 'bg-red-600', text: 'Split Opinion', icon: AlertTriangle, width: 'w-1/5' };
      default:
        return { color: 'bg-gray-600', text: 'Unknown', icon: AlertCircle, width: 'w-1/2' };
    }
  };

  const config = getConfig();
  const Icon = config.icon;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4" />
          <span className="text-sm font-medium">{config.text}</span>
        </div>
        <Badge variant={level === 'unanimous' || level === 'strong' ? 'default' : 'secondary'}>
          {level}
        </Badge>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full ${config.color} ${config.width} transition-all duration-500`} />
      </div>
    </div>
  );
};

const PerspectiveIcon: React.FC<{ perspective: string }> = ({ perspective }) => {
  const getIcon = () => {
    if (perspective.toLowerCase().includes('growth')) return '📈';
    if (perspective.toLowerCase().includes('cfo') || perspective.toLowerCase().includes('financial')) return '💰';
    if (perspective.toLowerCase().includes('customer') || perspective.toLowerCase().includes('cmo')) return '❤️';
    return '👤';
  };

  return <span className="text-2xl">{getIcon()}</span>;
};

// ==================== Main Components ====================

const PrimaryAnalysis: React.FC<{ data: BCGAnalysis }> = ({ data }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <Card className="p-6 bg-blue-50 border-blue-200">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-bold text-gray-900">Primary Analysis</h3>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default" className="bg-blue-600">
              {(data.overall_confidence * 100).toFixed(0)}% confidence
            </Badge>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        {expanded && (
          <div className="space-y-4">
            {/* Products Summary */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Products Analyzed</h4>
              <div className="grid grid-cols-4 gap-2 text-center">
                {Object.entries(
                  data.products.reduce((acc: any, p: any) => {
                    acc[p.category] = (acc[p.category] || 0) + 1;
                    return acc;
                  }, {})
                ).map(([category, count]) => (
                  <div key={category} className="bg-white rounded p-2">
                    <div className="text-2xl font-bold text-blue-600">{count as number}</div>
                    <div className="text-xs text-gray-600 capitalize">{category.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Assumptions */}
            {data.assumptions_made && data.assumptions_made.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Assumptions</h4>
                <ul className="space-y-1">
                  {data.assumptions_made.slice(0, 3).map((assumption, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>{assumption}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

const PerspectiveCard: React.FC<{ perspective: PerspectiveAnalysis; index: number }> = ({ 
  perspective, 
  index 
}) => {
  const [expanded, setExpanded] = useState(false);

  const colors = [
    'border-purple-200 bg-purple-50',
    'border-green-200 bg-green-50',
    'border-orange-200 bg-orange-50'
  ];

  return (
    <Card className={`p-6 ${colors[index % 3]}`}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <PerspectiveIcon perspective={perspective.perspective_name} />
            <h4 className="font-bold text-gray-900">{perspective.perspective_name}</h4>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </div>

        {/* Disagreements */}
        {perspective.disagreements && perspective.disagreements.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <h5 className="text-sm font-semibold text-gray-700">Disagreements</h5>
            </div>
            <ul className="space-y-1">
              {perspective.disagreements.slice(0, expanded ? undefined : 2).map((item, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-red-500">→</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {expanded && (
          <>
            {/* Alternative Recommendations */}
            {perspective.alternative_recommendations && 
             Object.keys(perspective.alternative_recommendations).length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-yellow-600" />
                  <h5 className="text-sm font-semibold text-gray-700">Alternative Recommendations</h5>
                </div>
                <div className="space-y-2">
                  {Object.entries(perspective.alternative_recommendations).map(([category, recs]) => (
                    <div key={category}>
                      <p className="text-xs font-medium text-gray-500 uppercase">{category}</p>
                      <ul className="space-y-1 mt-1">
                        {(recs as string[]).map((rec, idx) => (
                          <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-yellow-500">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Risks */}
            {perspective.risks_identified && perspective.risks_identified.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-orange-600" />
                  <h5 className="text-sm font-semibold text-gray-700">Risks Identified</h5>
                </div>
                <ul className="space-y-1">
                  {perspective.risks_identified.map((risk, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-orange-500">⚠</span>
                      <span>{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Opportunities */}
            {perspective.opportunities_identified && perspective.opportunities_identified.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <h5 className="text-sm font-semibold text-gray-700">Opportunities Identified</h5>
                </div>
                <ul className="space-y-1">
                  {perspective.opportunities_identified.map((opp, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-green-500">✓</span>
                      <span>{opp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
};

const FinalSynthesis: React.FC<{ data: BCGAnalysis }> = ({ data }) => {
  return (
    <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-green-600" />
          <h3 className="text-lg font-bold text-gray-900">Final Synthesis</h3>
        </div>

        {/* Strategic Recommendations by Category */}
        <div className="space-y-4">
          {Object.entries(data.strategic_recommendations).map(([category, rec]) => (
            <div key={category} className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-gray-900 capitalize">
                    {category.replace('_', ' ')}
                  </h4>
                  <Badge variant={rec.confidence > 0.8 ? 'default' : 'secondary'}>
                    {(rec.confidence * 100).toFixed(0)}% confidence
                  </Badge>
                </div>

                {/* Consensus Indicator */}
                <ConsensusIndicator level={rec.consensus_level} />

                {/* Recommendations */}
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase mb-2">Recommendations</p>
                  <ul className="space-y-1">
                    {rec.recommendations.map((recommendation, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-green-500">→</span>
                        <span>{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Alternative Views */}
                {rec.alternative_views && rec.alternative_views.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 uppercase mb-2">Alternative Views</p>
                    <ul className="space-y-1">
                      {rec.alternative_views.map((view, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                          <span className="text-blue-500">•</span>
                          <span>{view}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Risks */}
                {rec.risks && rec.risks.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 uppercase mb-2">Risks to Consider</p>
                    <ul className="space-y-1">
                      {rec.risks.map((risk, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                          <span className="text-orange-500">⚠</span>
                          <span>{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Overall Limitations */}
        {data.limitations && data.limitations.length > 0 && (
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Analysis Limitations</h4>
            <ul className="space-y-1">
              {data.limitations.map((limitation, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-yellow-600">!</span>
                  <span>{limitation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
};

// ==================== Main Component ====================

export const MultiAgentDebate: React.FC<MultiAgentDebateProps> = ({
  analysis,
  perspectives = [],
  showDebate = true
}) => {
  const [showPerspectives, setShowPerspectives] = useState(showDebate);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Multi-Agent Analysis</h2>
            <p className="text-sm text-gray-600">
              Multiple expert perspectives for reduced bias
            </p>
          </div>
        </div>
        {perspectives.length > 0 && (
          <Button
            variant="outline"
            onClick={() => setShowPerspectives(!showPerspectives)}
          >
            {showPerspectives ? 'Hide' : 'Show'} Expert Debate
          </Button>
        )}
      </div>

      {/* Primary Analysis */}
      <PrimaryAnalysis data={analysis} />

      {/* Alternative Perspectives */}
      {showPerspectives && perspectives.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-900">Alternative Viewpoints</h3>
            <Badge variant="secondary">{perspectives.length} experts</Badge>
          </div>
          
          <div className="grid gap-4">
            {perspectives.map((perspective, idx) => (
              <PerspectiveCard
                key={perspective.perspective_name}
                perspective={perspective}
                index={idx}
              />
            ))}
          </div>
        </div>
      )}

      {/* Final Synthesis */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Final Recommendations</h3>
        <FinalSynthesis data={analysis} />
      </div>

      {/* Transparency Note */}
      <Card className="p-4 bg-gray-50 border-gray-200">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-gray-700">
            <p className="font-medium mb-1">Transparent Multi-Perspective Analysis</p>
            <p className="text-gray-600">
              This analysis considers {perspectives.length > 0 ? perspectives.length + 1 : 1} different expert 
              perspective{perspectives.length > 0 ? 's' : ''} to reduce bias and provide balanced recommendations. 
              Consensus levels indicate agreement across perspectives, while alternative views highlight areas 
              of debate.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default MultiAgentDebate;
