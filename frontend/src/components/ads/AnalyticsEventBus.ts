export type AdEventType = 'impression' | 'click' | 'skip' | 'complete' | 'error';

export interface AdEvent {
  eventType: AdEventType;
  slotId: string;
  timestamp: number;
  sessionId: string;
  duration?: number;
  metadata?: Record<string, unknown>;
}

type EventCallback = (event: AdEvent) => void;

class AnalyticsEventBus {
  private subscribers = new Map<string, Set<EventCallback>>();
  private sessionId = crypto.randomUUID();
  private static _instance: AnalyticsEventBus | null = null;

  static instance(): AnalyticsEventBus {
    if (!AnalyticsEventBus._instance) {
      AnalyticsEventBus._instance = new AnalyticsEventBus();
    }
    return AnalyticsEventBus._instance;
  }

  publish(event: AdEvent): void {
    const callbacks = this.subscribers.get(event.slotId);
    if (callbacks) {
      for (const cb of callbacks) {
        try {
          cb(event);
        } catch {/* fail closed */}
      }
    }
    // Broadcast to wildcard subscribers
    const wildCards = this.subscribers.get('*');
    if (wildCards) {
      for (const cb of wildCards) {
        try {
          cb(event);
        } catch {/* fail closed */}
      }
    }
  }

  subscribe(slotId: string, callback: EventCallback): () => void {
    const slotSubs = this.subscribers.get(slotId);
    if (slotSubs) {
      slotSubs.add(callback);
    } else {
      this.subscribers.set(slotId, new Set([callback]));
    }
    return () => {
      const exists = this.subscribers.get(slotId);
      if (exists) {
        exists.delete(callback);
        if (exists.size === 0) this.subscribers.delete(slotId);
      }
    };
  }

  subscribeAll(callback: EventCallback): () => void {
    return this.subscribe('*', callback);
  }

  getSessionId(): string {
    return this.sessionId;
  }
}

export const analyticsEventBus = AnalyticsEventBus.instance();
