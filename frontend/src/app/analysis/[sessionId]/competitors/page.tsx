'use client';

import { AgentDebateTrigger } from '@/components/ai/AgentDebateTrigger';
import { GroundingSources } from '@/components/common/GroundingSources';
import { Globe, Loader2, MapPin, Search, Shield, Star, Target, TrendingDown, TrendingUp } from 'lucide-react';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { useSessionData } from '../layout';


export default function CompetitorsPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { sessionData, isLoading } = useSessionData();
  const [trends, setTrends] = useState<any>(null);
  const [loadingTrends, setLoadingTrends] = useState(false);
  const [groundedCompetitor, setGroundedCompetitor] = useState<any>(null);
  const [loadingGrounded, setLoadingGrounded] = useState<string | null>(null);
  const [verifyResult, setVerifyResult] = useState<any>(null);
  const [verifying, setVerifying] = useState(false);

  const unwrappedSession = (sessionData as any)?.data || sessionData;
  const restaurantInfo = unwrappedSession?.restaurant_info || {};
  const location = restaurantInfo?.location || restaurantInfo?.address || '';
  const cuisine = restaurantInfo?.cuisine || 'restaurant';

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
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Target className="w-5 h-5 text-teal-600" />
                Competitor Analysis
              </h1>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200/60 rounded-full text-[10px] font-semibold text-blue-700">
                <Globe className="h-2.5 w-2.5" /> Google Search Grounding · Auto-cited
              </span>
            </div>
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

              {/* Grounded Deep-Dive Button */}
              <div className="mt-3 pt-3 border-t border-gray-100">
                <button
                  onClick={async () => {
                    setLoadingGrounded(name);
                    try {
                      const res = await fetch('/api/v1/grounding/competitor/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ competitor_name: name, location, cuisine_type: cuisine }),
                      });
                      if (res.ok) setGroundedCompetitor(await res.json());
                    } catch (err) { console.warn('Grounded analysis failed:', err); }
                    finally { setLoadingGrounded(null); }
                  }}
                  disabled={loadingGrounded === name}
                  className="inline-flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 font-medium disabled:opacity-50"
                >
                  {loadingGrounded === name ? <Loader2 className="h-3 w-3 animate-spin" /> : <Search className="h-3 w-3" />}
                  Deep Dive with Google Search
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Grounding Actions Bar */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={async () => {
            setLoadingTrends(true);
            try {
              const res = await fetch('/api/v1/grounding/trends/research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cuisine_type: cuisine, location, time_period: 'last 6 months' }),
              });
              if (res.ok) setTrends(await res.json());
            } catch (err) { console.warn('Trends failed:', err); }
            finally { setLoadingTrends(false); }
          }}
          disabled={loadingTrends}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-cyan-700 bg-cyan-50 border border-cyan-200 rounded-lg hover:bg-cyan-100 transition-colors disabled:opacity-50"
        >
          {loadingTrends ? <Loader2 className="h-4 w-4 animate-spin" /> : <Globe className="h-4 w-4" />}
          {trends ? 'Trends Loaded ✓' : 'Research Market Trends'}
        </button>
        <button
          onClick={async () => {
            setVerifying(true);
            try {
              const res = await fetch('/api/v1/grounding/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  claim: `Competitive analysis of ${competitors.length} restaurants near ${location} is accurate`,
                  context: `Competitors: ${competitors.map((c: any) => c.name || c.business_name).join(', ')}`,
                }),
              });
              if (res.ok) setVerifyResult(await res.json());
            } catch (err) { console.warn('Verify failed:', err); }
            finally { setVerifying(false); }
          }}
          disabled={verifying}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors disabled:opacity-50"
        >
          {verifying ? <Loader2 className="h-4 w-4 animate-spin" /> : <Shield className="h-4 w-4" />}
          {verifyResult ? 'Verified ✓' : 'Verify with Sources'}
        </button>
      </div>

      {/* Market Trends Results */}
      {trends && (
        <div className="bg-cyan-50 border border-cyan-200 rounded-xl p-5">
          <h3 className="text-lg font-semibold text-cyan-900 mb-3 flex items-center gap-2">
            <Globe className="h-5 w-5" /> Market Trends — {cuisine} in {location}
          </h3>
          {Array.isArray(trends) ? (
            <div className="grid md:grid-cols-2 gap-3">
              {trends.slice(0, 6).map((trend: any, i: number) => (
                <div key={i} className="bg-white/70 rounded-lg p-3 border border-cyan-100">
                  <p className="font-medium text-gray-900 text-sm">{trend.name || trend.trend || `Trend ${i+1}`}</p>
                  <p className="text-xs text-gray-600 mt-1">{trend.description || trend.summary || JSON.stringify(trend).slice(0, 120)}</p>
                  {trend.sources?.length > 0 && (
                    <GroundingSources sources={trend.sources} isGrounded={true} variant="compact" />
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-700 whitespace-pre-wrap bg-white/60 rounded-lg p-3">
              {typeof trends === 'string' ? trends : JSON.stringify(trends, null, 2)}
            </div>
          )}
        </div>
      )}

      {/* Verification Result */}
      {verifyResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-emerald-900 mb-2 flex items-center gap-2">
            <Shield className="h-4 w-4" /> Verification Result
          </h3>
          {verifyResult.sources && <GroundingSources sources={verifyResult.sources} isGrounded={true} variant="compact" />}
          {verifyResult.result && (
            <p className="text-sm text-gray-700 mt-2">{typeof verifyResult.result === 'string' ? verifyResult.result : JSON.stringify(verifyResult.result).slice(0, 300)}</p>
          )}
        </div>
      )}

      {/* Grounded Deep-Dive on individual competitor */}
      {groundedCompetitor && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
          <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <Search className="h-5 w-5" /> Deep Dive — {groundedCompetitor.name || 'Competitor'}
          </h3>
          <div className="text-sm text-gray-700 whitespace-pre-wrap bg-white/60 rounded-lg p-3">
            {typeof groundedCompetitor === 'string' ? groundedCompetitor : JSON.stringify(groundedCompetitor, null, 2).slice(0, 1000)}
          </div>
          {groundedCompetitor.sources?.length > 0 && (
            <GroundingSources sources={groundedCompetitor.sources} isGrounded={true} />
          )}
        </div>
      )}

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
