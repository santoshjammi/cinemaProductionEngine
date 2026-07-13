'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import type { PipelineMetrics } from '@/lib/types';

interface MetricsPanelProps {
  metrics: PipelineMetrics;
}

function MetricBar({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">
          {(value * 100).toFixed(0)}%
        </span>
      </div>
      <Progress value={value * 100} className="h-2" />
    </div>
  );
}

export default function MetricsPanel({ metrics }: MetricsPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Pipeline Metrics</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <MetricBar
          label="YAML Validation Pass Rate"
          value={metrics.yamlValidationPassRate}
        />
        <MetricBar
          label="Scene Completion Rate"
          value={metrics.sceneCompletionRate}
        />
        <MetricBar
          label="Emotional Arc Score"
          value={metrics.emotionalArcScore}
        />
        <MetricBar
          label="Visual Prompt Quality"
          value={metrics.visualPromptQualityScore}
        />

        <div className="grid grid-cols-2 gap-4 pt-2 border-t text-sm">
          <div>
            <span className="text-muted-foreground">Total Scenes: </span>
            {metrics.totalScenes ?? '—'}
          </div>
          <div>
            <span className="text-muted-foreground">Duration: </span>
            {metrics.totalDuration ?? '—'}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}