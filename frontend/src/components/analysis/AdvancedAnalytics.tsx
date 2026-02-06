'use client';

import {
    AdvancedAnalyticsResult,
    api,
    DataCapabilityReport,
    MenuOptimizationResult
} from '@/lib/api';
import {
    AlertCircle,
    ArrowDown,
    ArrowUp,
    BarChart3,
    Calendar,
    CheckCircle,
    Clock,
    DollarSign,
    Lightbulb,
    Minus,
    TrendingUp,
    Zap
} from 'lucide-react';
import { useState } from 'react';

interface AdvancedAnalyticsProps {
  sessionId: string;
  hasData: boolean;
}

type TabType = 'capabilities' | 'optimization' | 'analytics';

export default function AdvancedAnalytics({ sessionId, hasData }: AdvancedAnalyticsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('capabilities');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [capabilities, setCapabilities] = useState<DataCapabilityReport | null>(null);
  const [optimization, setOptimization] = useState<MenuOptimizationResult | null>(null);
  const [analytics, setAnalytics] = useState<AdvancedAnalyticsResult | null>(null);

  const loadCapabilities = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.analyzeCapabilities(sessionId);
      setCapabilities(result);
    } catch (err) {
      setError('Failed to analyze data capabilities');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runMenuOptimization(sessionId);
      setOptimization(result);
    } catch (err) {
      setError('Failed to run menu optimization');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runAdvancedAnalytics(sessionId);
      setAnalytics(result);
    } catch (err) {
      setError('Failed to run advanced analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    if (tab === 'capabilities' && !capabilities) {
      loadCapabilities();
    } else if (tab === 'optimization' && !optimization) {
      loadOptimization();
    } else if (tab === 'analytics' && !analytics) {
      loadAnalytics();
    }
  };

  const _getActionIcon = (action: string) => {
    switch (action) {
      case 'increase_price': return <ArrowUp className="w-4 h-4 text-green-500" />;
      case 'decrease_price': return <ArrowDown className="w-4 h-4 text-red-500" />;
      case 'promote': return <Zap className="w-4 h-4 text-yellow-500" />;
      case 'remove': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  const _getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!hasData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="text-center py-8">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Advanced Analytics</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Upload sales data (CSV) to unlock advanced analytics including demand prediction, 
            menu optimization, and seasonal trends.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px">
          <button
            onClick={() => handleTabChange('capabilities')}
            className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'capabilities'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            📊 Data Capabilities
          </button>
          <button
            onClick={() => handleTabChange('optimization')}
            className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'optimization'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            💰 Menu Optimization
          </button>
          <button
            onClick={() => handleTabChange('analytics')}
            className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'analytics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            📈 Demand & Trends
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            <span className="ml-3 text-gray-600">Analyzing data...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* Capabilities Tab */}
        {activeTab === 'capabilities' && capabilities && !loading && (
          <div className="space-y-6">
            {/* Quality Score */}
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Data Quality Score</h4>
                <p className="text-sm text-gray-600">
                  {capabilities.row_count} rows · {capabilities.unique_items} items · {capabilities.date_range_days || 0} days
                </p>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {Math.round(capabilities.data_quality_score * 100)}%
              </div>
            </div>

            {/* Available Capabilities */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Available Analytics</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {capabilities.available_capabilities.map((cap) => (
                  <div key={cap} className="flex items-center p-3 bg-green-50 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    <span className="text-sm text-gray-700 capitalize">{cap.replace(/_/g, ' ')}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            {capabilities.recommendations.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Unlock More Features</h4>
                <div className="space-y-2">
                  {capabilities.recommendations.map((rec, idx) => (
                    <div key={idx} className="flex items-start p-3 bg-yellow-50 rounded-lg">
                      <Lightbulb className="w-5 h-5 text-yellow-500 mr-2 mt-0.5" />
                      <span className="text-sm text-gray-700">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Optimization Tab */}
        {activeTab === 'optimization' && optimization && !loading && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-500 mb-2" />
                <div className="text-2xl font-bold text-green-700">
                  ${optimization.revenue_opportunity.toLocaleString()}
                </div>
                <div className="text-sm text-green-600">Revenue Opportunity</div>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-500 mb-2" />
                <div className="text-2xl font-bold text-blue-700">
                  {optimization.margin_improvement_potential}%
                </div>
                <div className="text-sm text-blue-600">Margin Improvement</div>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <Zap className="w-6 h-6 text-yellow-500 mb-2" />
                <div className="text-2xl font-bold text-yellow-700">
                  {optimization.items_to_promote.length}
                </div>
                <div className="text-sm text-yellow-600">Items to Promote</div>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <AlertCircle className="w-6 h-6 text-red-500 mb-2" />
                <div className="text-2xl font-bold text-red-700">
                  {optimization.items_to_remove.length}
                </div>
                <div className="text-sm text-red-600">Items to Review</div>
              </div>
            </div>

            {/* Quick Wins */}
            {optimization.quick_wins.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">⚡ Quick Wins</h4>
                <div className="space-y-2">
                  {optimization.quick_wins.map((win, idx) => (
                    <div key={idx} className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                      <div className="font-medium text-gray-900">{win.action}</div>
                      <div className="text-sm text-gray-600 mt-1">{win.impact}</div>
                      <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                        {win.difficulty}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Price Adjustments */}
            {optimization.price_adjustments.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">💵 Price Adjustments</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Suggested</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {optimization.price_adjustments.slice(0, 10).map((adj, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">{adj.item}</td>
                          <td className="px-4 py-3 text-sm text-gray-500">${adj.current.toFixed(2)}</td>
                          <td className="px-4 py-3 text-sm text-green-600 font-medium">${adj.suggested.toFixed(2)}</td>
                          <td className="px-4 py-3 text-sm">
                            <span className={`inline-flex items-center ${adj.change_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {adj.change_pct > 0 ? <ArrowUp className="w-3 h-3 mr-1" /> : <ArrowDown className="w-3 h-3 mr-1" />}
                              {Math.abs(adj.change_pct).toFixed(1)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* AI Insights */}
            {optimization.ai_insights.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">🧠 AI Insights</h4>
                <div className="space-y-2">
                  {optimization.ai_insights.map((insight, idx) => (
                    <div key={idx} className="p-3 bg-indigo-50 rounded-lg text-sm text-indigo-800">
                      {insight}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && !loading && (
          <div className="space-y-6">
            {/* Key Insights */}
            {analytics.key_insights.length > 0 && (
              <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">🔍 Key Insights</h4>
                <div className="space-y-2">
                  {analytics.key_insights.map((insight, idx) => (
                    <div key={idx} className="text-sm text-gray-700">{insight}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Daily Patterns */}
            {analytics.daily_patterns.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Calendar className="w-5 h-5 mr-2 text-blue-500" />
                  Daily Patterns
                </h4>
                <div className="grid grid-cols-7 gap-2">
                  {analytics.daily_patterns.map((day) => (
                    <div 
                      key={day.day_of_week}
                      className={`p-3 rounded-lg text-center ${
                        day.is_peak_day ? 'bg-green-100 border-2 border-green-300' : 'bg-gray-50'
                      }`}
                    >
                      <div className="text-xs font-medium text-gray-500">{day.day_name.slice(0, 3)}</div>
                      <div className="text-lg font-bold text-gray-900">${day.avg_revenue.toFixed(0)}</div>
                      {day.is_peak_day && <span className="text-xs text-green-600">Peak</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Hourly Patterns */}
            {analytics.hourly_patterns.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-orange-500" />
                  Hourly Demand
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analytics.hourly_patterns.map((hour) => (
                    <div 
                      key={hour.hour}
                      className={`px-3 py-2 rounded-lg text-center min-w-[60px] ${
                        hour.peak_indicator ? 'bg-orange-100 border-2 border-orange-300' : 'bg-gray-50'
                      }`}
                    >
                      <div className="text-xs text-gray-500">{hour.hour}:00</div>
                      <div className="text-sm font-medium">{hour.avg_quantity.toFixed(0)}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Demand Forecast */}
            {analytics.demand_forecast.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
                  7-Day Forecast
                </h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Period</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Predicted Revenue</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Confidence Range</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {analytics.demand_forecast.map((forecast, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-3 text-sm text-gray-900">{forecast.period}</td>
                          <td className="px-4 py-3 text-sm font-medium text-green-600">
                            ${forecast.predicted_revenue.toFixed(2)}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                            ${forecast.confidence_lower.toFixed(0)} - ${forecast.confidence_upper.toFixed(0)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {analytics.recommendations.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">💡 Recommendations</h4>
                <div className="space-y-2">
                  {analytics.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
                      {rec}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Initial state - show load button */}
        {!loading && !error && (
          (activeTab === 'capabilities' && !capabilities) ||
          (activeTab === 'optimization' && !optimization) ||
          (activeTab === 'analytics' && !analytics)
        ) && (
          <div className="text-center py-8">
            <button
              onClick={() => {
                if (activeTab === 'capabilities') loadCapabilities();
                else if (activeTab === 'optimization') loadOptimization();
                else loadAnalytics();
              }}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Run {activeTab === 'capabilities' ? 'Capability Analysis' : 
                   activeTab === 'optimization' ? 'Menu Optimization' : 'Advanced Analytics'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
