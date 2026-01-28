'use client';

import { api, BCGAnalysisResult, BCGItem } from '@/lib/api';
import { use, useEffect, useState } from 'react';


interface BCGPageProps {
  params: Promise<{ sessionId: string }>;
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  STAR: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-400' },
  CASH_COW: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-400' },
  QUESTION_MARK: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-400' },
  DOG: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-400' },
};

const CATEGORY_ICONS: Record<string, string> = {
  STAR: '⭐',
  CASH_COW: '🐄',
  QUESTION_MARK: '❓',
  DOG: '🐕',
};

const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  STAR: 'High growth, high market share. Invest to maintain leadership.',
  CASH_COW: 'Low growth, high market share. Maximize profits, minimal investment.',
  QUESTION_MARK: 'High growth, low market share. Decide: invest heavily or divest.',
  DOG: 'Low growth, low market share. Consider discontinuing or repositioning.',
};

export default function BCGPage({ params }: BCGPageProps) {
  const { sessionId } = use(params);
  const [data, setData] = useState<BCGAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBCG = async () => {
      try {
        // Check if this is a demo session
        const session = sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(sessionId);
        if (session.bcg) {
          setData(session.bcg);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load BCG analysis');
      } finally {
        setLoading(false);
      }
    };

    fetchBCG();
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

  if (!data || !data.items?.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-4xl mb-4">📊</p>
        <p>No BCG analysis available yet.</p>
        <p className="text-sm mt-2">Run analysis to classify your menu items.</p>
      </div>
    );
  }

  const groupedItems = data.items.reduce((acc, item) => {
    const category = item.category || 'UNKNOWN';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {} as Record<string, BCGItem[]>);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">BCG Matrix Analysis</h2>
        <span className="text-sm text-gray-500">
          {data.items.length} items classified
        </span>
      </div>

      {/* BCG Visual Matrix */}
      <div className="mb-8">
        <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
          {/* Stars - Top Left */}
          <QuadrantCard
            title="Stars"
            icon="⭐"
            items={groupedItems['STAR'] || []}
            color={CATEGORY_COLORS.STAR}
            position="High Growth / High Share"
          />
          
          {/* Question Marks - Top Right */}
          <QuadrantCard
            title="Question Marks"
            icon="❓"
            items={groupedItems['QUESTION_MARK'] || []}
            color={CATEGORY_COLORS.QUESTION_MARK}
            position="High Growth / Low Share"
          />
          
          {/* Cash Cows - Bottom Left */}
          <QuadrantCard
            title="Cash Cows"
            icon="🐄"
            items={groupedItems['CASH_COW'] || []}
            color={CATEGORY_COLORS.CASH_COW}
            position="Low Growth / High Share"
          />
          
          {/* Dogs - Bottom Right */}
          <QuadrantCard
            title="Dogs"
            icon="🐕"
            items={groupedItems['DOG'] || []}
            color={CATEGORY_COLORS.DOG}
            position="Low Growth / Low Share"
          />
        </div>
      </div>

      {/* Insights */}
      {data.insights && Object.keys(data.insights).length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Strategic Insights</h3>
          <div className="space-y-4">
            {Object.entries(data.insights).map(([category, insight]) => (
              <div
                key={category}
                className={`p-4 rounded-lg border ${CATEGORY_COLORS[category]?.bg || 'bg-gray-100'} ${CATEGORY_COLORS[category]?.border || 'border-gray-300'}`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span>{CATEGORY_ICONS[category] || '📌'}</span>
                  <span className="font-medium">{category.replace('_', ' ')}</span>
                </div>
                <p className="text-sm text-gray-700">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      {data.summary && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-lg font-semibold mb-2 text-blue-800">📋 Summary</h3>
          <p className="text-gray-700">{data.summary}</p>
        </div>
      )}
    </div>
  );
}

interface QuadrantCardProps {
  title: string;
  icon: string;
  items: BCGItem[];
  color: { bg: string; text: string; border: string };
  position: string;
}

function QuadrantCard({ title, icon, items, color, position }: QuadrantCardProps) {
  return (
    <div className={`p-4 rounded-lg border-2 ${color.bg} ${color.border}`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{icon}</span>
        <div>
          <h4 className={`font-bold ${color.text}`}>{title}</h4>
          <p className="text-xs text-gray-500">{position}</p>
        </div>
        <span className={`ml-auto px-2 py-1 rounded-full text-sm font-medium ${color.bg} ${color.text}`}>
          {items.length}
        </span>
      </div>
      
      {items.length > 0 ? (
        <ul className="mt-3 space-y-1">
          {items.slice(0, 5).map((item, idx) => (
            <li key={idx} className="text-sm flex justify-between">
              <span className="truncate">{item.name}</span>
              <span className="font-mono text-gray-600">${item.price?.toFixed(2)}</span>
            </li>
          ))}
          {items.length > 5 && (
            <li className="text-xs text-gray-500">+{items.length - 5} more</li>
          )}
        </ul>
      ) : (
        <p className="text-sm text-gray-500 mt-3">No items in this category</p>
      )}
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
      <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-48 bg-gray-100 rounded-lg"></div>
        ))}
      </div>
    </div>
  );
}
