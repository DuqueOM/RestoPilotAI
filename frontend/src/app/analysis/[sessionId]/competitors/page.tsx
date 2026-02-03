'use client';

import { api } from '@/lib/api';
import { MapPin, Star, Target, TrendingDown, TrendingUp } from 'lucide-react';
import { use, useEffect, useState } from 'react';


interface CompetitorsPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function CompetitorsPage({ params }: CompetitorsPageProps) {
  const { sessionId } = use(params);
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = (sessionId === 'demo-session-001' || sessionId === 'margarita-pinta-demo-001')
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
        <div className="grid md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-48 bg-gray-100 rounded-xl"></div>)}
        </div>
      </div>
    );
  }

  // Get competitors from session data
  const competitors = session?.competitor_analysis?.competitors || [];
  const competitorContext = session?.competitor_context || "";

  if (!competitors.length && !loading) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Target className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p className="text-lg">No hay análisis de competencia disponible</p>
        <p className="text-sm mt-2">Ejecuta el análisis para identificar competidores.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Target className="h-6 w-6 text-orange-500" />
          Análisis de Competencia
        </h2>
        <span className="text-sm text-gray-500">{competitors.length} competidores identificados</span>
      </div>

      {/* Context from audio/text if available */}
      {competitorContext && (
        <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
          <h3 className="font-medium text-orange-800 mb-2">📝 Contexto Proporcionado</h3>
          <p className="text-sm text-gray-700">{competitorContext}</p>
        </div>
      )}

      {/* Competitor Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {competitors.map((competitor: any, idx: number) => (
          <div key={idx} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold text-gray-900">{competitor.name}</h3>
                <p className="text-xs text-gray-500">{competitor.type}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                competitor.trend === 'up' ? 'bg-green-100 text-green-700' :
                competitor.trend === 'down' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {competitor.trend === 'up' ? <TrendingUp className="h-3 w-3 inline" /> :
                 competitor.trend === 'down' ? <TrendingDown className="h-3 w-3 inline" /> :
                 '→'} {competitor.marketShare}%
              </span>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
              <span className="flex items-center gap-1">
                <MapPin className="h-4 w-4" /> {competitor.distance}
              </span>
              <span className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-500" /> {competitor.rating}
              </span>
              <span>{competitor.priceRange}</span>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-xs text-green-600 font-medium mb-1">Fortalezas</p>
                <div className="flex flex-wrap gap-1">
                  {competitor.strengths?.map((s: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs">{s}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs text-red-600 font-medium mb-1">Debilidades</p>
                <div className="flex flex-wrap gap-1">
                  {competitor.weaknesses?.map((w: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-xs">{w}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Market Position Summary */}
      <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-5 border border-orange-200">
        <h3 className="font-semibold text-orange-900 mb-3">📊 Posicionamiento en el Mercado</h3>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">
              {100 - competitors.reduce((sum: number, c: any) => sum + c.marketShare, 0)}%
            </p>
            <p className="text-xs text-gray-600">Tu Market Share</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">{competitors.length}</p>
            <p className="text-xs text-gray-600">Competidores</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">
              {(competitors.reduce((sum: number, c: any) => sum + c.rating, 0) / competitors.length).toFixed(1)}
            </p>
            <p className="text-xs text-gray-600">Rating Promedio</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-orange-700">
              {competitors.filter((c: any) => c.trend === 'up').length}
            </p>
            <p className="text-xs text-gray-600">En Crecimiento</p>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Recomendaciones Estratégicas</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="text-orange-500">→</span>
            Diferenciarte por calidad y experiencia frente a competidores de bajo costo
          </li>
          <li className="flex items-start gap-2">
            <span className="text-orange-500">→</span>
            Mejorar presencia digital para competir con establecimientos mejor posicionados
          </li>
          <li className="flex items-start gap-2">
            <span className="text-orange-500">→</span>
            Considerar promociones específicas para atraer clientes de competidores en declive
          </li>
        </ul>
      </div>

      {/* Add Links Suggestion */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 text-sm text-gray-600">
        <p className="font-medium mb-1">💡 Enriquece este análisis</p>
        <p>Agrega links de redes sociales, reseñas de Google Maps o TripAdvisor de tus competidores en la página de carga para un análisis más detallado con Gemini.</p>
      </div>
    </div>
  );
}
