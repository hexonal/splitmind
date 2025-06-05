import { useEffect, useCallback } from 'react';
import { websocket } from '@/services/websocket';
import { WebSocketMessage } from '@/types';

export function useWebSocket(handler: (message: WebSocketMessage) => void) {
  useEffect(() => {
    // Connect when component mounts
    websocket.connect();

    // Subscribe to messages
    const unsubscribe = websocket.subscribe(handler);

    // Cleanup on unmount
    return () => {
      unsubscribe();
    };
  }, [handler]);

  const send = useCallback((message: any) => {
    websocket.send(message);
  }, []);

  return { send };
}