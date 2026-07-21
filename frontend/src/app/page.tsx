'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import PipelineView from '@/components/pipeline/PipelineView';
import HistoryList from '@/components/pipeline/HistoryList';
import Link from 'next/link';

function HomeContent() {
  const searchParams = useSearchParams();
  const projectId = searchParams?.get('projectId');

  return (
    <>
      {/* Hero section */}
      <section className="product-tile-light text-center">
        <div className="max-w-[980px] mx-auto space-y-4">
          <h1 className="text-hero-display text-ink">
            Text Cinema Engine
          </h1>
          <p className="text-lead text-ink-muted-80 max-w-[680px] mx-auto">
            Transform your story ideas into cinematic video narratives
          </p>
          <div className="flex items-center justify-center gap-3 pt-md">
            <Link href="/projects" className="btn-primary text-caption">
              View Projects
            </Link>
            <Link href="/" className="btn-secondary-pill text-caption">
              Learn More
            </Link>
          </div>
        </div>
      </section>

      {/* Pipeline section */}
      <section className="bg-canvas-parchment py-section px-lg">
        <div className="max-w-[1440px] mx-auto space-y-8">
          <PipelineView projectId={projectId || undefined} />
        </div>
      </section>

      {/* History section */}
      <section className="bg-canvas py-section px-lg">
        <div className="max-w-[1440px] mx-auto">
          <HistoryList />
        </div>
      </section>
    </>
  );
}

export default function Home() {
  return (
    <Suspense fallback={null}>
      <HomeContent />
    </Suspense>
  );
}
