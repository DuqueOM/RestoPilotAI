import { useState, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';

export function useRealTimeProgress(sessionId: string) {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<string>('initializing');
  const [message, setMessage] = useState<string>('');
  const [isComplete, setIsComplete] = useState(false);

  const { lastMessage } = useWebSocket(sessionId);

  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.type === 'progress_update') {
      if (typeof lastMessage.progress === 'number') {
        setProgress(lastMessage.progress);
        if (lastMessage.progress >= 100) {
          setIsComplete(true);
        }
      }
      if (lastMessage.stage) {
        setStage(lastMessage.stage);
      }
      if (lastMessage.message) {
        setMessage(lastMessage.message);
      }
    } else if (lastMessage.type === 'analysis_complete') {
      setProgress(100);
      setIsComplete(true);
      setStage('completed');
    }
  }, [lastMessage]);

  return { progress, stage, message, isComplete };
}
