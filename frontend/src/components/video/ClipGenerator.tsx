'use client';

import { Card, CardContent } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import type { VideoClipResult } from '@/lib/types';

interface ClipGeneratorProps {
  clips: VideoClipResult[];
  onGenerateAll: () => void;
  isGenerating: boolean;
}

export default function ClipGenerator({
  clips,
  onGenerateAll,
  isGenerating,
}: ClipGeneratorProps) {
  const completedClips = clips.filter(
    (c) => c.status === 'completed'
  ).length;

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-sm">Video Clips</h4>
            <p className="text-xs text-muted-foreground">
              {completedClips}/{clips.length} clips generated
            </p>
          </div>
          <button
            onClick={onGenerateAll}
            disabled={isGenerating || clips.length === 0}
            className="inline-flex items-center justify-center rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? 'Generating…' : 'Generate All'}
          </button>
        </div>

        {clips.length > 0 && (
          <Progress
            value={(completedClips / clips.length) * 100}
            className="h-1.5"
          />
        )}

        <div className="grid gap-2">
          {clips.map((clip) => (
            <div
              key={clip.sceneNumber}
              className="flex items-center justify-between p-2 rounded border bg-card"
            >
              <span className="text-xs font-medium">
                Scene {clip.sceneNumber}
              </span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded ${
                  clip.status === 'completed'
                    ? 'bg-emerald-100 text-emerald-700'
                    : clip.status === 'generating'
                      ? 'bg-blue-100 text-blue-700 animate-pulse'
                      : clip.status === 'failed'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-slate-100 text-slate-700'
                }`}
              >
                {clip.status}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}