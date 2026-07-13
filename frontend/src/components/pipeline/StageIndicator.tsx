'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn, getStageLabel } from '@/lib/utils';
import type {
  PipelineStage,
  PipelineStageName,
  PipelineStageStatus,
} from '@/lib/types';

interface StageIndicatorProps {
  stages: PipelineStage[];
  currentStage?: string;
  onStageClick?: (stage: PipelineStageName) => void;
}

const stageOrder: PipelineStageName[] = [
  'research',
  'story',
  'scenes',
  'dialogues',
  'prompts',
  'validation',
];

const statusIcons: Record<PipelineStageStatus, string> = {
  pending: '○',
  running: '◌',
  completed: '●',
  failed: '✕',
  skipped: '—',
};

const statusColors: Record<PipelineStageStatus, string> = {
  pending: 'text-slate-300 dark:text-slate-600',
  running: 'text-blue-500 animate-pulse',
  completed: 'text-emerald-500',
  failed: 'text-red-500',
  skipped: 'text-slate-400',
};

function StageDot({
  status,
  isActive,
}: {
  status: PipelineStageStatus;
  isActive: boolean;
}) {
  return (
    <span
      className={cn(
        'text-lg leading-none transition-colors',
        statusColors[status],
        isActive && 'ring-2 ring-primary ring-offset-2 rounded-full'
      )}
    >
      {statusIcons[status]}
    </span>
  );
}

export default function StageIndicator({
  stages,
  currentStage,
  onStageClick,
}: StageIndicatorProps) {
  const stageMap = new Map(stages.map((s) => [s.name, s]));

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between gap-1">
          {stageOrder.map((name, index) => {
            const stage = stageMap.get(name);
            const status = stage?.status ?? 'pending';
            const isActive = name === currentStage;
            const isClickable = status === 'failed' && onStageClick;

            return (
              <React.Fragment key={name}>
                <button
                  onClick={
                    isClickable
                      ? () => onStageClick(name)
                      : undefined
                  }
                  className={cn(
                    'flex flex-col items-center gap-1.5 group',
                    isClickable && 'cursor-pointer hover:opacity-80',
                    !isClickable && 'cursor-default'
                  )}
                  disabled={!isClickable}
                  title={
                    stage?.error
                      ? `${getStageLabel(name)}: ${stage.error}`
                      : getStageLabel(name)
                  }
                >
                  <StageDot status={status} isActive={isActive} />
                  <span
                    className={cn(
                      'text-[10px] font-medium whitespace-nowrap',
                      isActive
                        ? 'text-primary'
                        : 'text-muted-foreground'
                    )}
                  >
                    {getStageLabel(name)}
                  </span>
                  {status === 'failed' && stage?.error && (
                    <span className="text-[8px] text-red-500 max-w-[80px] truncate">
                      {stage.error}
                    </span>
                  )}
                </button>
                {index < stageOrder.length - 1 && (
                  <div className="flex-1 h-px bg-border mx-1" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}