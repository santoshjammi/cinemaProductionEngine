import { DEFAULT_CONFIG, type AdConfig } from './config';

export function loadAdConfig(): Promise<AdConfig> {
  return new Promise((resolve) => {
    resolve({ ...DEFAULT_CONFIG });
  });
}
