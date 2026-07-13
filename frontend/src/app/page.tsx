'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import PipelineView from '@/components/pipeline/PipelineView';
import HistoryList from '@/components/pipeline/HistoryList';
import Link from 'next/link';
import { FolderIcon } from 'lucide-react';

function HomeContent() {
  const searchParams = useSearchParams();
  const projectId = searchParams?.get('projectId');

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <header className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
            Text Cinema Engine
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            Transform your story ideas into cinematic video narratives
          </p>
        </header>

        <div className="flex gap-2">
          <Link
            href="/projects"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <FolderIcon className="w-4 h-4" />
            Projects
          </Link>
        </div>

        <PipelineView projectId={projectId || undefined} />
        <HistoryList />
      </div>
    </main>
  );
}

export default function Home() {
  return (
    <Suspense fallback={null}>
      <HomeContent />
    </Suspense>
  );
}