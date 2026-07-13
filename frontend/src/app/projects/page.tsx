'use client';

import { useEffect } from 'react';
import { usePipelineStore } from '@/lib/store';
import { ProjectCard } from '@/components/projects/ProjectCard';
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog';
import { EmptyState } from '@/components/ui/EmptyState';
import { FolderIcon } from 'lucide-react';

export default function ProjectsPage() {
  const { projects, loadProjects } = usePipelineStore();

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground mt-1">
              Organize your story ideas into projects
            </p>
          </div>
          <CreateProjectDialog />
        </div>

        {projects.length === 0 ? (
          <EmptyState
            icon={<FolderIcon className="w-12 h-12" />}
            title="No projects yet"
            description="Create your first project to get started"
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
