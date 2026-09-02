import type { Metadata } from 'next';
import { Suspense } from 'react';
import './globals.css';
import GoogleAnalytics from '@/components/GoogleAnalytics';

const SITE_URL = 'https://textcinemaengine.com';

export const metadata: Metadata = {
  title: {
    default: 'Text Cinema Engine — AI Video Generation Platform',
    template: '%s | Text Cinema Engine',
  },
  description: 'Transform story ideas into cinematic video narratives. Generate, review, and certify cinematic content with our AI-powered pipeline.',
  keywords: ['AI video generation', 'text to video', 'cinematic videos', 'story to film', 'GENESIS3', 'creative integrity', 'video production', 'content certification'],
  authors: [{ name: 'Sai Ameya Technologies' }],
  creator: 'Sai Ameya Technologies',
  publisher: 'Sai Ameya Technologies',
  metadataBase: new URL(SITE_URL),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: SITE_URL,
    siteName: 'Text Cinema Engine',
    title: 'Text Cinema Engine — AI Video Generation Platform',
    description: 'Transform story ideas into cinematic video narratives with our AI-powered pipeline.',
    images: [
      {
        url: `${SITE_URL}/og-image.png`,
        width: 1200,
        height: 630,
        alt: 'Text Cinema Engine',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@textcinema',
    creator: '@textcinema',
    title: 'Text Cinema Engine — AI Video Generation Platform',
    description: 'Transform story ideas into cinematic video narratives.',
    images: [`${SITE_URL}/og-image.png`],
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <body className="antialiased min-h-screen">
        <Suspense fallback={null}>
          <GoogleAnalytics />
        </Suspense>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebSite',
              name: 'Text Cinema Engine',
              alternateName: ['TCE', 'TextCinema'],
              url: SITE_URL,
              description: 'AI-powered video generation and content certification platform.',
              publisher: {
                '@type': 'Organization',
                name: 'Sai Ameya Technologies',
                url: SITE_URL,
              },
            }),
          }}
        />
        {/* Apple-style global nav */}
        <nav className="global-nav fixed top-0 left-0 right-0 z-50">
          <div className="container flex items-center justify-between h-full max-w-[1440px] mx-auto px-lg">
            <div className="flex items-center gap-5">
              <a href="/" className="text-body-on-dark text-nav-link hover:opacity-80 transition-opacity font-body">
                Text Cinema
              </a>
              <a href="/projects" className="text-body-muted text-nav-link hover:text-body-on-dark transition-colors font-body">
                Projects
              </a>
              <a href="/genesis3" className="text-body-muted text-nav-link hover:text-body-on-dark transition-colors font-body">
                GENESIS3
              </a>
              <a href="/production" className="text-body-muted text-nav-link hover:text-body-on-dark transition-colors font-body">
                Production
              </a>
            </div>
            <div className="flex items-center gap-3">
              <button className="btn-dark-utility text-xs">Sign In</button>
            </div>
          </div>
        </nav>

        {/* Main content with nav offset */}
        <main className="pt-[44px]">
          {children}
        </main>

        {/* Apple-style footer */}
        <footer className="bg-canvas-parchment py-xxl px-lg">
          <div className="max-w-[1440px] mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-lg">
              <div>
                <h4 className="text-caption-strong text-ink-muted-48 mb-sm">Product</h4>
                <ul className="space-y-1">
                  <li><a href="/" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Home</a></li>
                  <li><a href="/projects" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Projects</a></li>
                  <li><a href="/genesis3" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>GENESIS3</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-caption-strong text-ink-muted-48 mb-sm">Resources</h4>
                <ul className="space-y-1">
                  <li><a href="#" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Documentation</a></li>
                  <li><a href="#" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>API</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-caption-strong text-ink-muted-48 mb-sm">Support</h4>
                <ul className="space-y-1">
                  <li><a href="#" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Help</a></li>
                  <li><a href="#" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Contact</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-caption-strong text-ink-muted-48 mb-sm">Legal</h4>
                <ul className="space-y-1">
                  <li><a href="#" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Privacy</a></li>
                  <li><a href="#" className="text-body text-ink-muted-80 hover:text-ink transition-colors" style={{ lineHeight: '2.41' }}>Terms</a></li>
                </ul>
              </div>
            </div>
            <div className="mt-xxl pt-lg border-t border-hairline">
              <p className="text-fine-print text-ink-muted-48">© 2026 Text Cinema Engine. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
