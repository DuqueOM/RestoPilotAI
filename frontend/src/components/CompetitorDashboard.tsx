'use client';

import React, { useState } from 'react';

interface PriceGap {
  itemCategory: string;
  ourItem: string;
  ourPrice: number;
  competitorName: string;
  competitorItem: string;
  competitorPrice: number;
  priceDifference: number;
  priceDifferencePercent: number;
  recommendation: string;
  confidence: number;
}

interface CompetitorInsight {
  competitorName: string;
  priceComparison: 'higher' | 'lower' | 'similar';
  avgPriceDifference: number;
  uniqueItems: string[];
  recommendations: string[];
  confidenceScore: number;
  itemCount: number;
  priceRange: { min: number; max: number };
}

interface CompetitorAnalysis {
  analysisId: string;
  competitorsAnalyzed: string[];
  marketPosition: string;
  competitiveIntensity: string;
  keyDifferentiators: string[];
  competitiveGaps: string[];
  pricePositioning: string;
  priceGaps: PriceGap[];
  pricingOpportunities: string[];
  ourUniqueItems: string[];
  competitorUniqueItems: Record<string, string[]>;
  categoryGaps: Array<{ category: string; competitorsOffering: number; ourCount: number; opportunity: string }>;
  strategicRecommendations: Array<{ priority: number; action: string; expectedImpact: string; timeframe: string }>;
  competitiveThreats: Array<{ threat: string; severity: string; recommendedResponse: string }>;
  confidence: number;
}

interface CompetitorDashboardProps {
  analysis?: CompetitorAnalysis;
  insights?: CompetitorInsight[];
  isLoading?: boolean;
}

export default function CompetitorDashboard({ 
  analysis, 
  insights = [], 
  isLoading = false 
}: CompetitorDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'pricing' | 'products' | 'strategy'>('overview');

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!analysis && insights.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No competitor data</h3>
        <p className="mt-1 text-sm text-gray-500">Add competitors to see competitive insights.</p>
      </div>
    );
  }

  const getPriceComparisonColor = (comparison: string) => {
    switch (comparison) {
      case 'higher': return 'bg-red-100 text-red-800';
      case 'lower': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🎯 Competitor Intelligence</h2>
          <p className="mt-1 text-sm text-gray-500">
            Analyzing {analysis?.competitorsAnalyzed?.length || insights.length} competitors
          </p>
        </div>
        {analysis && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Confidence:</span>
            <span className={`px-2 py-1 rounded-full text-sm font-medium ${
              analysis.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
              analysis.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {Math.round(analysis.confidence * 100)}%
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'pricing', label: '💰 Pricing' },
            { id: 'products', label: '🍽️ Products' },
            { id: 'strategy', label: '🎯 Strategy' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && analysis && (
        <div className="space-y-6">
          {/* Market Position Card */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-indigo-500">
              <h3 className="text-sm font-medium text-gray-500">Market Position</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900 capitalize">{analysis.marketPosition}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
              <h3 className="text-sm font-medium text-gray-500">Competitive Intensity</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900 capitalize">{analysis.competitiveIntensity}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
              <h3 className="text-sm font-medium text-gray-500">Price Positioning</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900 capitalize">{analysis.pricePositioning}</p>
            </div>
          </div>

          {/* Key Differentiators */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">✨ Our Key Differentiators</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.keyDifferentiators?.map((diff, idx) => (
                <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                  {diff}
                </span>
              ))}
            </div>
          </div>

          {/* Competitive Gaps */}
          {analysis.competitiveGaps?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">⚠️ Areas to Improve</h3>
              <ul className="space-y-2">
                {analysis.competitiveGaps.map((gap, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="flex-shrink-0 h-5 w-5 text-yellow-500">•</span>
                    <span className="ml-2 text-gray-700">{gap}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Competitor Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {insights.map((insight, idx) => (
              <div key={idx} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900">{insight.competitorName}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriceComparisonColor(insight.priceComparison)}`}>
                    {insight.priceComparison === 'higher' ? '↑ More Expensive' :
                     insight.priceComparison === 'lower' ? '↓ Cheaper' : '≈ Similar'}
                  </span>
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Items:</span>
                    <span className="font-medium">{insight.itemCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Price Range:</span>
                    <span className="font-medium">${insight.priceRange.min} - ${insight.priceRange.max}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Avg Difference:</span>
                    <span className={`font-medium ${insight.avgPriceDifference > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {insight.avgPriceDifference > 0 ? '+' : ''}{insight.avgPriceDifference.toFixed(1)}%
                    </span>
                  </div>
                </div>

                {insight.uniqueItems.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 mb-2">They offer (we don&apos;t):</p>
                    <div className="flex flex-wrap gap-1">
                      {insight.uniqueItems.slice(0, 3).map((item, i) => (
                        <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                          {item}
                        </span>
                      ))}
                      {insight.uniqueItems.length > 3 && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs">
                          +{insight.uniqueItems.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pricing Tab */}
      {activeTab === 'pricing' && analysis && (
        <div className="space-y-6">
          {/* Price Gaps Table */}
          {analysis.priceGaps?.length > 0 && (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">💰 Price Gap Analysis</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Our Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Competitor</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Difference</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommendation</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analysis.priceGaps.map((gap, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{gap.itemCategory}</div>
                          <div className="text-xs text-gray-500">{gap.ourItem}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${gap.ourPrice.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">${gap.competitorPrice.toFixed(2)}</div>
                          <div className="text-xs text-gray-500">{gap.competitorName}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded text-sm font-medium ${
                            gap.priceDifferencePercent > 10 ? 'bg-red-100 text-red-800' :
                            gap.priceDifferencePercent < -10 ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {gap.priceDifferencePercent > 0 ? '+' : ''}{gap.priceDifferencePercent.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-700 max-w-xs truncate">
                          {gap.recommendation}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Pricing Opportunities */}
          {analysis.pricingOpportunities?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">💡 Pricing Opportunities</h3>
              <ul className="space-y-3">
                {analysis.pricingOpportunities.map((opp, idx) => (
                  <li key={idx} className="flex items-start p-3 bg-green-50 rounded-lg">
                    <span className="flex-shrink-0 text-green-500 mr-3">💵</span>
                    <span className="text-gray-700">{opp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && analysis && (
        <div className="space-y-6">
          {/* Our Unique Items */}
          {analysis.ourUniqueItems?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🌟 Our Unique Offerings</h3>
              <div className="flex flex-wrap gap-2">
                {analysis.ourUniqueItems.map((item, idx) => (
                  <span key={idx} className="px-3 py-2 bg-indigo-100 text-indigo-800 rounded-lg text-sm font-medium">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Category Gaps */}
          {analysis.categoryGaps?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Category Gap Analysis</h3>
              <div className="space-y-4">
                {analysis.categoryGaps.map((gap, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{gap.category}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        gap.ourCount === 0 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {gap.ourCount === 0 ? 'Missing' : `${gap.ourCount} items`}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">
                      {gap.competitorsOffering} competitor(s) offer this category
                    </p>
                    <p className="text-sm text-indigo-600 mt-2">
                      💡 {gap.opportunity}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Competitor Unique Items */}
          {Object.keys(analysis.competitorUniqueItems || {}).length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Competitor Exclusives</h3>
              <div className="space-y-4">
                {Object.entries(analysis.competitorUniqueItems).map(([competitor, items]) => (
                  <div key={competitor} className="border-l-4 border-orange-400 pl-4">
                    <h4 className="font-medium text-gray-900">{competitor}</h4>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {items.slice(0, 5).map((item, idx) => (
                        <span key={idx} className="px-2 py-1 bg-orange-50 text-orange-700 rounded text-xs">
                          {item}
                        </span>
                      ))}
                      {items.length > 5 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">
                          +{items.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Strategy Tab */}
      {activeTab === 'strategy' && analysis && (
        <div className="space-y-6">
          {/* Strategic Recommendations */}
          {analysis.strategicRecommendations?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🎯 Strategic Recommendations</h3>
              <div className="space-y-4">
                {analysis.strategicRecommendations.map((rec, idx) => (
                  <div key={idx} className={`border-l-4 pl-4 py-3 ${
                    rec.priority === 1 ? 'border-red-500 bg-red-50' :
                    rec.priority === 2 ? 'border-yellow-500 bg-yellow-50' :
                    'border-blue-500 bg-blue-50'
                  }`}>
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{rec.action}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        rec.priority === 1 ? 'bg-red-200 text-red-800' :
                        rec.priority === 2 ? 'bg-yellow-200 text-yellow-800' :
                        'bg-blue-200 text-blue-800'
                      }`}>
                        Priority {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">Expected Impact:</span> {rec.expectedImpact}
                    </p>
                    <p className="text-sm text-gray-500">
                      <span className="font-medium">Timeframe:</span> {rec.timeframe}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Competitive Threats */}
          {analysis.competitiveThreats?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">⚠️ Competitive Threats</h3>
              <div className="space-y-3">
                {analysis.competitiveThreats.map((threat, idx) => (
                  <div key={idx} className={`p-4 rounded-lg border ${getSeverityColor(threat.severity)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{threat.threat}</span>
                      <span className="text-xs font-medium uppercase">{threat.severity}</span>
                    </div>
                    <p className="text-sm">
                      <span className="font-medium">Response:</span> {threat.recommendedResponse}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
