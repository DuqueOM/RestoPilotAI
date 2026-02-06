'use client';

import { AgentDebateTrigger } from '@/components/ai/AgentDebateTrigger';
import { ExternalLink, MapPin, MessageCircle, Star, ThumbsDown, ThumbsUp, TrendingUp } from 'lucide-react';
import { useParams } from 'next/navigation';
import { useSessionData } from '../layout';


export default function SentimentPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { sessionData, isLoading } = useSessionData();

  const unwrappedSession = (sessionData as any)?.data || sessionData;

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-gray-200 rounded w-48"></div>
        <div className="grid md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-100 rounded-xl"></div>)}
        </div>
      </div>
    );
  }

  // Get sentiment data from full pipeline analysis
  const sentimentData = unwrappedSession?.sentiment_analysis || sessionData?.sentiment_analysis;

  // Get Google Maps reviews from enriched business profile
  const enrichedProfile = unwrappedSession?.business_profile_enriched || sessionData?.business_profile_enriched;
  const googleMapsData = enrichedProfile?.google_maps;
  const googleReviews = googleMapsData?.reviews || [];
  const reviewsSummary = googleMapsData?.reviews_summary;
  const restaurantInfo = unwrappedSession?.restaurant_info || sessionData?.restaurant_info;
  const businessRating = enrichedProfile?.rating || googleMapsData?.rating || restaurantInfo?.rating;
  const totalRatings = googleMapsData?.user_ratings_total || enrichedProfile?.user_ratings_total || restaurantInfo?.user_ratings_total;
  const businessName = enrichedProfile?.name || restaurantInfo?.name;
  const placeId = enrichedProfile?.location?.place_id || unwrappedSession?.restaurant_info?.place_id;
  const googleMapsUri = googleMapsData?.google_maps_uri || enrichedProfile?.google_maps?.google_maps_uri;
  const googleMapsLinks = googleMapsData?.google_maps_links || enrichedProfile?.google_maps?.google_maps_links || {};
  const googleMapsUrl = googleMapsUri || googleMapsLinks?.placeUri || (placeId ? `https://www.google.com/maps/place/?q=place_id:${placeId}` : null);
  const reviewsUrl = googleMapsLinks?.reviewsUri || googleMapsUrl;

  // Also get competitor reviews for comparison
  const competitors = unwrappedSession?.enriched_competitors || unwrappedSession?.competitors || sessionData?.enriched_competitors || sessionData?.competitors || [];
  const competitorReviews = competitors.flatMap((c: any) => 
    (c.google_maps?.reviews || []).map((r: any) => ({ ...r, competitor_name: c.name }))
  );

  const hasAnyData = sentimentData || googleReviews.length > 0 || businessRating;

  if (!hasAnyData && !isLoading) {
    return (
      <div className="text-center py-12 text-gray-500">
        <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p className="text-lg">No sentiment analysis available</p>
        <p className="text-sm mt-2">Select a location with Google Maps reviews to view the analysis.</p>
      </div>
    );
  }

  const audioContext = unwrappedSession?.audio_analysis || sessionData?.audio_analysis;

  const _getSentimentColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 bg-green-100';
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const _getRatingColor = (rating: number) => {
    if (rating >= 4) return 'text-green-600';
    if (rating >= 3) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Calculate average from Google reviews
  const avgReviewRating = googleReviews.length > 0
    ? (googleReviews.reduce((sum: number, r: any) => sum + (r.rating || 0), 0) / googleReviews.length)
    : businessRating || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <MessageCircle className="h-6 w-6 text-blue-500" />
          Sentiment Analysis
        </h2>
        {googleMapsUrl && (
          <a
            href={googleMapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            <MapPin className="h-4 w-4" />
            View on Google Maps
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>

      {/* Overall Rating from Google Maps */}
      {businessRating && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-600 rounded-xl p-6 text-white">
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-blue-100 text-sm mb-1">Google Maps Rating</p>
              <p className="text-4xl font-bold flex items-center justify-center gap-2">
                <Star className="h-8 w-8 text-yellow-300 fill-yellow-300" />
                {Number(businessRating).toFixed(1)}
              </p>
              <p className="text-blue-200">out of 5.0</p>
            </div>
            <div className="text-center">
              <p className="text-blue-100 text-sm mb-1">Total Reviews</p>
              <p className="text-2xl font-bold">{totalRatings || googleReviews.length}</p>
            </div>
            <div className="text-center">
              <p className="text-blue-100 text-sm mb-1">Recent Reviews</p>
              <p className="text-2xl font-bold">{googleReviews.length}</p>
              <p className="text-blue-200">available</p>
            </div>
            <div className="text-center">
              <p className="text-blue-100 text-sm mb-1">Sentiment</p>
              <p className="text-2xl font-bold">
                {avgReviewRating >= 4 ? 'Positive' : avgReviewRating >= 3 ? 'Mixed' : 'Negative'}
              </p>
              <p className="text-blue-200">
                {avgReviewRating >= 4 ? '😊' : avgReviewRating >= 3 ? '😐' : '😟'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Full Pipeline Sentiment (if available) */}
      {sentimentData && (
        <>
          <div className="bg-gradient-to-r from-purple-500 to-violet-600 rounded-xl p-6 text-white">
            <h3 className="font-semibold mb-4">Advanced Sentiment Analysis (AI)</h3>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-purple-100 text-sm mb-1">Overall Sentiment</p>
                <p className="text-4xl font-bold">{(sentimentData.overall.score * 100).toFixed(0)}%</p>
                <p className="text-purple-200">{sentimentData.overall.label}</p>
              </div>
              <div className="text-center">
                <p className="text-purple-100 text-sm mb-1">Trend</p>
                <p className="text-2xl font-bold flex items-center justify-center gap-2">
                  <TrendingUp className="h-6 w-6" />
                  {sentimentData.overall.trend === 'improving' ? 'Improving' : 
                   sentimentData.overall.trend === 'declining' ? 'Declining' : 'Stable'}
                </p>
              </div>
              <div className="text-center">
                <p className="text-purple-100 text-sm mb-1">Sources</p>
                <p className="text-2xl font-bold">{sentimentData.sources?.length || 0}</p>
              </div>
              <div className="text-center">
                <p className="text-purple-100 text-sm mb-1">Topics</p>
                <p className="text-2xl font-bold">{sentimentData.topics?.length || 0}</p>
              </div>
            </div>
          </div>

          {/* Topics Analysis */}
          {sentimentData.topics?.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-900 mb-4">📊 Topic Analysis</h3>
              <div className="space-y-4">
                {sentimentData.topics.map((topic: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-4">
                    <div className="w-32 text-sm font-medium text-gray-700">{topic.topic}</div>
                    <div className="flex-1">
                      <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            topic.sentiment >= 0.7 ? 'bg-green-500' :
                            topic.sentiment >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${topic.sentiment * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="w-16 text-right text-sm font-medium">
                      {(topic.sentiment * 100).toFixed(0)}%
                    </div>
                    <div className="w-20 text-right text-xs text-gray-500">
                      {topic.mentions} mentions
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Reviews Summary from Gemini */}
      {reviewsSummary && (
        <div className="bg-indigo-50 rounded-xl p-5 border border-indigo-200">
          <h3 className="font-semibold text-indigo-900 mb-2">🤖 Reviews Summary (Gemini AI)</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{reviewsSummary}</p>
        </div>
      )}

      {/* Audio Analysis Results if available */}
      {audioContext && (audioContext.business?.length > 0 || audioContext.competitor?.length > 0) && (
        <div className="bg-violet-50 rounded-xl p-5 border border-violet-200">
          <h3 className="font-semibold text-violet-900 mb-3">🎙️ Audio Analysis (Gemini Multimodal)</h3>
          <div className="space-y-3">
            {audioContext.business?.map((analysis: any, idx: number) => (
              <div key={idx} className="bg-white/60 rounded-lg p-3">
                <p className="text-sm font-medium text-violet-800">Audio #{idx + 1}</p>
                <p className="text-sm text-gray-700 mt-1">{analysis.summary}</p>
                <div className="flex gap-2 mt-2">
                  {analysis.key_points?.slice(0, 3).map((point: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-violet-100 text-violet-700 rounded text-xs">{point}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Google Maps Reviews */}
      {googleReviews.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">💬 Google Maps Reviews — {businessName}</h3>
            {reviewsUrl && (
              <a
                href={reviewsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                View all reviews <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
          <div className="space-y-4">
            {googleReviews.map((review: any, idx: number) => (
              <div key={idx} className="flex gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                {review.author_photo ? (
                  <img src={review.author_photo} alt={review.author_name} className="w-10 h-10 rounded-full object-cover flex-shrink-0" />
                ) : (
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${(review.rating || 0) >= 4 ? 'bg-green-100' : (review.rating || 0) >= 3 ? 'bg-yellow-100' : 'bg-red-100'}`}>
                    {(review.rating || 0) >= 4 ? <ThumbsUp className="h-4 w-4 text-green-600" /> : <ThumbsDown className="h-4 w-4 text-yellow-600" />}
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {review.author_uri ? (
                      <a href={review.author_uri} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-gray-900 hover:text-blue-600">
                        {review.author_name || 'User'}
                      </a>
                    ) : (
                      <span className="text-sm font-medium text-gray-900">{review.author_name || 'User'}</span>
                    )}
                    <span className="flex items-center gap-0.5">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`h-3 w-3 ${i < (review.rating || 0) ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                      ))}
                    </span>
                  </div>
                  {review.text && (
                    <p className="text-sm text-gray-700">"{review.text}"</p>
                  )}
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span>{review.relative_time_description || review.time || ''}</span>
                    {review.google_maps_uri ? (
                      <a href={review.google_maps_uri} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:text-blue-700 flex items-center gap-1">
                        View on Google Maps <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : (
                      <span className="text-blue-500">Google Maps</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Competitor Reviews Comparison */}
      {competitorReviews.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4">🔍 Competitor Reviews (Comparison)</h3>
          <div className="space-y-4">
            {competitorReviews.slice(0, 10).map((review: any, idx: number) => (
              <div key={idx} className="flex gap-4 p-4 bg-orange-50/50 rounded-lg">
                <div className={`p-2 rounded-full h-fit ${(review.rating || 0) >= 4 ? 'bg-green-100' : 'bg-yellow-100'}`}>
                  {(review.rating || 0) >= 4 ? <ThumbsUp className="h-4 w-4 text-green-600" /> : <ThumbsDown className="h-4 w-4 text-yellow-600" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-orange-700 bg-orange-100 px-2 py-0.5 rounded">{review.competitor_name}</span>
                    <span className="text-sm font-medium text-gray-900">{review.author_name || 'User'}</span>
                    <span className="flex items-center gap-0.5">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`h-3 w-3 ${i < (review.rating || 0) ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                      ))}
                    </span>
                  </div>
                  {review.text && (
                    <p className="text-sm text-gray-700">"{review.text}"</p>
                  )}
                  <span className="text-xs text-gray-500 mt-1 block">{review.relative_time_description || ''}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rating Comparison with Competitors */}
      {/* AI Agent Debate on Reputation */}
      <AgentDebateTrigger
        sessionId={sessionId}
        topic={`Reputation Strategy: ${avgReviewRating.toFixed(1)}/5 rating with ${googleReviews.length} reviews`}
        context={sentimentData ? `Overall sentiment: ${(sentimentData.overall.score * 100).toFixed(0)}%, Trend: ${sentimentData.overall.trend}` : `Google rating: ${businessRating || 'N/A'}`}
        variant="card"
      />

      {competitors.length > 0 && businessRating && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-4">📊 Rating Comparison</h3>
          <div className="space-y-3">
            {/* Your business */}
            <div className="flex items-center gap-4">
              <div className="w-40 text-sm font-bold text-blue-700 truncate">{businessName || 'Your business'}</div>
              <div className="flex-1">
                <div className="h-6 bg-white rounded-full overflow-hidden border">
                  <div 
                    className="h-full bg-blue-500 rounded-full flex items-center justify-end pr-2"
                    style={{ width: `${(Number(businessRating) / 5) * 100}%` }}
                  >
                    <span className="text-xs text-white font-bold">{Number(businessRating).toFixed(1)}</span>
                  </div>
                </div>
              </div>
              <div className="w-16 text-right text-sm font-medium text-gray-600">
                {totalRatings || '?'} rev.
              </div>
            </div>
            {/* Competitors */}
            {competitors.map((c: any, idx: number) => {
              const cRating = c.rating || c.google_rating || c.google_maps?.rating;
              const cTotal = c.user_ratings_total || c.userRatingsTotal || c.google_maps?.user_ratings_total;
              if (!cRating) return null;
              return (
                <div key={idx} className="flex items-center gap-4">
                  <div className="w-40 text-sm font-medium text-gray-700 truncate">{c.name}</div>
                  <div className="flex-1">
                    <div className="h-6 bg-white rounded-full overflow-hidden border">
                      <div 
                        className={`h-full rounded-full flex items-center justify-end pr-2 ${
                          Number(cRating) > Number(businessRating) ? 'bg-red-400' : 'bg-green-400'
                        }`}
                        style={{ width: `${(Number(cRating) / 5) * 100}%` }}
                      >
                        <span className="text-xs text-white font-bold">{Number(cRating).toFixed(1)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="w-16 text-right text-sm font-medium text-gray-600">
                    {cTotal || '?'} rev.
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
