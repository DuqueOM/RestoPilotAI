import { useEffect, useRef, useState } from 'react';

interface UseWebSocketResult {
  lastMessage: string | null;
  isConnected: boolean;
  error: Error | null;
  send: (message: string) => void;
}

export function useWebSocket(url: string | null): UseWebSocketResult {
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!url) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    const connect = () => {
      try {
        const ws = new WebSocket(url);

        ws.onopen = () => {
          console.log('WebSocket connected:', url);
          setIsConnected(true);
          setError(null);
        };

        ws.onmessage = (event) => {
          setLastMessage(event.data);
        };

        ws.onerror = (event) => {
          console.error('WebSocket error:', event);
          setError(new Error('WebSocket connection error'));
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);

          // Attempt to reconnect after 3 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 3000);
        };

        wsRef.current = ws;
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to connect'));
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [url]);

  const send = (message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    } else {
      console.warn('WebSocket not connected, message not sent');
    }
  };

  return {
    lastMessage,
    isConnected,
    error,
    send,
  };
}
