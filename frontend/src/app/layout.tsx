import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Text Cinema Engine',
  description: 'Generate cinematic videos from story prompts',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased min-h-screen">
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
