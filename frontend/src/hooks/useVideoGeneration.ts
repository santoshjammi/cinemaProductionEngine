import { useCallback, useEffect, useRef } from 'react';
import { usePipelineStore } from '@/lib/store';

export function useVideoGeneration() {
  const store = usePipelineStore();
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const generate = useCallback(async () => {
    await store.startVideoGen();
  }, [store.startVideoGen]);

  const poll = useCallback(
    async (id: string) => {
      await store.pollVideoGen(id);
    },
    [store.pollVideoGen]
  );

  useEffect(() => {
    const progress = store.generationProgress;
    if (!progress) return;

    const isActive =
      progress.clips?.some((c) => c.status === 'generating' || c.status === 'pending') ||
      progress.finalVideo?.status === 'pending' ||
      progress.finalVideo?.status === 'assembling';

    if (isActive) {
      const id = progress.pipeline?.id;
      if (id) {
        pollIntervalRef.current = setInterval(() => poll(id), 2000);
      }
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [
    store.generationProgress?.clips,
    store.generationProgress?.finalVideo?.status,
    store.generationProgress?.pipeline?.id,
  ]);

  return {
    progress: store.generationProgress,
    isGenerating:
      store.generationProgress?.clips?.some((c) => c.status === 'generating') ??
      false,
    isAssembling:
      store.generationProgress?.finalVideo?.status === 'assembling',
    isComplete: store.generationProgress?.finalVideo?.status === 'completed',
    error: store.error,
    generate,
  };
}
