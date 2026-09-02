export enum SlotPosition {
  PREROLL = 'preroll',
  POSTROLL = 'postroll',
  MIDROLL = 'midroll',
  BANNER_HEADER = 'banner_header',
  BANNER_SIDEBAR = 'banner_sidebar',
}

export interface AdSlotDefinition {
  id: string;
  position: SlotPosition;
  adType: 'video' | 'banner';
  duration?: number;
  minGapSeconds?: number;
  maxFrequency?: number;
}

export interface AdConfig {
  slots: AdSlotDefinition[];
  enabled: boolean;
  failClosed: boolean;
  frequencyCapWindowMinutes?: number;
}

export const DEFAULT_CONFIG: Required<AdConfig> = {
  enabled: true,
  failClosed: true,
  frequencyCapWindowMinutes: 60,
  slots: [
    { id: 'preroll_1', position: SlotPosition.PREROLL, adType: 'video', duration: 30 },
    { id: 'postroll_1', position: SlotPosition.POSTROLL, adType: 'video', duration: 30 },
    { id: 'midroll_break_1', position: SlotPosition.MIDROLL, adType: 'video', duration: 25, minGapSeconds: 60 },
    { id: 'banner_header_1', position: SlotPosition.BANNER_HEADER, adType: 'banner', maxFrequency: 2 },
    { id: 'banner_sidebar_1', position: SlotPosition.BANNER_SIDEBAR, adType: 'banner' },
  ],
};

export const EMPTY_CONFIG: Required<AdConfig> = {
  ...DEFAULT_CONFIG,
  enabled: false,
  failClosed: true,
  slots: [],
};
