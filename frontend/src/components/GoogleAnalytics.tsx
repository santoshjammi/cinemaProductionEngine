'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import Script from 'next/script';
import { GA_MEASUREMENT_ID, GA_INIT_SCRIPT, gaEvent, gaPageView } from '@/lib/analytics';

export default function GoogleAnalytics() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Track page views when the path changes
  useEffect(() => {
    if (pathname) {
      gaPageView(pathname + (searchParams?.toString() ? '?' + searchParams.toString() : ''));
    }
  }, [pathname, searchParams]);

  return (
    <>
      {/* Inject gtag.js */}
      <Script
        id="gtag-init"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: GA_INIT_SCRIPT.replace(
            'GA_MEASUREMENT_ID_PLACEHOLDER',
            GA_MEASUREMENT_ID || 'DUMMY'
          ),
        }}
      />

      {/* Inline the default_pageview event */}
      <Script id="gtag-config" strategy="afterInteractive">
        {`
          window.gtag && window.gtag('config', '${GA_MEASUREMENT_ID}', {
            page_path: window.location.pathname,
          });
        `}
      </Script>
    </>
  );
}
