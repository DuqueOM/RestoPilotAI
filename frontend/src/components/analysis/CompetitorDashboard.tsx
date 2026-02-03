'use client';

import { GroundingSources } from '@/components/common/GroundingSources';
import { useState } from 'react';

interface PriceGap {
  item_category: string;
  our_item: string;
  our_price: number;
  competitor_name: string;
  competitor_item: string;
  competitor_price: number;
  price_difference: number;
  price_difference_percent: number;
  recommendation: string;
  confidence: number;
}

interface CompetitorInsight {
  competitorName?: string;
  name?: string;
  priceComparison?: 'higher' | 'lower' | 'similar';
  avgPriceDifference?: number;
  uniqueItems?: string[];
  recommendations?: string[];
  confidenceScore?: number;
  itemCount?: number;
  priceRange?: { min: number; max: number };
  // Enriched fields
  rating?: number;
  address?: string;
  distance?: string;
  cuisine_type?: string;
  social_media?: Array<{ platform: string; url: string; handle?: string }>;
  menu?: { item_count: number; sources: string[] };
  competitive_intelligence?: {
    cuisine_types?: string[];
    specialties?: string[];
    brand_positioning?: string;
    target_audience?: string;
  };
  photo_analysis?: {
    ambiance?: string;
    visual_quality_score?: number;
    presentation_style?: string;
    price_perception?: string;
  };
  metadata?: {
    confidence_score: number;
    data_sources: string[];
  };
}

interface CompetitorAnalysis {
  analysis_id: string;
  competitors_analyzed: string[];
  competitive_landscape: {
    market_position: string;
    competitive_intensity: string;
    key_differentiators: string[];
    competitive_gaps: string[];
  };
  price_analysis: {
    price_positioning: string;
    price_gaps: PriceGap[];
    pricing_opportunities: string[];
  };
  product_analysis: {
    our_unique_items: string[];
    competitor_unique_items: Record<string, string[]>;
    category_gaps: Array<{ category: string; competitors_offering: number; our_count: number; opportunity: string }>;
    trending_items_missing: string[];
  };
  strategic_recommendations: Array<{ priority: number; action: string; expected_impact: string; timeframe: string }>;
  competitive_threats: Array<{ threat: string; severity: string; recommended_response: string }>;
  metadata: {
    confidence: number;
  };
  grounding_sources?: Array<{ web?: { uri: string; title?: string }; uri?: string; title?: string }>;
  grounded?: boolean;
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

  // Check if we have basic competitor data from location search
  const hasBasicCompetitors = insights.some((i: any) => i.competitorName || i.name);

  if (!analysis && insights.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No competitor data</h3>
        <p className="mt-1 text-sm text-gray-500">Search for your restaurant location to discover nearby competitors.</p>
      </div>
    );
  }

  // Show basic competitor info from location search if no full analysis
  if (!analysis && hasBasicCompetitors) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">🎯 Nearby Competitors</h2>
            <p className="mt-1 text-sm text-gray-500">
              {insights.length} restaurants found near your location
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {insights.map((competitor, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow p-5 border border-gray-100 hover:shadow-md transition-shadow relative overflow-hidden">
              {/* Confidence Badge */}
              {competitor.metadata?.confidence_score && (
                 <div className="absolute top-0 right-0 px-2 py-1 bg-emerald-50 text-emerald-700 text-[10px] font-bold rounded-bl-lg border-l border-b border-emerald-100">
                   {Math.round(competitor.metadata.confidence_score * 100)}% Match
                 </div>
              )}

              <div className="flex items-start justify-between mb-3 pr-8">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">{competitor.competitorName || competitor.name}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    {(competitor.rating && competitor.rating > 0) && (
                      <div className="flex items-center gap-1 px-1.5 py-0.5 bg-yellow-50 rounded text-xs border border-yellow-100">
                        <span className="text-yellow-500">★</span>
                        <span className="font-medium">{competitor.rating}</span>
                      </div>
                    )}
                    {competitor.competitive_intelligence?.cuisine_types?.map((type, i) => (
                      <span key={i} className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {competitor.address && (
                <p className="text-sm text-gray-500 mb-2 flex items-start gap-1">
                  <span className="flex-shrink-0">📍</span> 
                  <span className="line-clamp-1">{competitor.address}</span>
                </p>
              )}
              
              {/* Enriched Data Grid */}
              <div className="grid grid-cols-2 gap-3 mt-4 mb-4">
                <div className="p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Menu Analysis</p>
                  <p className="font-semibold text-gray-900 flex items-center gap-1">
                    🍽️ {competitor.menu?.item_count || competitor.itemCount || 0} items
                  </p>
                  {competitor.menu?.sources && (
                    <p className="text-[10px] text-gray-400 mt-1 truncate">
                      Src: {competitor.menu.sources.join(', ')}
                    </p>
                  )}
                </div>
                <div className="p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Social Media</p>
                  <div className="flex gap-2 mt-1">
                    {competitor.social_media && competitor.social_media.length > 0 ? (
                      competitor.social_media.map((sm, i) => (
                        <a 
                          key={i} 
                          href={sm.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-emerald-600 transition-colors"
                          title={`${sm.platform}: ${sm.handle || 'Link'}`}
                        >
                          {sm.platform === 'facebook' && '📘'}
                          {sm.platform === 'instagram' && '📸'}
                          {sm.platform === 'tiktok' && '🎵'}
                          {sm.platform === 'whatsapp_business' && '💬'}
                          {sm.platform === 'twitter' && '🐦'}
                        </a>
                      ))
                    ) : (
                      <span className="text-xs text-gray-400 italic">None found</span>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Positioning / Intelligence */}
              {competitor.competitive_intelligence?.brand_positioning && (
                <div className="mb-3">
                  <p className="text-xs text-gray-500 mb-0.5">Brand Positioning</p>
                  <p className="text-sm text-gray-700 italic">
                    "{competitor.competitive_intelligence.brand_positioning}"
                  </p>
                </div>
              )}

              {/* Visual Intelligence */}
              {competitor.photo_analysis && (
                <div className="mb-3 p-2 bg-purple-50 rounded-lg border border-purple-100">
                  <p className="text-xs text-purple-700 font-semibold mb-1 flex justify-between">
                    <span>Visual Intelligence</span>
                    {competitor.photo_analysis.visual_quality_score && (
                      <span>{Math.round(competitor.photo_analysis.visual_quality_score * 10)}/10 Score</span>
                    )}
                  </p>
                  <div className="space-y-1">
                    {competitor.photo_analysis.ambiance && (
                      <p className="text-xs text-gray-600">
                        <span className="font-medium">Ambiance:</span> {competitor.photo_analysis.ambiance}
                      </p>
                    )}
                    {competitor.photo_analysis.presentation_style && (
                      <p className="text-xs text-gray-600">
                        <span className="font-medium">Style:</span> {competitor.photo_analysis.presentation_style}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {competitor.distance && (
                <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                  🚶 {competitor.distance} away
                </p>
              )}

              {(competitor as any).cuisine_type && !competitor.competitive_intelligence && (
                <span className="inline-block mt-2 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                  {(competitor as any).cuisine_type}
                </span>
              )}
            </div>
          ))}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-700">
            <strong>💡 Tip:</strong> For detailed competitive analysis including pricing comparisons, 
            product gaps, and strategic recommendations, provide competitor menu data or connect social media links.
          </p>
        </div>
      </div>
    );
  }

  const getPriceComparisonColor = (comparison?: string) => {
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
            Analyzing {analysis?.competitors_analyzed?.length || insights.length} competitors
          </p>
        </div>
        {analysis && analysis.metadata && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Confidence:</span>
            <span className={`px-2 py-1 rounded-full text-sm font-medium ${
              analysis.metadata.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
              analysis.metadata.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {Math.round(analysis.metadata.confidence * 100)}%
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
          {/* Grounding Sources */}
          {analysis.grounding_sources && analysis.grounding_sources.length > 0 && (
            <GroundingSources 
              sources={analysis.grounding_sources}
              isGrounded={analysis.grounded || false}
            />
          )}

          {/* Key Differentiators */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">✨ Our Key Differentiators</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.competitive_landscape.key_differentiators?.map((diff, idx) => (
                <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                  {diff}
                </span>
              ))}
            </div>
          </div>

          {/* Competitive Gaps */}
          {analysis.competitive_landscape.competitive_gaps?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">⚠️ Areas to Improve</h3>
              <ul className="space-y-2">
                {analysis.competitive_landscape.competitive_gaps.map((gap, idx) => (
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
                  <h4 className="text-lg font-semibold text-gray-900">{insight.competitorName || insight.name}</h4>
                  {insight.priceComparison && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriceComparisonColor(insight.priceComparison)}`}>
                      {insight.priceComparison === 'higher' ? '↑ More Expensive' :
                       insight.priceComparison === 'lower' ? '↓ Cheaper' : '≈ Similar'}
                    </span>
                  )}
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Items:</span>
                    <span className="font-medium">{insight.itemCount || insight.menu?.item_count || 0}</span>
                  </div>
                  {(insight.priceRange || insight.menu?.sources) && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Price Range:</span>
                      <span className="font-medium">
                        {insight.priceRange 
                          ? `$${insight.priceRange.min} - $${insight.priceRange.max}`
                          : 'N/A'
                        }
                      </span>
                    </div>
                  )}
                  {insight.avgPriceDifference !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Avg Difference:</span>
                      <span className={`font-medium ${insight.avgPriceDifference > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {insight.avgPriceDifference > 0 ? '+' : ''}{insight.avgPriceDifference.toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>

                {insight.uniqueItems && insight.uniqueItems.length > 0 && (
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
          {analysis.price_analysis.price_gaps?.length > 0 && (
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
                    {analysis.price_analysis.price_gaps.map((gap, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{gap.item_category}</div>
                          <div className="text-xs text-gray-500">{gap.our_item}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${gap.our_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">${gap.competitor_price.toFixed(2)}</div>
                          <div className="text-xs text-gray-500">{gap.competitor_name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded text-sm font-medium ${
                            gap.price_difference_percent > 10 ? 'bg-red-100 text-red-800' :
                            gap.price_difference_percent < -10 ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {gap.price_difference_percent > 0 ? '+' : ''}{gap.price_difference_percent.toFixed(1)}%
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
          {analysis.price_analysis.pricing_opportunities?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">💡 Pricing Opportunities</h3>
              <ul className="space-y-3">
                {analysis.price_analysis.pricing_opportunities.map((opp, idx) => (
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
          {analysis.product_analysis.our_unique_items?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🌟 Our Unique Offerings</h3>
              <div className="flex flex-wrap gap-2">
                {analysis.product_analysis.our_unique_items.map((item, idx) => (
                  <span key={idx} className="px-3 py-2 bg-indigo-100 text-indigo-800 rounded-lg text-sm font-medium">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Category Gaps */}
          {analysis.product_analysis.category_gaps?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Category Gap Analysis</h3>
              <div className="space-y-4">
                {analysis.product_analysis.category_gaps.map((gap, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{gap.category}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        gap.our_count === 0 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {gap.our_count === 0 ? 'Missing' : `${gap.our_count} items`}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">
                      {gap.competitors_offering} competitor(s) offer this category
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
          {Object.keys(analysis.product_analysis.competitor_unique_items || {}).length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Competitor Exclusives</h3>
              <div className="space-y-4">
                {Object.entries(analysis.product_analysis.competitor_unique_items).map(([competitor, items]) => (
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
          {analysis.strategic_recommendations?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🎯 Strategic Recommendations</h3>
              <div className="space-y-4">
                {analysis.strategic_recommendations.map((rec, idx) => (
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
                      <span className="font-medium">Expected Impact:</span> {rec.expected_impact}
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
          {analysis.competitive_threats?.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">⚠️ Competitive Threats</h3>
              <div className="space-y-3">
                {analysis.competitive_threats.map((threat, idx) => (
                  <div key={idx} className={`p-4 rounded-lg border ${getSeverityColor(threat.severity)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{threat.threat}</span>
                      <span className="text-xs font-medium uppercase">{threat.severity}</span>
                    </div>
                    <p className="text-sm">
                      <span className="font-medium">Response:</span> {threat.recommended_response}
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
