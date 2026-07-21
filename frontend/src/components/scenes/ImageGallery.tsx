'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ImageIcon, Loader2, RefreshCw } from 'lucide-react';
import { getImageUrl } from '@/lib/api';
import type { SceneImageResult } from '@/lib/types';
import type { SceneResult } from '@/lib/types';

interface ImageGalleryProps {
  pipelineId: string;
  scenes: SceneResult[];
  images: SceneImageResult[];
  isGenerating: boolean;
  onGenerateAll: () => void;
  onRegenerateScene?: (sceneNumber: number) => void;
  story?: { title: string; synopsis: string; logline: string; emotionalTone: string; themes: string[] };
}

export default function ImageGallery({
  pipelineId,
  scenes,
  images,
  isGenerating,
  onGenerateAll,
  onRegenerateScene,
  story,
}: ImageGalleryProps) {
  const completedCount = images.filter((i) => i.status === 'completed').length;
  const totalCount = scenes.length;

  const getImageStatus = (sceneNumber: number): SceneImageResult | undefined =>
    images.find((i) => i.sceneNumber === sceneNumber);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Scene Images</CardTitle>
        <Button
          onClick={onGenerateAll}
          disabled={isGenerating || totalCount === 0}
          size="sm"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              Generating…
            </>
          ) : completedCount > 0 ? (
            <>
              <RefreshCw className="w-4 h-4 mr-1" />
              Regenerate All
            </>
          ) : (
            <>
              <ImageIcon className="w-4 h-4 mr-1" />
              Generate Images
            </>
          )}
        </Button>
      </CardHeader>
      {story && (
        <CardContent className="border-b pb-4 mb-4">
          <h3 className="text-sm font-semibold mb-1">{story.title}</h3>
          <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3">
            {story.synopsis}
          </p>
          {story.themes.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {story.themes.map((t, i) => (
                <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                  {t}
                </span>
              ))}
            </div>
          )}
        </CardContent>
      )}
      <CardContent>
        {totalCount > 0 && completedCount > 0 && (
          <p className="text-sm text-muted-foreground mb-4">
            {completedCount}/{totalCount} images generated
          </p>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {scenes.map((scene) => {
            const img = getImageStatus(scene.sceneNumber);
            const sceneNum = scene.sceneNumber;

            let content;
            if (img?.status === 'generating') {
              content = (
                <div className="flex flex-col items-center justify-center h-full gap-2">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <span className="text-xs text-muted-foreground">Generating…</span>
                </div>
              );
            } else if (img?.status === 'failed') {
              content = (
                <div className="flex flex-col items-center justify-center h-full gap-2 p-4 text-center">
                  <span className="text-xs text-red-500">Failed</span>
                  <span className="text-[10px] text-muted-foreground line-clamp-2">
                    {img.error}
                  </span>
                  {onRegenerateScene && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onRegenerateScene(sceneNum)}
                      className="text-xs"
                    >
                      <RefreshCw className="w-3 h-3 mr-1" />
                      Retry
                    </Button>
                  )}
                </div>
              );
            } else if (img?.status === 'completed' && img.imageUrl) {
              content = (
                <img
                  src={getImageUrl(pipelineId, sceneNum)}
                  alt={`Scene ${sceneNum}`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.src = img.imageUrl || '';
                  }}
                />
              );
            } else {
              content = (
                <div className="flex flex-col items-center justify-center h-full gap-2">
                  <ImageIcon className="w-8 h-8 text-muted-foreground/40" />
                  <span className="text-xs text-muted-foreground">Pending</span>
                </div>
              );
            }

            return (
              <div
                key={sceneNum}
                className="relative aspect-video rounded-lg border bg-muted overflow-hidden group"
              >
                {content}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                  <p className="text-xs text-white font-medium truncate">
                    Scene {sceneNum}: {scene.title}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {totalCount === 0 && (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <ImageIcon className="w-12 h-12 text-muted-foreground/20" />
            <p className="text-sm text-muted-foreground">
              No scenes available. Complete the pipeline first.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
