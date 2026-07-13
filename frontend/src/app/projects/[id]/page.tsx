'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { usePipelineStore } from '@/lib/store';
import { StoryTable } from '@/components/projects/StoryTable';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { ArrowLeftIcon } from 'lucide-react';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;
  const { currentProject, loadProject } = usePipelineStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadProject(id).finally(() => setLoading(false));
    }
  }, [id]);

  const handleNewStory = () => {
    if (currentProject?.id) {
      router.push(`/?projectId=${currentProject.id}`);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
        <div className="container py-8 space-y-4">
          <LoadingSkeleton className="h-8 w-48" />
          <LoadingSkeleton className="h-64 w-full" />
        </div>
      </main>
    );
  }

  if (!currentProject) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
        <div className="container py-8">
          <p className="text-muted-foreground">Project not found</p>
          <Link href="/projects" className="text-primary text-sm">Back to projects</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/projects" className="text-sm text-muted-foreground hover:text-foreground">
              <ArrowLeftIcon className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold">{currentProject.name}</h1>
              {currentProject.description && (
                <p className="text-sm text-muted-foreground">{currentProject.description}</p>
              )}
            </div>
          </div>
        </div>

        <ErrorBoundary>
          <StoryTable
            stories={currentProject.stories}
            projectId={currentProject.id}
            onNewStory={handleNewStory}
          />
        </ErrorBoundary>
      </div>
    </main>
  );
}
