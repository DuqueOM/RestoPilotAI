'use client';

import { useRouter, usePathname } from 'next/navigation';
import { ReactNode } from 'react';

interface AnalysisLayoutProps {
  children: ReactNode;
  params: { sessionId: string };
}

const tabs = [
  { value: 'menu', label: '📋 Menu', href: '' },
  { value: 'bcg', label: '📊 BCG Matrix', href: '/bcg' },
  { value: 'predictions', label: '📈 Predictions', href: '/predictions' },
  { value: 'campaigns', label: '📢 Campaigns', href: '/campaigns' },
];

export default function AnalysisLayout({ children, params }: AnalysisLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  
  const currentTab = pathname.split('/').pop() || 'menu';
  const isMenuTab = pathname.endsWith(params.sessionId) || pathname.endsWith('/menu');

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 
              className="text-2xl font-bold cursor-pointer hover:text-blue-600 transition"
              onClick={() => router.push('/')}
            >
              🍽️ MenuPilot
            </h1>
            <span className="text-sm text-gray-500">
              Session: {params.sessionId.slice(0, 8)}...
            </span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="flex border-b">
            {tabs.map((tab) => {
              const isActive = tab.value === 'menu' 
                ? isMenuTab 
                : currentTab === tab.value;
              
              return (
                <button
                  key={tab.value}
                  onClick={() => router.push(`/analysis/${params.sessionId}${tab.href}`)}
                  className={`px-6 py-4 text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
