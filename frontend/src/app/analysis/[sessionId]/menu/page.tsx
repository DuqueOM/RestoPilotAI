'use client';

import { api, MenuItem } from '@/lib/api';
import { use, useEffect, useState } from 'react';


interface MenuPageProps {
  params: Promise<{ sessionId: string }>;
}

export default function MenuPage({ params }: MenuPageProps) {
  const { sessionId } = use(params);
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = (sessionId === 'demo-session-001' || sessionId === 'margarita-pinta-demo-001')
          ? await api.getDemoSession()
          : await api.getSession(sessionId);
        setSession(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load session');
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
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

  const items = session?.menu?.items || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Extracted Menu Items</h2>
        <span className="text-sm text-gray-500">
          {items.length} items found
        </span>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-4xl mb-4">📋</p>
          <p>No menu items extracted yet.</p>
          <p className="text-sm mt-2">Upload a menu image to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Item</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Category</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Price</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Description</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">Source</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: MenuItem & { source?: string; has_sales_data?: boolean }, index: number) => (
                <tr key={index} className="border-b hover:bg-gray-50 transition">
                  <td className="py-3 px-4 font-medium">{item.name}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                      {item.category || 'Uncategorized'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono">
                    ${item.price?.toFixed(2) || '0.00'}
                  </td>
                  <td className="py-3 px-4 text-gray-600 text-sm max-w-xs truncate">
                    {item.description || '-'}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded text-xs ${
                      item.source === 'sales_data' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-purple-100 text-purple-700'
                    }`}>
                      {item.source === 'sales_data' ? '📊 CSV' : '📷 Menu'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Categories Summary */}
      {session?.menu?.categories && session.menu.categories.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Categories</h3>
          <div className="flex flex-wrap gap-2">
            {session.menu.categories.map((category: string, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
              >
                {category}
              </span>
            ))}
          </div>
        </div>
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
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-12 bg-gray-100 rounded"></div>
        ))}
      </div>
    </div>
  );
}
