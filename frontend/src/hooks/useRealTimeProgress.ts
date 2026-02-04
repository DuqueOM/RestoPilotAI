import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export function useRealTimeProgress(sessionId: string) {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<string>('initializing');
  const [message, setMessage] = useState<string>('');
  const [isComplete, setIsComplete] = useState(false);

  const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = typeof window !== 'undefined' ? window.location.host : 'localhost:3000';
  const defaultWsUrl = `${wsProtocol}//${wsHost}/api/v1`;
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || defaultWsUrl;

  const { lastMessage } = useWebSocket(sessionId ? `${wsUrl}/ws/analysis/${sessionId}` : null);

  useEffect(() => {
    if (!lastMessage) return;

    try {
      const data = typeof lastMessage === 'string' ? JSON.parse(lastMessage) : lastMessage;

      if (data.type === 'progress_update') {
        if (typeof data.progress === 'number') {
          setProgress(data.progress);
          if (data.progress >= 100) {
            setIsComplete(true);
          }
        }
        if (data.stage) {
          setStage(data.stage);
        }
        if (data.message) {
          setMessage(data.message);
        }
      } else if (data.type === 'analysis_complete') {
        setProgress(100);
        setIsComplete(true);
        setStage('completed');
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
    }
  }, [lastMessage]);

  return { progress, stage, message, isComplete };
}
