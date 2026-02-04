import { useWebSocket } from '@/hooks/useWebSocket';
import { cn } from '@/lib/utils';
import { Wifi, WifiOff } from 'lucide-react';

export function WebSocketIndicator({ sessionId, className }: { sessionId: string | null, className?: string }) {
  // Use relative path for WS to leverage proxy if possible, or fallback to direct localhost
  // Note: Client-side only
  const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = typeof window !== 'undefined' ? window.location.host : 'localhost:3000';
  const defaultWsUrl = `${wsProtocol}//${wsHost}/api/v1`;
  
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || defaultWsUrl;
  const { isConnected } = useWebSocket(sessionId ? `${wsUrl}/ws/analysis/${sessionId}` : null);

  return (
    <div className={cn("flex items-center space-x-2 text-xs font-medium", className)}>
      {isConnected ? (
        <>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          <span className="text-green-600 dark:text-green-400 flex items-center">
            <Wifi className="w-3 h-3 mr-1" />
            Live
          </span>
        </>
      ) : (
        <>
          <span className="h-2 w-2 rounded-full bg-gray-300 dark:bg-gray-600"></span>
          <span className="text-gray-500 dark:text-gray-400 flex items-center">
            <WifiOff className="w-3 h-3 mr-1" />
            Offline
          </span>
        </>
      )}
    </div>
  );
}
