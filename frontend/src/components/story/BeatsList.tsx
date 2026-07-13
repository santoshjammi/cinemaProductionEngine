'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface Beat {
  id: number;
  title: string;
  description: string;
  type: 'setup' | 'conflict' | 'rising' | 'climax' | 'falling' | 'resolution';
}

interface BeatsListProps {
  beats: Beat[];
  className?: string;
}

const beatColors: Record<string, string> = {
  setup: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100',
  conflict:
    'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-100',
  rising:
    'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-100',
  climax: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100',
  falling:
    'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-100',
  resolution:
    'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-100',
};

export default function BeatsList({ beats, className }: BeatsListProps) {
  if (beats.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-lg">Story Beats</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No story beats available yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-lg">Story Beats</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative pl-6 space-y-4">
          {beats.map((beat, index) => (
            <div key={beat.id} className="relative">
              {index < beats.length - 1 && (
                <div className="absolute left-[-13px] top-4 bottom-[-16px] w-px bg-border" />
              )}
              <div className="absolute left-[-18px] top-1.5 w-3 h-3 rounded-full border-2 border-primary bg-background" />
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-medium">{beat.title}</h4>
                  <Badge
                    variant="outline"
                    className={`text-[10px] px-1.5 py-0 ${
                      beatColors[beat.type] || ''
                    }`}
                  >
                    {beat.type}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {beat.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
