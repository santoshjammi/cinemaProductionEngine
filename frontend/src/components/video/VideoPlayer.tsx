'use client';

import { Card, CardContent } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { Button } from '@/components/ui/Button';
import { Loader2, Play, Download } from 'lucide-react';
import type { FinalVideoResult, VideoClipResult } from '@/lib/types';
import { getFinalVideoUrl } from '@/lib/api';
import { useEffect, useRef } from 'react';
import { AdManager } from '@/components/ads/AdManager';
import { analyticsEventBus } from '@/components/ads/AnalyticsEventBus';

interface VideoPlayerProps {
  finalVideo: FinalVideoResult | null;
  onGenerate: () => void;
  isGenerating: boolean;
  clips?: VideoClipResult[];
}

const VIDEO_AD_SLOTS = [
  { id: 'preroll_1', position: 'preroll' as const },
  { id: 'midroll_break_1', position: 'midroll' as const, minGap: 60 },
  { id: 'postroll_1', position: 'postroll' as const },
];

export default function VideoPlayer({
  finalVideo,
  onGenerate,
  isGenerating,
  clips,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const completedCount = clips?.filter((c) => c.status === 'completed').length ?? 0;
  const totalCount = clips?.length ?? 0;
  const allClipsDone = totalCount > 0 && completedCount === totalCount;
  const isAssembling = finalVideo?.status === 'assembling';

  useEffect(() => {
    AdManager.instance().activateAll();
    return () => AdManager.instance().deactivateAll();
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let lastMidrollCheck = 0;
    const handleTimeUpdate = () => {
      const current = video.currentTime || 0;
      for (const slot of VIDEO_AD_SLOTS) {
        if (slot.id === 'midroll_break_1') {
          const mid = Math.floor(video.duration || 0) / 2;
          if (current >= mid - 1 && current < mid + 1 && current - lastMidrollCheck > (slot as any).minGap) {
            lastMidrollCheck = current;
            analyticsEventBus.publish({ eventType: 'impression', slotId: slot.id, timestamp: Date.now(), sessionId: analyticsEventBus.getSessionId() });
          }
        }
      }
    };

    const handleEnded = () => {
      const activePostroll = AdManager.instance().requestSlot('postroll_1');
      if (activePostroll) {
        analyticsEventBus.publish({ eventType: 'impression', slotId: activePostroll.id, timestamp: Date.now(), sessionId: analyticsEventBus.getSessionId() });
      }
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('ended', handleEnded);
    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('ended', handleEnded);
    };
  }, [finalVideo?.videoUrl]);

  if (isGenerating || isAssembling) {
    return (
      <Card>
        <CardContent className="p-8 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">
            {isAssembling
              ? 'Assembling final video…'
              : totalCount > 0
                ? `Generating clips… ${completedCount}/${totalCount}`
                : 'Generating final video…'}
          </p>
          {clips && clips.length > 0 && (
            <div className="w-full max-w-xs space-y-1">
              {clips.map((clip) => (
                <div key={clip.sceneNumber} className="flex items-center gap-2 text-xs">
                  <span className="w-16 text-muted-foreground">Scene {clip.sceneNumber}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all duration-300"
                      style={{
                        width: `${
                          clip.status === 'completed'
                            ? 100
                            : clip.status === 'generating'
                              ? (clip.progress ?? 0) * 100
                              : 0
                        }%`,
                      }}
                    />
                  </div>
                  <span className="w-14 text-right text-muted-foreground">
                    {clip.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  if (finalVideo?.status === 'completed' && finalVideo.videoUrl) {
    return (
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <video
              controls
              className="w-full h-full"
              src={finalVideo.videoUrl}
            >
              <track kind="captions" />
            </video>
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="space-x-4 text-muted-foreground">
              {finalVideo.duration && (
                <span>Duration: {Math.round(finalVideo.duration)}s</span>
              )}
              {finalVideo.fileSize && (
                <span>Size: {(finalVideo.fileSize / 1024 / 1024).toFixed(1)}MB</span>
              )}
            </div>
            <Button size="sm" variant="outline" asChild>
              <a
                href={finalVideo.videoUrl}
                download
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-8 flex flex-col items-center justify-center gap-3">
        <Play className="w-8 h-8 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          {totalCount > 0
            ? 'All clips generated. Ready to assemble final video.'
            : 'Generate clips first, then assemble the final video'}
        </p>
        <Button onClick={onGenerate} disabled={isGenerating || (totalCount > 0 && !allClipsDone)}>
          {totalCount > 0 ? 'Assemble Final Video' : 'Generate Video'}
        </Button>
      </CardContent>
    </Card>
  );
}
