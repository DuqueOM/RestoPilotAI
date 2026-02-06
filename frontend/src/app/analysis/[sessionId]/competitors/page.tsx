'use client';

import { AgentDebateTrigger } from '@/components/ai/AgentDebateTrigger';
import { MapPin, Star, Target, TrendingDown, TrendingUp } from 'lucide-react';
import { useParams } from 'next/navigation';
import { useSessionData } from '../layout';


export default function CompetitorsPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { sessionData, isLoading } = useSessionData();

  const unwrappedSession = (sessionData as any)?.data || sessionData;

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-gray-200 rounded w-48"></div>
        <div className="grid md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-48 bg-gray-100 rounded-xl"></div>)}
        </div>
      </div>
    );
  }

  // Get competitors from session data - check multiple sources
  const competitors = unwrappedSession?.competitor_analysis?.competitors 
    || sessionData?.competitor_analysis?.competitors 
    || unwrappedSession?.enriched_competitors 
    || unwrappedSession?.competitors 
    || sessionData?.enriched_competitors
    || sessionData?.competitors
    || [];
  const competitorContext = unwrappedSession?.competitor_context || unwrappedSession?.business_context?.competitors_input || sessionData?.competitor_context || "";

  if (!competitors.length && !isLoading) {
    return (
      <div className="text-center py-12 text-gray-500">
        <img src="/images/empty-state-plate.png" alt="" className="w-32 h-24 mx-auto mb-4 object-cover rounded-lg opacity-60" />
        <p className="text-lg">No competitor analysis available</p>
        <p className="text-sm mt-2">Run the analysis to identify competitors.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header with Accent Image */}
      <div className="relative rounded-xl overflow-hidden bg-gradient-to-r from-teal-50 to-cyan-50 border border-teal-200/60">
        <div className="flex items-center gap-6 p-5">
          <div className="hidden sm:block flex-shrink-0 w-28 h-20 rounded-lg overflow-hidden shadow-md">
            <img src="/images/competitors-market.png" alt="" className="w-full h-full object-cover" loading="lazy" />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-teal-600" />
              Competitor Analysis
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">Market intelligence on {competitors.length} nearby competitors with Google Search grounding</p>
          </div>
        </div>
      </div>

      {/* Context from audio/text if available */}
      {competitorContext && (
        <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
          <h3 className="font-medium text-orange-800 mb-2">📝 Context Provided</h3>
          <p className="text-sm text-gray-700">{competitorContext}</p>
        </div>
      )}

      {/* Competitor Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {competitors.map((competitor: any, idx: number) => {
          const name = competitor.name || competitor.business_name || 'Unknown';
          const rating = competitor.rating || competitor.google_rating;
          const address = competitor.address || competitor.vicinity;
          const priceRange = competitor.priceRange || competitor.price_level ? '$'.repeat(competitor.price_level || 2) : '';
          const reviewCount = competitor.userRatingsTotal || competitor.user_ratings_total || competitor.total_reviews;
          const types = competitor.type || competitor.types?.join(', ') || '';
          const strengths = competitor.strengths || competitor.competitive_intelligence?.strengths || [];
          const weaknesses = competitor.weaknesses || competitor.competitive_intelligence?.weaknesses || [];
          
          return (
            <div key={idx} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{name}</h3>
                  {types && <p className="text-xs text-gray-500">{types}</p>}
                </div>
                {competitor.trend && competitor.marketShare && (
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    competitor.trend === 'up' ? 'bg-green-100 text-green-700' :
                    competitor.trend === 'down' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {competitor.trend === 'up' ? <TrendingUp className="h-3 w-3 inline" /> :
                     competitor.trend === 'down' ? <TrendingDown className="h-3 w-3 inline" /> :
                     '→'} {competitor.marketShare}%
                  </span>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600 mb-4 flex-wrap">
                {address && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" /> {competitor.distance || address}
                  </span>
                )}
                {rating && (
                  <span className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-500" /> {rating}
                    {reviewCount && <span className="text-xs text-gray-400">({reviewCount})</span>}
                  </span>
                )}
                {priceRange && <span>{priceRange}</span>}
              </div>

              {(strengths.length > 0 || weaknesses.length > 0) && (
                <div className="space-y-3">
                  {strengths.length > 0 && (
                    <div>
                      <p className="text-xs text-green-600 font-medium mb-1">Strengths</p>
                      <div className="flex flex-wrap gap-1">
                        {strengths.map((s: string, i: number) => (
                          <span key={i} className="px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs">{s}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {weaknesses.length > 0 && (
                    <div>
                      <p className="text-xs text-red-600 font-medium mb-1">Weaknesses</p>
                      <div className="flex flex-wrap gap-1">
                        {weaknesses.map((w: string, i: number) => (
                          <span key={i} className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-xs">{w}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Show social media / website if available from enrichment */}
              {(competitor.website || competitor.contact?.website) && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <a 
                    href={competitor.website || competitor.contact?.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:text-blue-800 underline"
                  >
                    Visit website →
                  </a>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Market Position Summary */}
      <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-5 border border-orange-200">
        <h3 className="font-semibold text-orange-900 mb-3">📊 Market Positioning</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">{competitors.length}</p>
            <p className="text-xs text-gray-600">Competitors</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">
              {competitors.length > 0 ? (competitors.reduce((sum: number, c: any) => sum + (Number(c.rating || c.google_rating) || 0), 0) / competitors.length).toFixed(1) : 'N/A'}
            </p>
            <p className="text-xs text-gray-600">Average Rating</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">
              {competitors.reduce((sum: number, c: any) => sum + (Number(c.userRatingsTotal || c.user_ratings_total || c.total_reviews) || 0), 0)}
            </p>
            <p className="text-xs text-gray-600">Total Reviews</p>
          </div>
        </div>
      </div>

      {/* AI Agent Debate */}
      <AgentDebateTrigger
        sessionId={sessionId}
        topic={`Competitive Strategy against ${competitors.length} nearby competitors`}
        context={`Competitors: ${competitors.map((c: any) => c.name || c.business_name).join(', ')}. Average market rating: ${competitors.length > 0 ? (competitors.reduce((s: number, c: any) => s + (Number(c.rating || c.google_rating) || 0), 0) / competitors.length).toFixed(1) : 'N/A'}`}
        variant="card"
      />

      {/* Recommendations */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Strategic Recommendations</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="text-orange-500">→</span>
            Differentiate by quality and experience vs low-cost competitors
          </li>
          <li className="flex items-start gap-2">
            <span className="text-orange-500">→</span>
            Improve digital presence to compete with better-positioned establishments
          </li>
          <li className="flex items-start gap-2">
            <span className="text-orange-500">→</span>
            Consider specific promotions to attract customers from declining competitors
          </li>
        </ul>
      </div>

      {/* Add Links Suggestion */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 text-sm text-gray-600">
        <p className="font-medium mb-1">💡 Enrich this analysis</p>
        <p>Add social media links, Google Maps reviews, or TripAdvisor links of your competitors on the setup page for a more detailed analysis with Gemini.</p>
      </div>
    </div>
  );
}
