'use client';

import { api, PredictionResult } from '@/lib/api';
import { use, useEffect, useState } from 'react';


interface PredictionsPageProps {
  params: Promise<{ sessionId: string }>;
}

const ALL_PERIODS = [
  { value: '30d', label: '30 días' },
  { value: '90d', label: '3 meses' },
  { value: '180d', label: '6 meses' },
  { value: '365d', label: '1 año' },
  { value: 'all', label: 'Todo' },
];

function getAvailablePeriods(sessionData: any) {
  // Handle nested data structure
  const data = sessionData?.data || sessionData;
  const availableInfo = data?.available_periods;
  const available = availableInfo?.available_periods || [];
  
  // If no available periods info, return all periods
  if (available.length === 0) return ALL_PERIODS;
  
  // Filter to only show available periods
  let filtered = ALL_PERIODS.filter(p => available.includes(p.value));

  // Remove 'all' if redundant (e.g. we have another period that covers the same records)
  const periodInfo = availableInfo?.period_info;
  if (periodInfo && filtered.length > 1) {
    const allInfo = periodInfo['all'];
    if (allInfo) {
       const redundant = filtered.some(p => p.value !== 'all' && periodInfo[p.value]?.records === allInfo.records);
       if (redundant) {
         filtered = filtered.filter(p => p.value !== 'all');
       }
    }
  }

  return filtered;
}

export default function PredictionsPage({ params }: PredictionsPageProps) {
  const { sessionId } = use(params);
  const [data, setData] = useState<PredictionResult | null>(null);
  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('all');
  const [retrainingLoading, setRetrainingLoading] = useState(false);

  const fetchPredictions = async () => {
    try {
      const session = (sessionId === 'demo-session-001' || sessionId === 'margarita-pinta-demo-001')
        ? await api.getDemoSession()
        : await api.getSession(sessionId);
      setSessionData(session);
      
      // Handle both formats: direct predictions object or nested in data
      const sessionData = session.data || session;
      if (sessionData.predictions) {
        setData(sessionData.predictions);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  const retrainWithPeriod = async (period: string) => {
    setRetrainingLoading(true);
    setSelectedPeriod(period);
    setError(null);
    
    try {
      // Call predictions API with period parameter
      const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
      const response = await fetch(
        `${API_URL}/api/v1/predict/sales?session_id=${sessionId}&period=${period}`,
        { method: 'POST' }
      );
      
      if (!response.ok) throw new Error('Failed to retrain predictions');
      
      const result = await response.json();
      setData(result);
      
      // Update session data
      await fetchPredictions();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to retrain model');
    } finally {
      setRetrainingLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, [sessionId]);

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

  const availablePeriods = sessionData ? getAvailablePeriods(sessionData) : [];

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold">Sales Predictions</h2>
          <span className="text-sm text-gray-500">
            {data.predictions.length} days forecasted
          </span>
        </div>
        
        {/* Period Selector */}
        {availablePeriods.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Training period:</span>
            <div className="flex bg-gray-100 rounded-lg p-1">
              {availablePeriods.map((p) => (
                <button
                  key={p.value}
                  onClick={() => retrainWithPeriod(p.value)}
                  disabled={retrainingLoading}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    selectedPeriod === p.value
                      ? 'bg-white text-blue-600 shadow-sm font-medium'
                      : 'text-gray-600 hover:text-gray-900'
                  } disabled:opacity-50`}
                >
                  {p.label}
                </button>
              ))}
            </div>
            {retrainingLoading && (
              <span className="text-xs text-blue-600">Re-training...</span>
            )}
          </div>
        )}
      </div>
      
      {/* Info about period-based training */}
      {availablePeriods.length > 0 && (
        <div className="mb-6 p-3 bg-blue-50 rounded-lg border border-blue-200 text-sm text-blue-800">
          <strong>💡 Pro tip:</strong> Training with more data (longer periods) typically improves prediction accuracy. 
          Current training data: {selectedPeriod === 'all' ? 'All available data' : availablePeriods.find(p => p.value === selectedPeriod)?.label}
        </div>
      )}

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
