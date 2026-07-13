'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { StoryResult } from '@/lib/types';

interface StoryViewerProps {
  story: StoryResult;
}

export default function StoryViewer({ story }: StoryViewerProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-xl">{story.title}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1 italic">
              {story.logline}
            </p>
          </div>
          <Badge variant="secondary">{story.emotionalTone}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-1">
            Synopsis
          </h4>
          <p className="text-sm leading-relaxed">{story.synopsis}</p>
        </div>

        {story.researchContext && (
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-1">
              Research Context
            </h4>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {story.researchContext}
            </p>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {story.themes.map((theme, i) => (
            <Badge key={i} variant="outline">
              {theme}
            </Badge>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Target Audience: </span>
            {story.targetAudience}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}