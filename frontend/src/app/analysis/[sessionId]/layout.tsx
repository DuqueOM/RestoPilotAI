'use client';

import { api } from '@/lib/api';
import { BarChart3, Brain, ChefHat, Megaphone, MessageSquare, Sparkles, Target, TrendingUp } from 'lucide-react';
import { usePathname, useRouter } from 'next/navigation';
import { ReactNode, useEffect, useState } from 'react';

interface AnalysisLayoutProps {
  children: ReactNode;
  params: { sessionId: string };
}

const tabs = [
  { value: 'overview', label: 'Overview', href: '', icon: Sparkles },
  { value: 'menu', label: 'Menu', href: '/menu', icon: ChefHat },
  { value: 'bcg', label: 'BCG Matrix', href: '/bcg', icon: BarChart3 },
  { value: 'competitors', label: 'Competitors', href: '/competitors', icon: Target },
  { value: 'sentiment', label: 'Sentiment', href: '/sentiment', icon: MessageSquare },
  { value: 'predictions', label: 'Predictions', href: '/predictions', icon: TrendingUp },
  { value: 'campaigns', label: 'Campaigns', href: '/campaigns', icon: Megaphone },
];

export default function AnalysisLayout({ children, params }: AnalysisLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [sessionData, setSessionData] = useState<any>(null);
  
  const pathParts = pathname.split('/');
  const lastPart = pathParts[pathParts.length - 1];
  const currentTab = tabs.find(t => t.href === `/${lastPart}`)?.value || 
                     (pathname.endsWith(params.sessionId) ? 'overview' : 'overview');

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = params.sessionId === 'demo-session-001'
          ? await api.getDemoSession()
          : await api.getSession(params.sessionId);
        setSessionData(data);
      } catch (err) {
        console.error('Failed to load session:', err);
      }
    };
    fetchSession();
  }, [params.sessionId]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Matching main page style */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => router.push('/')}>
              <div className="p-2 bg-blue-500 rounded-lg">
                <ChefHat className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MenuPilot</h1>
                <p className="text-sm text-gray-500">AI-Powered Restaurant Optimization</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-500" />
                <span className="text-sm font-medium text-gray-600">Powered by Gemini 3</span>
              </div>
              <span className="text-xs bg-gray-100 text-gray-600 px-3 py-1 rounded-full">
                {params.sessionId === 'demo-session-001' ? '🎭 Demo' : `Session: ${params.sessionId.slice(0, 8)}...`}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Tabs - Matching main page style */}
        <div className="bg-white rounded-xl border border-gray-200 p-1 flex gap-1 overflow-x-auto mb-6">
          {tabs.map((tab) => {
            const isActive = currentTab === tab.value;
            const TabIcon = tab.icon;
            
            return (
              <button
                key={tab.value}
                onClick={() => router.push(`/analysis/${params.sessionId}${tab.href}`)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-500 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <TabIcon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {children}
        </div>

        {/* Marathon Agent Footer - if available */}
        {sessionData?.marathon_agent_context && (
          <div className="mt-6 bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl p-4 border border-violet-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-violet-500 rounded-lg">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-violet-900">Marathon Agent Active</p>
                <p className="text-xs text-violet-600">
                  {sessionData.marathon_agent_context.session_count} sesiones • 
                  {sessionData.marathon_agent_context.total_analyses} análisis
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            MenuPilot - Built for Gemini 3 Hackathon | Multimodal AI for Restaurant Optimization
          </p>
        </div>
      </footer>
    </div>
  );
}
