/**
 * GA4 analytics helper for Next.js apps.
 * Wraps `gtag.js` — initializes the measurement ID, fires page_view / events, sets user properties.
 */

declare global {
  interface Window {
    gtag: (command: string, targetId: string, config?: Record<string, unknown>) => void;
    dataLayer: unknown[];
  }
}

export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID ?? '';

// Does gtag exist and is the ID populated? (server-side check during render)
function hasGtag(): boolean {
  return !(typeof window === 'undefined') && typeof window.gtag === 'function' && !!GA_MEASUREMENT_ID;
}

export const GA_INIT_SCRIPT = `
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
(g=>{var s=document.createElement(script),j=document.getElementsByTagName(script)[0];
s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID_PLACEHOLDER';
j.parentNode.insertBefore(s,j);
})(window);
`;

export type GaEventOptions = {
  event_category: string;
  event_label?: string;
  value?: number;
  [key: string]: unknown;
};

/** Fire an analytics page_view (called automatically by GoogleAnalytics). */
export function gaPageView(path: string): void {
  if (!hasGtag()) return;
  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: path,
  });
}

/** Fire a custom event to GA4. */
export function gaEvent(options: GaEventOptions): void {
  if (!hasGtag()) return;
  const { event_category, event_label, value, ...rest } = options;
  window.gtag('event', event_category, {
    event_label,
    value,
    ...rest,
  });
}
