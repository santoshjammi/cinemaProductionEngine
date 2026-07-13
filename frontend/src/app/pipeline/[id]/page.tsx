'use client';

import React, { useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import PipelineView from '@/components/pipeline/PipelineView';
import { usePipelineStore } from '@/lib/store';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';

export default function PipelineDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const { currentPipeline, pollStatus, reset } = usePipelineStore();

  useEffect(() => {
    if (id) {
      pollStatus(id);
    }
    return () => {
      reset();
    };
  }, [id]);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <Link href="/projects" className="hover:text-foreground transition-colors">
                Projects
              </Link>
              {currentPipeline?.project_id && (
                <>
                  <span>/</span>
                  <Link
                    href={`/projects/${currentPipeline.project_id}`}
                    className="hover:text-foreground transition-colors"
                  >
                    Project
                  </Link>
                </>
              )}
              <span>/</span>
              <span>Story</span>
            </div>
            <Link
              href="/"
              className="text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
            >
              &larr; Back to Home
            </Link>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50 mt-1">
              {currentPipeline?.topic || `Pipeline ${id?.slice(0, 8)}...`}
            </h1>
            {currentPipeline && (
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {currentPipeline.topic} &middot;{' '}
                {currentPipeline.status}
              </p>
            )}
          </div>
        </div>

        <ErrorBoundary>
          {currentPipeline ? (
            <PipelineView />
          ) : (
            <div className="space-y-4">
              <LoadingSkeleton className="h-8 w-48" />
              <LoadingSkeleton className="h-64 w-full" />
            </div>
          )}
        </ErrorBoundary>
      </div>
    </main>
  );
}
