import type { AdConfig, AdSlotDefinition } from './config';
import { DEFAULT_CONFIG } from './config';
import { analyticsEventBus } from './AnalyticsEventBus';
import { loadAdConfig } from './defaults';

interface ActiveSlot {
  definition: AdSlotDefinition;
  container?: HTMLDivElement | null;
  isActive: boolean;
}

export class AdManager {
  private static instanceRef: AdManager | null = null;
  private config: AdConfig = DEFAULT_CONFIG;
  private activeSlots: Map<string, ActiveSlot> = new Map();
  private frequencyMap: Map<string, number[]> = new Map();
  private initialized = false;

  static instance(): AdManager {
    if (!AdManager.instanceRef) {
      AdManager.instanceRef = new AdManager();
    }
    return AdManager.instanceRef;
  }

  async init(): Promise<void> {
    if (this.initialized) return;
    try {
      this.config = await loadAdConfig();
    } catch {
      this.config = DEFAULT_CONFIG;
    }
    this.initialized = true;
  }

  getConfig(): AdConfig {
    return this.config;
  }

  getSlots(position: string): AdSlotDefinition[] {
    return this.config.slots.filter((s) => s.position === position);
  }

  activateAll(): void {
    if (!this.initialized) this.init().catch(() => {});
    for (const slot of this.config.slots) {
      try {
        this.activateSlot(slot);
      } catch {/* fail closed */}
    }
  }

  deactivateAll(): void {
    for (const [id, active] of this.activeSlots.entries()) {
      try {
        active.isActive = false;
        if (active.container && active.container.parentNode) {
          active.container.parentNode.removeChild(active.container);
        }
        this.onSlotEvent({ eventType: 'skip', slotId: id, timestamp: Date.now(), sessionId: analyticsEventBus.getSessionId() });
      } catch {/* fail closed */}
    }
    this.activeSlots.clear();
  }

  isActive(slotId: string): boolean {
    return this.activeSlots.get(slotId)?.isActive ?? false;
  }

  findContainer(slotId: string): HTMLDivElement | null {
    if (typeof document === 'undefined') return null;
    return document.querySelector(`[data-ad-slot="${slotId}"]`) as HTMLDivElement | null;
  }

  trackFrequency(slotId: string, currentTime?: number): boolean {
    const windowMinutes = this.config.frequencyCapWindowMinutes ?? 60;
    const now = currentTime ?? Date.now();
    const key = `${slotId}_${Math.floor(now / (windowMinutes * 60 * 1000))}`;

    let timestamps = this.frequencyMap.get(key);
    if (!timestamps) {
      timestamps = [];
      this.frequencyMap.set(key, timestamps);
    }

    timestamps.push(now);

    // Cleanup old entries
    const keep = timestamps.filter((t) => now - t < windowMinutes * 60 * 1000);
    if (keep.length !== timestamps.length) {
      this.frequencyMap.set(key, keep);
    }

    return keep.length === 0;
  }

  private activateSlot(slot: AdSlotDefinition): void {
    if (!this.config.enabled) return;

    const existing = this.activeSlots.get(slot.id);

    // Frequency cap for slots with maxFrequency
    if (slot.maxFrequency && existing?.isActive) {
      const timestamps = this.frequencyMap.get(`${slot.id}_freq`);
      if (timestamps && timestamps.length >= slot.maxFrequency) return;
    }

    try {
      this.onSlotEvent({ eventType: 'impression', slotId: slot.id, timestamp: Date.now(), sessionId: analyticsEventBus.getSessionId() });
    } catch {/* fail closed */}

    this.activeSlots.set(slot.id, { definition: slot, isActive: true });

    // Track frequency for slots with explicit cap
    if (slot.maxFrequency) {
      const key = `${slot.id}_freq`;
      let timestamps = this.frequencyMap.get(key);
      if (!timestamps) {
        timestamps = [];
        this.frequencyMap.set(key, timestamps);
      }
      timestamps.push(Date.now());
    }
  }

  private onSlotEvent(event: Parameters<typeof analyticsEventBus['publish']>[0]): void {
    try {
      analyticsEventBus.publish({ ...event });
    } catch {/* fail closed */}
  }

  requestSlot(slotId: string): AdSlotDefinition | null {
    const slot = this.activeSlots.get(slotId);
    if (!slot?.isActive) return null;
    return slot.definition;
  }
}
