import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

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
      <body className={`${inter.className} antialiased min-h-screen`}>
        <nav className="border-b bg-background">
          <div className="container flex items-center h-12 gap-6">
            <a href="/" className="font-bold text-sm hover:text-primary transition-colors">
              Text Cinema
            </a>
            <a href="/projects" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Projects
            </a>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}