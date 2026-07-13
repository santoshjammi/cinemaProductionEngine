'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FolderIcon } from 'lucide-react';
import type { Project } from '@/lib/types';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
        <CardContent className="p-4 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <FolderIcon className="w-5 h-5 text-primary shrink-0" />
            <h3 className="font-semibold truncate">{project.name}</h3>
          </div>
          {project.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">{project.description}</p>
          )}
          <div className="flex items-center gap-2 mt-auto pt-2">
            <Badge variant="secondary" className="text-xs">
              {project.story_count} {project.story_count === 1 ? 'story' : 'stories'}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
