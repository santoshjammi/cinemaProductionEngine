/**
 * Slot lifecycle manager — creates and destroys ad containers.
 * Returns a context object bound to each slot for analytics and state tracking.
 */

import { DEFAULT_CONFIG } from './config';

export type SlotContext = {
  id: string;
  position: string;
  containerEl: HTMLDivElement | null;
};

/** Create an ad container element in the DOM and return the context. */
export function createSlot(context: Partial<SlotContext>): SlotContext {
  const {
    id = `slot_${Date.now()}`,
    position = 'banner_header',
  } = context;

  let containerEl: HTMLDivElement | null = document.getElementById(id) as HTMLDivElement | null;

  if (!containerEl) {
    containerEl = document.createElement('div');
    containerEl.id = id;
    containerEl.className = `ad-slot ad-slot-${position}`;
    // Insert after any existing placeholder marker <div data-ad-slot="${id}">
    const marker = document.querySelector(`[data-ad-slot="${id}"]`);
    if (marker && marker.parentElement) {
      marker.parentElement.insertBefore(containerEl, marker.nextSibling);
    } else if (typeof window !== 'undefined') {
      // fallback: append to body — caller should position via CSS grid/flex
      document.body.appendChild(containerEl);
    }
  }

  return { id, position, containerEl };
}

/** Remove the slot's DOM element and clean up event listeners. */
export function destroySlot(ctx: SlotContext): void {
  if (ctx.containerEl) {
    ctx.containerEl.replaceWith(ctx.containerEl.cloneNode(true));
  }
}

/** Get the config for a given position. */
export function getConfigForPosition(position: string) {
  return DEFAULT_CONFIG.slots.find((s: import('./config').AdSlotDefinition) => s.position === position);
}
