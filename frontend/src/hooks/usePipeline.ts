import { useCallback, useEffect } from 'react';
import { usePipelineStore } from '@/lib/store';
import type { PipelineInput, PipelineStageName } from '@/lib/types';

export function usePipeline() {
  const store = usePipelineStore();

  const start = useCallback(
    async (input: PipelineInput) => {
      await store.startPipeline(input);
    },
    [store.startPipeline]
  );

  const retry = useCallback(
    async (stage: PipelineStageName | string) => {
      await store.retryStage(stage);
    },
    [store.retryStage]
  );

  const poll = useCallback(
    async (id: string) => {
      await store.pollStatus(id);
    },
    [store.pollStatus]
  );

  const loadHistory = useCallback(async () => {
    await store.loadHistory();
  }, [store.loadHistory]);

  const reset = useCallback(() => {
    store.reset();
  }, [store.reset]);

  useEffect(() => {
    if (store.currentPipeline?.id && store.currentPipeline.status === 'running') {
      poll(store.currentPipeline.id);
    }
  }, [store.currentPipeline?.id, store.currentPipeline?.status]);

  return {
    pipeline: store.currentPipeline,
    history: store.history,
    isRunning: store.isRunning,
    error: store.error,
    start,
    retry,
    poll,
    loadHistory,
    reset,
  };
}
