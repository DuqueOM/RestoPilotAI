'use client';

import { api } from '@/lib/api';
import { BarChart3, Brain, CheckCircle2, ChefHat, Loader2, Megaphone, MessageSquare, Sparkles, Target } from 'lucide-react';
import { usePathname, useRouter } from 'next/navigation';
import { createContext, ReactNode, use, useCallback, useContext, useEffect, useRef, useState } from 'react';

interface AnalysisLayoutProps {
  children: ReactNode;
  params: Promise<{ sessionId: string }>;
}

// SessionContext to share data across tabs
interface SessionContextType {
  sessionData: any;
  isLoading: boolean;
  error: string | null;
  taskState: any;
  refreshSession: () => Promise<void>;
}

export const SessionContext = createContext<SessionContextType | null>(null);

// Custom hook to use the context
export const useSessionData = () => {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSessionData must be used within SessionContext.Provider');
  return ctx;
};

const tabs = [
  { value: 'overview', label: 'Overview', href: '', icon: Sparkles, dataKey: null },
  { value: 'bcg', label: 'BCG Matrix', href: '/bcg', icon: BarChart3, dataKey: 'bcg' },
  { value: 'competitors', label: 'Competitors', href: '/competitors', icon: Target, dataKey: 'competitors' },
  { value: 'sentiment', label: 'Sentiment', href: '/sentiment', icon: MessageSquare, dataKey: 'sentiment' },
  { value: 'campaigns', label: 'Campaigns', href: '/campaigns', icon: Megaphone, dataKey: 'campaigns' },
];

function getCompletionMap(data: any): Record<string, boolean> {
  if (!data) return {};
  const d = data?.data || data;
  return {
    bcg: !!(d?.bcg_analysis?.items?.length || d?.bcg?.items?.length),
    competitors: !!(d?.competitor_analysis || d?.competitors?.length || d?.enriched_competitors?.length),
    sentiment: !!d?.sentiment_analysis,
    campaigns: !!(Array.isArray(d?.campaigns) ? d.campaigns.length : d?.campaigns?.campaigns?.length),
  };
}

export default function AnalysisLayout({ children, params }: AnalysisLayoutProps) {
  const { sessionId } = use(params);
  const router = useRouter();
  const pathname = usePathname();
  const [sessionData, setSessionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskState, setTaskState] = useState<any>(null);
  const hasFetched = useRef(false);
  
  const pathParts = pathname.split('/');
  const lastPart = pathParts[pathParts.length - 1];
  const currentTab = tabs.find(t => t.href === `/${lastPart}`)?.value || 
                     (pathname.endsWith(sessionId) ? 'overview' : 'overview');

  // Centralized fetch - RUNS ONLY ONCE
  const fetchSession = useCallback(async () => {
    try {
      if (!hasFetched.current) setIsLoading(true);
      setError(null);
      const data = await api.getSession(sessionId);
      
      setSessionData(data);
      hasFetched.current = true;
      
      // Extract taskState if it exists (handle nested backend structure)
      const unwrappedData = (data as any)?.data || data;
      const activeTaskId = unwrappedData?.active_task_id || unwrappedData?.marathon_agent_context?.active_task_id;
      if (activeTaskId) {
        setTaskState(unwrappedData?.task_state || null);
      }
    } catch (err) {
      console.error('Failed to load session:', err);
      setError(err instanceof Error ? err.message : 'Failed to load session');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (!hasFetched.current) {
      fetchSession();
    }
  }, [fetchSession]);

  return (
    <SessionContext.Provider value={{ sessionData, isLoading, error, taskState, refreshSession: fetchSession }}>
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
                <h1 className="text-xl font-bold text-gray-900">RestoPilotAI</h1>
                <p className="text-sm text-gray-500">AI-Powered Restaurant Optimization</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-500" />
                <span className="text-sm font-medium text-gray-600">Powered by Gemini 3</span>
              </div>
              <span className="text-xs bg-gray-100 text-gray-600 px-3 py-1 rounded-full">
                {`Session: ${sessionId.slice(0, 8)}...`}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Tabs with completion badges */}
        <div className="bg-white rounded-xl border border-gray-200 p-1 flex gap-1 overflow-x-auto mb-6">
          {tabs.map((tab) => {
            const isActive = currentTab === tab.value;
            const TabIcon = tab.icon;
            const completionMap = getCompletionMap(sessionData);
            const isComplete = tab.dataKey ? completionMap[tab.dataKey] : false;
            
            return (
              <button
                key={tab.value}
                onClick={() => router.push(`/analysis/${sessionId}${tab.href}`)}
                className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-500 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <TabIcon className="h-4 w-4" />
                {tab.label}
                {tab.dataKey && isComplete && !isActive && (
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                )}
                {tab.dataKey && isComplete && isActive && (
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-200" />
                )}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              <span className="ml-3 text-gray-600">Loading session data...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="text-red-500 text-lg mb-2">⚠️ Error</div>
              <p className="text-gray-600">{error}</p>
              <button
                onClick={fetchSession}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Retry
              </button>
            </div>
          ) : (
            children
          )}
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
                  {sessionData.marathon_agent_context.session_count} sessions • 
                  {sessionData.marathon_agent_context.total_analyses} analyses
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer — Gemini 3 Tech Stack Showcase */}
      <footer className="bg-gradient-to-r from-slate-900 to-blue-950 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-white text-sm font-semibold">
              <Sparkles className="h-4 w-4 text-amber-400" />
              RestoPilotAI
              <span className="text-blue-300/60 font-normal">· Gemini 3 Hackathon</span>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-2">
              {[
                { label: 'Gemini 3 Pro', color: 'bg-blue-500/20 text-blue-200 border-blue-400/30' },
                { label: 'Imagen 3', color: 'bg-purple-500/20 text-purple-200 border-purple-400/30' },
                { label: 'Vision', color: 'bg-cyan-500/20 text-cyan-200 border-cyan-400/30' },
                { label: 'Video', color: 'bg-pink-500/20 text-pink-200 border-pink-400/30' },
                { label: 'Audio', color: 'bg-emerald-500/20 text-emerald-200 border-emerald-400/30' },
                { label: 'Search Grounding', color: 'bg-amber-500/20 text-amber-200 border-amber-400/30' },
              ].map((tech) => (
                <span key={tech.label} className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${tech.color}`}>
                  {tech.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </footer>
      </div>
    </SessionContext.Provider>
  );
}
