export type WebSocketMessage = {
  type: string;
  session_id: string;
  data?: any;
  thought?: {
    id: string;
    type: 'thinking' | 'observation' | 'action' | 'verification' | 'result';
    content: string;
    step?: string;
    confidence?: number;
  };
  stage?: string;
  progress?: number;
  message?: string;
  error?: string;
  timestamp?: string;
};

type MessageHandler = (message: WebSocketMessage) => void;

export class AnalysisWebSocket {
  private ws: WebSocket | null = null;
  private baseUrl: string;
  private reconnectInterval: number = 3000;
  private maxReconnectAttempts: number = 5;
  private reconnectAttempts: number = 0;
  private handlers: Set<MessageHandler> = new Set();
  private sessionId: string | null = null;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }

  connect(urlOrId: string) {
    let wsUrl: string;

    // Check if it's a full URL (ws:// or wss://)
    if (urlOrId.includes('://')) {
      wsUrl = urlOrId;
      // Extract something as ID or just use the URL as ID for tracking
      this.sessionId = urlOrId;
    } else {
      // Treat as session ID
      if (this.sessionId === urlOrId && this.ws?.readyState === WebSocket.OPEN) {
        return;
      }
      this.sessionId = urlOrId;
      wsUrl = `${this.baseUrl}/ws/analysis/${urlOrId}`;
    }
    
    console.log(`Connecting to WebSocket: ${wsUrl}`);
    
    try {
      if (this.ws) {
        this.ws.close();
      }

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket Connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.notifyHandlers(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket Disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
      };
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId) {
      this.reconnectAttempts++;
      console.log(`Reconnecting in ${this.reconnectInterval}ms... (Attempt ${this.reconnectAttempts})`);
      setTimeout(() => {
        if (this.sessionId) this.connect(this.sessionId);
      }, this.reconnectInterval);
    }
  }

  subscribe(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  private notifyHandlers(message: WebSocketMessage) {
    this.handlers.forEach(handler => handler(message));
  }

  disconnect() {
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect attempts
      this.ws.close();
      this.ws = null;
      this.sessionId = null;
      this.handlers.clear();
    }
  }

  sendMessage(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type,
        ...data
      }));
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  }
}

// Singleton instance for global access if needed
export const wsManager = new AnalysisWebSocket();
