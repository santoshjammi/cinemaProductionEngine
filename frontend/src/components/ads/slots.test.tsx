import { describe, it, expect, vi, beforeEach } from 'vitest';
import { loadAdConfig, DEFAULT_CONFIG } from './config';
import { createSlot, destroySlot, getConfigForPosition, SlotContext } from './slots';
import { publishEvent, subscribeAdEvents, AdAnalyticsEvent } from './AnalyticsEventBus';

// ---------- config.ts tests ----------

describe('loadAdConfig', () => {
  let mockStorage: Record<string, string>;

  beforeEach(() => {
    mockStorage = {};
    Object.defineProperty(globalThis, 'localStorage', {
      value: {
        getItem(key: string) { return mockStorage[key] ?? null; },
        setItem(key: string, val: string) { mockStorage[key] = val; },
        removeItem(key: string) { delete mockStorage[key]; },
        clear() { Object.keys(mockStorage).forEach((k) => delete mockStorage[k]); },
        get length() { return Object.keys(mockStorage).length; },
        key(n: number) { return Object.keys(mockStorage)[n] ?? null; },
      } as Storage,
      writable: true,
    });
  });

  it('returns DEFAULT_CONFIG when no localStorage key exists', () => {
    const cfg = loadAdConfig();
    expect(cfg).toEqual(DEFAULT_CONFIG);
  });

  it('parses and returns JSON from localStorage when available', () => {
    const custom: typeof DEFAULT_CONFIG = { ...DEFAULT_CONFIG, slots: [] };
    localStorage.setItem('ad_config', JSON.stringify(custom));
    const cfg = loadAdConfig();
    expect(cfg.slots).toHaveLength(0);
  });

  it('returns default config when localStorage value is invalid JSON', () => {
    localStorage.setItem('ad_config', '{ broken');
    const cfg = loadAdConfig();
    expect(cfg).toEqual(DEFAULT_CONFIG);
  });
});

describe('DEFAULT_CONFIG', () => {
  it('contains at least a preroll slot with correct id', () => {
    const preroll = DEFAULT_CONFIG.slots.find((s) => s.position === 'preroll');
    expect(preroll?.id).toBe('ad_preroll');
    expect(preroll?.enabled).toBe(true);
  });

  it('contains a sidebar banner slot', () => {
    const sidebar = DEFAULT_CONFIG.slots.find((s) => s.position === 'banner_sidebar');
    expect(sidebar?.position).toBe('banner_sidebar');
    expect(sidebar?.width).toBe(300);
    expect(sidebar?.height).toBe(250);
  });

  it('disables midroll by default', () => {
    const mid = DEFAULT_CONFIG.slots.find((s) => s.position === 'midroll');
    expect(mid?.enabled).toBe(false);
  });

  it('has analytics enabled flag', () => {
    expect(DEFAULT_CONFIG.analytics.enabled).toBe(true);
  });
});

// ---------- slots.ts tests ----------

describe('createSlot', () => {
  it('returns a context object with provided id and position', () => {
    const ctx = createSlot({ id: 'slot_test_1', position: 'test' });
    expect(ctx.id).toBe('slot_test_1');
    expect(ctx.position).toBe('test');
  });

  it('creates a DOM element with the expected id when no element exists', () => {
    const id = `slots-test-slot-${Date.now()}`;
    document.body.innerHTML = '';
    const ctx = createSlot({ id, position: 'banner_header' });
    expect(ctx.containerEl).toBeTruthy();
    expect(ctx.containerEl?.id).toBe(id);
  });

  it('reuses existing DOM element for same id', () => {
    const id = `slots-test-existing-${Date.now()}`;
    document.body.innerHTML = `<div id="${id}"></div>`;
    const ctx1 = createSlot({ id, position: 'test' });
    const ctx2 = createSlot({ id, position: 'test' });
    expect(ctx1.containerEl).toBe(ctx2.containerEl);
  });

  it('uses default values when arguments omitted', () => {
    document.body.innerHTML = '';
    const ctx = createSlot({});
    expect(typeof ctx.id).toBe('string');
    expect(ctx.position).toBe('banner_header');
  });
});

describe('destroySlot', () => {
  it('replaces the slot element with a clone (removing listeners)', () => {
    const id = `slot-destroy-test-${Date.now()}`;
    document.body.innerHTML = `<div id="${id}">content</div>`;
    const el = document.getElementById(id)!;
    const ctx: SlotContext = { id, position: 'test', containerEl: el };
    destroySlot(ctx);
    expect(el.parentNode).toBeFalsy(); // cloneNode replaces the original
  });

  it('handles null context gracefully', () => {
    const ctx: SlotContext = { id: '', position: '', containerEl: null };
    expect(() => destroySlot(ctx)).not.toThrow();
  });
});

describe('getConfigForPosition', () => {
  it('returns config for existing position', () => {
    const cfg = getConfigForPosition('preroll');
    expect(cfg?.id).toBe('ad_preroll');
  });

  it('returns undefined for unknown position', () => {
    const cfg = getConfigForPosition('nonexistent_position');
    expect(cfg).toBeUndefined();
  });
});

// ---------- AnalyticsEventBus.ts tests ----------

describe('publishEvent', () => {
  it('notifies all subscribers on ad_impression', () => {
    const events: AdAnalyticsEvent[] = [];
    const unsub = subscribeAdEvents((ev) => { events.push(ev); });
    publishEvent({ type: 'ad_impression', slotId: 's1', position: 'preroll' });
    expect(events).toHaveLength(1);
    expect(events[0].type).toBe('ad_impression');
    unsub();
  });

  it('notifies all subscribers on ad_click', () => {
    const events: AdAnalyticsEvent[] = [];
    subscribeAdEvents((ev) => { events.push(ev); });
    publishEvent({ type: 'ad_click', slotId: 's1', position: 'banner_header', destinationUrl: '/ad/1' });
    expect(events[0].type).toBe('ad_click');
  });

  it('notifies on ad_skip', () => {
    const events: AdAnalyticsEvent[] = [];
    subscribeAdEvents((ev) => { events.push(ev); });
    publishEvent({ type: 'ad_skip', slotId: 's1', position: 'preroll' });
    expect(events[0].type).toBe('ad_skip');
  });

  it('notifies on ad_complete with duration', () => {
    const events: AdAnalyticsEvent[] = [];
    subscribeAdEvents((ev) => { events.push(ev); });
    publishEvent({ type: 'ad_complete', slotId: 's1', position: 'preroll', adDuration: 15 });
    expect(events[0].type).toBe('ad_complete');
  });

  it('notifies on ad_error with code and message', () => {
    const events: AdAnalyticsEvent[] = [];
    subscribeAdEvents((ev) => { events.push(ev); });
    publishEvent({ type: 'ad_error', slotId: 's1', position: 'postroll', code: 'NO_FILL', message: 'No ads available' });
    expect(events[0].type).toBe('ad_error');
  });

  it('unsubscribed listener does not receive future events', () => {
    const events: AdAnalyticsEvent[] = [];
    const unsub = subscribeAdEvents((ev) => { events.push(ev); });
    publishEvent({ type: 'ad_impression', slotId: 's1', position: 'preroll' });
    expect(events).toHaveLength(1);

    unsub();
    publishEvent({ type: 'ad_impression', slotId: 's2', position: 'banner_sidebar' });
    expect(events).toHaveLength(1); // no new event added
  });
});
