import { WebSocketMessage, wsManager } from '@/lib/api/websocket';
import { useCallback, useEffect, useRef, useState } from 'react';

export function useWebSocket(sessionId: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  // Use a ref to track if we've already subscribed to avoid double subscriptions in strict mode
  const isSubscribed = useRef(false);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to WebSocket
    wsManager.connect(sessionId);
    setIsConnected(true); // Optimistic, ideally wsManager exposes connection state

    // Subscribe to messages
    const unsubscribe = wsManager.subscribe((message) => {
      setLastMessage(message);
    });
    isSubscribed.current = true;

    return () => {
      unsubscribe();
      isSubscribed.current = false;
      // We don't necessarily disconnect on unmount if we want to keep the connection alive 
      // for other components, but for this hook it might be cleaner to let the manager handle it.
      // wsManager.disconnect(); // Only disconnect if we are sure no one else is using it
    };
  }, [sessionId]);

  const sendMessage = useCallback((type: string, data: any) => {
    wsManager.sendMessage(type, data);
  }, []);

  return {
    isConnected,
    lastMessage,
    sendMessage
  };
}
