'use client';

import { AgentDebateTrigger } from '@/components/ai/AgentDebateTrigger';
import { ConfidenceIndicator } from '@/components/ai/ConfidenceIndicator';
import { MenuItemsTable } from '@/components/analysis/MenuItemsTable';
import { GroundingSources } from '@/components/common/GroundingSources';
import { MenuTransformationIntegrated } from '@/components/creative/MenuTransformationIntegrated';
import { CollapsibleSection } from '@/components/ui/CollapsibleSection';
import { BCGAnalysisResult, MenuEngineeringItem } from '@/lib/api';
import { AlertTriangle, BarChart3, RefreshCw, TrendingUp } from 'lucide-react';
import { use, useCallback, useEffect, useState } from 'react';
import { useSessionData } from '../layout';

interface BCGPageProps {
  params: Promise<{ sessionId: string }>;
}

const ALL_PERIODS = [
  { value: '30d', label: '30 days' },
  { value: '90d', label: '3 months' },
  { value: '180d', label: '6 months' },
  { value: '365d', label: '1 year' },
  { value: 'all', label: 'All Time' },
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

const CATEGORY_CONFIG: Record<string, { bg: string; text: string; border: string; icon: string; label: string; desc: string }> = {
  star: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-400', icon: '⭐', label: 'Stars', desc: 'High popularity + High margin. Protect and promote.' },
  plowhorse: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-400', icon: '🐴', label: 'Plowhorses', desc: 'High popularity + Low margin. Improve profitability.' },
  puzzle: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-400', icon: '🧩', label: 'Puzzles', desc: 'Low popularity + High margin. Promote more.' },
  dog: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-400', icon: '🐕', label: 'Dogs', desc: 'Low popularity + Low margin. Consider removal.' },
};

export default function BCGPage({ params }: BCGPageProps) {
  const { sessionId } = use(params);
  const { sessionData, isLoading: sessionLoading } = useSessionData();
  const [data, setData] = useState<BCGAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingPeriod, setLoadingPeriod] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [expandedItem, setExpandedItem] = useState<string | null>(null);
  const [showMenuList, setShowMenuList] = useState(false);
  const [showMenuTransform, setShowMenuTransform] = useState(false);

  const fetchAnalysis = useCallback(async (period: string) => {
    try {
      // Use data from SessionContext
      const unwrappedData = (sessionData as any)?.data || sessionData;
      if (unwrappedData?.bcg_analysis) {
        setData(unwrappedData.bcg_analysis);
      } else if (unwrappedData?.bcg) {
        setData(unwrappedData.bcg);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analysis');
    }
  }, [sessionData]);

  useEffect(() => {
    if (!sessionLoading && sessionData) {
      fetchAnalysis(selectedPeriod).finally(() => setLoading(false));
    }
  }, [fetchAnalysis, selectedPeriod, sessionLoading, sessionData]);

  const handlePeriodChange = async (period: string) => {
    setSelectedPeriod(period);
    setLoadingPeriod(true);
    setError(null);
    
    try {
      // Call backend API to recalculate BCG with new period
      const API_URL = '';
      const response = await fetch(
        `${API_URL}/api/v1/analyze/bcg?session_id=${sessionId}&period=${period}`,
        { method: 'POST' }
      );
      
      if (!response.ok) throw new Error('Failed to recalculate BCG analysis');
      
      const result = await response.json();
      setData(result);
      
      // Refresh session data
      await fetchAnalysis(period);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update analysis');
    } finally {
      setLoadingPeriod(false);
    }
  };

  if (loading) return <LoadingSkeleton />;

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-600 font-medium">{error}</p>
        <button onClick={() => fetchAnalysis(selectedPeriod)} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.items?.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p className="text-lg">No analysis available</p>
        <p className="text-sm mt-2">Run the analysis to classify your products.</p>
      </div>
    );
  }

  const groupedItems = data.items.reduce((acc, item) => {
    const cat = item.category || 'unknown';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, MenuEngineeringItem[]>);

  // Calculate available periods once
  const availablePeriods = getAvailablePeriods(sessionData);
  
  // Extract menu items from sessionData
  const unwrappedData = (sessionData as any)?.data || sessionData;
  const menuItems = unwrappedData?.menu?.items || [];

  return (
    <div className="space-y-6">
      {/* Section 1: Menu List */}
      <CollapsibleSection
        title="📋 Full Menu List"
        count={menuItems.length}
        isOpen={showMenuList}
        onToggle={() => setShowMenuList(!showMenuList)}
      >
        <MenuItemsTable items={menuItems} />
      </CollapsibleSection>
      
      {/* Section 2: Menu Transformation */}
      <CollapsibleSection
        title="🎨 Menu Style Transformation"
        isOpen={showMenuTransform}
        onToggle={() => setShowMenuTransform(!showMenuTransform)}
      >
        <MenuTransformationIntegrated sessionId={sessionId} />
      </CollapsibleSection>
      {/* Header with Period Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <BarChart3 className="w-6 h-6" />
            Menu Engineering
          </h2>
          <div className="flex items-center gap-3">
            <p className="text-sm text-gray-500">
              {data.methodology} • {data.items_analyzed} items analyzed
            </p>
            {(data as any).confidence && (
              <ConfidenceIndicator value={(data as any).confidence} variant="badge" size="sm" />
            )}
          </div>
        </div>
        
        {availablePeriods.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Period:</span>
            <div className="flex bg-gray-100 rounded-lg p-1">
              {availablePeriods.map((p) => (
                <button
                  key={p.value}
                  onClick={() => handlePeriodChange(p.value)}
                  disabled={loadingPeriod}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    selectedPeriod === p.value
                      ? 'bg-white text-blue-600 shadow-sm font-medium'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
            {loadingPeriod && <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />}
          </div>
        )}
      </div>

      {/* Grounding Sources */}
      {data.grounding_sources && data.grounding_sources.length > 0 && (
        <GroundingSources 
          sources={data.grounding_sources}
          isGrounded={data.grounded || false}
        />
      )}

      {/* Date Range Info */}
      {data.date_range?.start && (
        <div className="text-sm text-gray-500 bg-gray-50 px-4 py-2 rounded-lg">
          Data from {new Date(data.date_range.start).toLocaleDateString('en-US')} to {new Date(data.date_range.end || '').toLocaleDateString('en-US')}
          {' • '}{data.total_records} sales records
        </div>
      )}

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Total Revenue" value={`$${data.summary?.total_revenue?.toLocaleString() || 0}`} icon={<TrendingUp className="w-5 h-5" />} color="blue" />
        <KPICard label="Total Contribution" value={`$${data.summary?.total_contribution?.toLocaleString() || 0}`} icon={<BarChart3 className="w-5 h-5" />} color="green" />
        <KPICard label="Units Sold" value={data.summary?.total_units?.toLocaleString() || '0'} icon={<span className="text-lg">📦</span>} color="purple" />
        <KPICard label="Avg CM" value={`$${data.summary?.avg_cm?.toFixed(2) || 0}`} icon={<span className="text-lg">💰</span>} color="amber" />
      </div>

      {/* Menu Engineering Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {['star', 'plowhorse', 'puzzle', 'dog'].map((cat) => {
          const config = CATEGORY_CONFIG[cat];
          const items = groupedItems[cat] || [];
          const catSummary = data.summary?.categories?.find(c => c.category === cat);
          return (
            <QuadrantCard
              key={cat}
              category={cat}
              config={config}
              items={items}
              summary={catSummary}
              expandedItem={expandedItem}
              onToggleItem={setExpandedItem}
            />
          );
        })}
      </div>

      {/* AI Agent Debate Section */}
      <AgentDebateTrigger
        sessionId={sessionId}
        topic={`Menu Engineering Strategy for ${data.items_analyzed} items across ${Object.keys(groupedItems).length} categories`}
        context={`Stars: ${(groupedItems['star'] || []).length} items, Dogs: ${(groupedItems['dog'] || []).length} items, Puzzles: ${(groupedItems['puzzle'] || []).length} items, Plowhorses: ${(groupedItems['plowhorse'] || []).length} items`}
        variant="card"
      />

      {/* Category Distribution Chart */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="font-semibold mb-4">Category Distribution</h3>
        <div className="space-y-3">
          {data.summary?.categories?.map((cat) => {
            const config = CATEGORY_CONFIG[cat.category] || { bg: 'bg-gray-100', text: 'text-gray-800', icon: '📊', label: cat.category };
            return (
              <div key={cat.category} className="flex items-center gap-3">
                <span className="text-xl w-8">{config.icon}</span>
                <span className="w-32 text-sm font-medium">{config.label}</span>
                <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${config.bg} ${config.text} flex items-center justify-end pr-2 text-xs font-medium`}
                    style={{ width: `${Math.max(cat.pct_contribution, 5)}%` }}
                  >
                    {cat.pct_contribution.toFixed(1)}%
                  </div>
                </div>
                <span className="w-24 text-right text-sm text-gray-600">${cat.total_contribution.toLocaleString()}</span>
              </div>
            );
          })}
        </div>
        <p className="text-xs text-gray-500 mt-4">Total contribution percentage by category</p>
      </div>

      {/* Attention Needed */}
      {data.summary?.attention_needed > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800 font-medium mb-2">
            <AlertTriangle className="w-5 h-5" />
            {data.summary.attention_needed} products require attention
          </div>
          <p className="text-sm text-red-700">
            The following products have low popularity and low margin: {data.summary.dogs_list?.join(', ')}
          </p>
        </div>
      )}

      {/* Top Performers */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <h4 className="font-semibold mb-3 flex items-center gap-2">🏆 Top by Contribution</h4>
          <ul className="space-y-2">
            {data.summary?.top_by_contribution?.map((item, i) => (
              <li key={i} className="flex justify-between text-sm">
                <span>{i + 1}. {item.name}</span>
                <span className="font-mono text-green-600">${item.contribution.toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <h4 className="font-semibold mb-3 flex items-center gap-2">🔥 Top by Popularity</h4>
          <ul className="space-y-2">
            {data.summary?.top_by_popularity?.map((item, i) => (
              <li key={i} className="flex justify-between text-sm">
                <span>{i + 1}. {item.name}</span>
                <span className="font-mono text-blue-600">{item.popularity_pct.toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Thresholds Info */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm">
        <h4 className="font-medium mb-2">Classification Thresholds</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-gray-600">
          <div>
            <span className="block text-xs text-gray-500">Popularity Threshold</span>
            <span className="font-mono">{data.thresholds?.popularity_threshold?.toFixed(2)}%</span>
          </div>
          <div>
            <span className="block text-xs text-gray-500">CM Threshold</span>
            <span className="font-mono">${data.thresholds?.cm_threshold?.toFixed(2)}</span>
          </div>
          <div>
            <span className="block text-xs text-gray-500">Expected Popularity</span>
            <span className="font-mono">{data.thresholds?.expected_popularity?.toFixed(2)}%</span>
          </div>
          <div>
            <span className="block text-xs text-gray-500">Total Items</span>
            <span className="font-mono">{data.thresholds?.n_items}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function KPICard({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    purple: 'bg-purple-50 text-purple-700',
    amber: 'bg-amber-50 text-amber-700',
  };
  return (
    <div className={`rounded-lg p-4 ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-1">{icon}<span className="text-xs font-medium opacity-80">{label}</span></div>
      <div className="text-xl font-bold">{value}</div>
    </div>
  );
}

interface QuadrantCardProps {
  category: string;
  config: { bg: string; text: string; border: string; icon: string; label: string; desc: string };
  items: MenuEngineeringItem[];
  summary?: { count: number; pct_items: number; total_contribution: number; pct_contribution: number };
  expandedItem: string | null;
  onToggleItem: (name: string | null) => void;
}

function QuadrantCard({ category, config, items, summary, expandedItem, onToggleItem }: QuadrantCardProps) {
  return (
    <div className={`rounded-lg border-2 ${config.border} ${config.bg} p-4`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <h4 className={`font-bold ${config.text}`}>{config.label}</h4>
            <p className="text-xs text-gray-600">{config.desc}</p>
          </div>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${config.text}`}>{items.length}</span>
          <p className="text-xs text-gray-500">{summary?.pct_contribution?.toFixed(1) || 0}% contrib.</p>
        </div>
      </div>

      {items.length > 0 ? (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {items.map((item) => (
            <div key={item.name} className="bg-white/70 rounded-lg p-2">
              <div
                className="flex justify-between items-center cursor-pointer"
                onClick={() => onToggleItem(expandedItem === item.name ? null : item.name)}
              >
                <span className="font-medium text-sm truncate flex-1">{item.name}</span>
                <div className="flex gap-3 text-xs">
                  <span className="text-gray-600">Pop: {item.popularity_pct?.toFixed(1)}%</span>
                  <span className="text-green-700">CM: ${item.cm_unitario?.toFixed(2)}</span>
                </div>
              </div>
              {expandedItem === item.name && (
                <div className="mt-2 pt-2 border-t text-xs space-y-1">
                  <div className="grid grid-cols-2 gap-2">
                    <span>Units: {item.units_sold}</span>
                    <span>Price: ${item.price?.toFixed(2)}</span>
                    <span>Cost: ${item.cost?.toFixed(2)}</span>
                    <span>Margin: {item.margin_pct?.toFixed(1)}%</span>
                  </div>
                  {(item as any).confidence && (
                    <ConfidenceIndicator value={(item as any).confidence} variant="bar" size="xs" showLabel />
                  )}
                  <div className="mt-2 p-2 bg-white rounded space-y-2">
                    <div>
                      <span className="font-medium text-gray-700 block mb-1">{item.strategy?.action}</span>
                      <div className="flex gap-2 text-[10px] mb-2">
                        {item.strategy?.priority && (
                          <span className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600 border border-gray-200">
                            Priority: {item.strategy.priority}
                          </span>
                        )}
                        {item.strategy?.pricing && (
                          <span className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600 border border-gray-200">
                            Price: {item.strategy.pricing}
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-gray-500 mb-1">
                        Position: {item.strategy?.menu_position || 'Standard'}
                      </div>
                    </div>
                    <ul className="mt-1 text-gray-600 list-disc list-inside">
                      {item.strategy?.recommendations?.slice(0, 3).map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500 text-center py-4">No products in this category</p>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="flex justify-between">
        <div className="h-8 bg-gray-200 rounded w-48"></div>
        <div className="h-8 bg-gray-200 rounded w-64"></div>
      </div>
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => <div key={i} className="h-24 bg-gray-100 rounded-lg"></div>)}
      </div>
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => <div key={i} className="h-64 bg-gray-100 rounded-lg"></div>)}
      </div>
    </div>
  );
}
