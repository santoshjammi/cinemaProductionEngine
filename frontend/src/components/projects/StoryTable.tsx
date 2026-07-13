'use client';

import Link from 'next/link';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { formatDate } from '@/lib/utils';
import { PlusIcon, FileTextIcon } from 'lucide-react';
import type { StorySummary } from '@/lib/types';

interface StoryTableProps {
  stories: StorySummary[];
  projectId: string;
  onNewStory: () => void;
}

export function StoryTable({ stories, projectId, onNewStory }: StoryTableProps) {
  if (stories.length === 0) {
    return (
      <EmptyState
        icon={<FileTextIcon className="w-12 h-12" />}
        title="No stories yet"
        description="Create your first story in this project"
        action={{ label: 'New Story', onClick: onNewStory }}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{stories.length} stories</p>
        <Button size="sm" onClick={onNewStory}>
          <PlusIcon className="w-4 h-4 mr-1" />
          New Story
        </Button>
      </div>

      <div className="rounded-md border">
        <div className="grid grid-cols-[1fr_auto_auto_auto] gap-2 p-3 bg-muted/50 text-xs font-medium text-muted-foreground">
          <span>Topic</span>
          <span>Status</span>
          <span>Created</span>
          <span></span>
        </div>
        {stories.map((story) => (
          <Link
            key={story.id}
            href={`/pipeline/${story.id}`}
            className="grid grid-cols-[1fr_auto_auto_auto] gap-2 p-3 items-center border-t hover:bg-accent transition-colors"
          >
            <span className="font-medium text-sm truncate">{story.topic}</span>
            <div>
              <Badge
                variant={
                  story.status === 'completed' ? 'success'
                  : story.status === 'failed' ? 'destructive'
                  : 'warning'
                }
                className="text-[10px]"
              >
                {story.status}
              </Badge>
            </div>
            <span className="text-xs text-muted-foreground">{formatDate(story.created_at)}</span>
            <span className="text-xs text-primary">&rarr;</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
