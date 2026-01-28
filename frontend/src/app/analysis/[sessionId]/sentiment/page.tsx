'use client';

import { api } from '@/lib/api';
import { MessageCircle, Star, ThumbsDown, ThumbsUp, TrendingUp } from 'lucide-react';
import { use, useEffect, useState } from 'react';


interface SentimentPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function SentimentPage({ params }: SentimentPageProps) {
  const { sessionId } = use(params);
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(sessionId);
        setSession(data);
      } catch (err) {
        console.error('Failed to load session:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-gray-200 rounded w-48"></div>
        <div className="grid md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-100 rounded-xl"></div>)}
        </div>
      </div>
    );
  }

  // Demo sentiment data - in real implementation from audio/link analysis
  const sentimentData = session?.sentiment_analysis || {
    overall: {
      score: 0.72,
      label: "Positivo",
      trend: "improving"
    },
    sources: [
      { name: "Google Reviews", count: 156, avgRating: 4.3, sentiment: 0.78 },
      { name: "TripAdvisor", count: 89, avgRating: 4.1, sentiment: 0.71 },
      { name: "Redes Sociales", count: 234, avgRating: null, sentiment: 0.68 }
    ],
    topics: [
      { topic: "Calidad de comida", sentiment: 0.85, mentions: 120, trend: "up" },
      { topic: "Servicio", sentiment: 0.65, mentions: 89, trend: "stable" },
      { topic: "Ambiente", sentiment: 0.78, mentions: 67, trend: "up" },
      { topic: "Precios", sentiment: 0.52, mentions: 95, trend: "down" },
      { topic: "Tiempo de espera", sentiment: 0.45, mentions: 43, trend: "stable" }
    ],
    recentReviews: [
      { text: "Excelente comida, los tacos al pastor son los mejores de la zona", rating: 5, source: "Google", date: "hace 2 días" },
      { text: "Buen ambiente pero el servicio fue un poco lento", rating: 4, source: "TripAdvisor", date: "hace 3 días" },
      { text: "Precios un poco elevados para las porciones, pero calidad top", rating: 4, source: "Google", date: "hace 5 días" }
    ]
  };

  const audioContext = session?.audio_analysis;
  const businessContext = session?.business_context || "";

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 bg-green-100';
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <MessageCircle className="h-6 w-6 text-blue-500" />
          Análisis de Sentimiento
        </h2>
      </div>

      {/* Overall Sentiment */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl p-6 text-white">
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-blue-100 text-sm mb-1">Sentimiento General</p>
            <p className="text-4xl font-bold">{(sentimentData.overall.score * 100).toFixed(0)}%</p>
            <p className="text-blue-200">{sentimentData.overall.label}</p>
          </div>
          <div className="text-center">
            <p className="text-blue-100 text-sm mb-1">Tendencia</p>
            <p className="text-2xl font-bold flex items-center justify-center gap-2">
              <TrendingUp className="h-6 w-6" />
              {sentimentData.overall.trend === 'improving' ? 'Mejorando' : 
               sentimentData.overall.trend === 'declining' ? 'Declinando' : 'Estable'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-blue-100 text-sm mb-1">Total Reseñas</p>
            <p className="text-2xl font-bold">
              {sentimentData.sources.reduce((sum: number, s: any) => sum + s.count, 0)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-blue-100 text-sm mb-1">Rating Promedio</p>
            <p className="text-2xl font-bold flex items-center justify-center gap-1">
              <Star className="h-5 w-5 text-yellow-300" />
              {(sentimentData.sources.filter((s: any) => s.avgRating).reduce((sum: number, s: any) => sum + s.avgRating, 0) / 
                sentimentData.sources.filter((s: any) => s.avgRating).length).toFixed(1)}
            </p>
          </div>
        </div>
      </div>

      {/* Audio Analysis Results if available */}
      {audioContext && (audioContext.business?.length > 0 || audioContext.competitor?.length > 0) && (
        <div className="bg-violet-50 rounded-xl p-5 border border-violet-200">
          <h3 className="font-semibold text-violet-900 mb-3">🎙️ Análisis de Audio (Gemini Multimodal)</h3>
          <div className="space-y-3">
            {audioContext.business?.map((analysis: any, idx: number) => (
              <div key={idx} className="bg-white/60 rounded-lg p-3">
                <p className="text-sm font-medium text-violet-800">Audio de Negocio #{idx + 1}</p>
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

      {/* Sources Breakdown */}
      <div className="grid md:grid-cols-3 gap-4">
        {sentimentData.sources.map((source: any, idx: number) => (
          <div key={idx} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">{source.name}</h3>
              <span className={`px-2 py-1 rounded text-sm font-medium ${getSentimentColor(source.sentiment)}`}>
                {(source.sentiment * 100).toFixed(0)}%
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Reseñas</span>
                <span className="font-medium">{source.count}</span>
              </div>
              {source.avgRating && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Rating</span>
                  <span className="font-medium flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-500" /> {source.avgRating}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Topics Analysis */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-4">📊 Análisis por Tema</h3>
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
                {topic.mentions} menciones
              </div>
              <div className={`w-8 text-center ${
                topic.trend === 'up' ? 'text-green-500' :
                topic.trend === 'down' ? 'text-red-500' : 'text-gray-400'
              }`}>
                {topic.trend === 'up' ? '↑' : topic.trend === 'down' ? '↓' : '→'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reviews */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-4">💬 Reseñas Recientes</h3>
        <div className="space-y-4">
          {sentimentData.recentReviews.map((review: any, idx: number) => (
            <div key={idx} className="flex gap-4 p-3 bg-gray-50 rounded-lg">
              <div className={`p-2 rounded-full h-fit ${review.rating >= 4 ? 'bg-green-100' : 'bg-yellow-100'}`}>
                {review.rating >= 4 ? <ThumbsUp className="h-4 w-4 text-green-600" /> : <ThumbsDown className="h-4 w-4 text-yellow-600" />}
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-700">"{review.text}"</p>
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className={`h-3 w-3 ${i < review.rating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                    ))}
                  </span>
                  <span>{review.source}</span>
                  <span>{review.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Links Suggestion */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 text-sm text-gray-600">
        <p className="font-medium mb-1">💡 Enriquece este análisis</p>
        <p>Agrega links de Google Reviews, TripAdvisor, Yelp o redes sociales en la página de carga. También puedes subir audios con feedback de clientes para que Gemini los analice directamente.</p>
      </div>
    </div>
  );
}
