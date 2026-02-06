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
  const reconnectAttemptsRef = useRef<number>(0);
  const intentionalCloseRef = useRef<boolean>(false);

  useEffect(() => {
    if (!url) {
      if (wsRef.current) {
        intentionalCloseRef.current = true;
        wsRef.current.close();
        wsRef.current = null;
      }
      setIsConnected(false);
      setError(null);
      return;
    }

    intentionalCloseRef.current = false;
    reconnectAttemptsRef.current = 0;

    const connect = () => {
      // Stop reconnecting after 5 failed attempts
      if (reconnectAttemptsRef.current >= 5) {
        console.warn('WebSocket: Max reconnection attempts reached');
        return;
      }

      try {
        const ws = new WebSocket(url);

        ws.onopen = () => {
          console.log('WebSocket connected:', url);
          setIsConnected(true);
          setError(null);
          reconnectAttemptsRef.current = 0;
        };

        ws.onmessage = (event) => {
          setLastMessage(event.data);
        };

        ws.onerror = (_event) => {
          // Only log error if we haven't seen multiple failures
          if (reconnectAttemptsRef.current < 2) {
            console.warn('WebSocket connection error for:', url);
          }
          setError(new Error('WebSocket connection error'));
        };

        ws.onclose = (event) => {
          setIsConnected(false);

          // Don't reconnect if this was an intentional close
          if (intentionalCloseRef.current) {
            return;
          }

          // Only log and reconnect if not a normal closure
          if (event.code !== 1000) {
            reconnectAttemptsRef.current += 1;
            
            if (reconnectAttemptsRef.current < 5) {
              const delay = Math.min(3000 * reconnectAttemptsRef.current, 10000);
              reconnectTimeoutRef.current = setTimeout(() => {
                console.log(`WebSocket reconnecting (attempt ${reconnectAttemptsRef.current})...`);
                connect();
              }, delay);
            }
          }
        };

        wsRef.current = ws;
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to connect'));
        reconnectAttemptsRef.current += 1;
      }
    };

    connect();

    return () => {
      intentionalCloseRef.current = true;
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
