'use client';

import { api, PredictionResult } from '@/lib/api';
import { useEffect, useState } from 'react';

interface PredictionsPageProps {
  params: { sessionId: string };
}

export default function PredictionsPage({ params }: PredictionsPageProps) {
  const [data, setData] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const session = params.sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(params.sessionId);
        if (session.predictions) {
          setData(session.predictions);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load predictions');
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, [params.sessionId]);

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 text-lg mb-2">⚠️ Error</div>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  if (!data || !data.predictions?.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-4xl mb-4">📈</p>
        <p>No sales predictions available yet.</p>
        <p className="text-sm mt-2">Upload sales data to generate forecasts.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Sales Predictions</h2>
        <span className="text-sm text-gray-500">
          {data.predictions.length} days forecasted
        </span>
      </div>

      {/* Metrics Cards */}
      {data.metrics && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          <MetricCard
            label="MAPE"
            value={`${(data.metrics.mape * 100).toFixed(1)}%`}
            description="Mean Absolute % Error"
            good={data.metrics.mape < 0.1}
          />
          <MetricCard
            label="RMSE"
            value={data.metrics.rmse.toFixed(2)}
            description="Root Mean Square Error"
            good={data.metrics.rmse < 100}
          />
          <MetricCard
            label="R²"
            value={data.metrics.r2.toFixed(3)}
            description="Coefficient of Determination"
            good={data.metrics.r2 > 0.8}
          />
        </div>
      )}

      {/* Predictions Chart Placeholder */}
      <div className="bg-gray-50 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">Forecast Visualization</h3>
        <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
          <div className="text-center text-gray-500">
            <p className="text-3xl mb-2">📊</p>
            <p>Chart visualization</p>
            <p className="text-sm">Install recharts for interactive charts</p>
          </div>
        </div>
      </div>

      {/* Predictions Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="text-left py-3 px-4 font-medium text-gray-600">Date</th>
              <th className="text-right py-3 px-4 font-medium text-gray-600">Predicted</th>
              <th className="text-right py-3 px-4 font-medium text-gray-600">Actual</th>
              <th className="text-right py-3 px-4 font-medium text-gray-600">Confidence Range</th>
            </tr>
          </thead>
          <tbody>
            {data.predictions.map((pred, index) => (
              <tr key={index} className="border-b hover:bg-gray-50 transition">
                <td className="py-3 px-4">{pred.date}</td>
                <td className="py-3 px-4 text-right font-mono text-blue-600">
                  ${pred.predicted.toFixed(2)}
                </td>
                <td className="py-3 px-4 text-right font-mono">
                  {pred.actual ? `$${pred.actual.toFixed(2)}` : '-'}
                </td>
                <td className="py-3 px-4 text-right text-sm text-gray-500">
                  ${pred.confidence_lower.toFixed(0)} - ${pred.confidence_upper.toFixed(0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Insights */}
      {data.insights && data.insights.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">💡 Insights</h3>
          <div className="space-y-2">
            {data.insights.map((insight, index) => (
              <div
                key={index}
                className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm"
              >
                {insight}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  description: string;
  good: boolean;
}

function MetricCard({ label, value, description, good }: MetricCardProps) {
  return (
    <div className={`p-4 rounded-lg border ${good ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
      <div className="text-sm text-gray-600">{label}</div>
      <div className={`text-2xl font-bold ${good ? 'text-green-700' : 'text-yellow-700'}`}>
        {value}
      </div>
      <div className="text-xs text-gray-500">{description}</div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="flex items-center justify-between mb-6">
        <div className="h-6 bg-gray-200 rounded w-48"></div>
        <div className="h-4 bg-gray-200 rounded w-24"></div>
      </div>
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-lg"></div>
        ))}
      </div>
      <div className="h-64 bg-gray-100 rounded-lg"></div>
    </div>
  );
}
