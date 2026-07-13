'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { SceneResult } from '@/lib/types';

interface EmotionalArcProps {
  scenes: SceneResult[];
  className?: string;
}

const emotionColors: Record<string, string> = {
  joy: 'bg-yellow-500',
  sadness: 'bg-blue-600',
  fear: 'bg-purple-600',
  anger: 'bg-red-600',
  surprise: 'bg-orange-400',
  disgust: 'bg-green-700',
  anticipation: 'bg-cyan-400',
  trust: 'bg-teal-500',
  wonder: 'bg-indigo-400',
  neutral: 'bg-slate-400',
  hope: 'bg-emerald-400',
  despair: 'bg-slate-700',
  tension: 'bg-rose-500',
  relief: 'bg-lime-400',
};

const emotionLabels: Record<string, string> = {
  joy: 'Joy',
  sadness: 'Sadness',
  fear: 'Fear',
  anger: 'Anger',
  surprise: 'Surprise',
  disgust: 'Disgust',
  anticipation: 'Anticipation',
  trust: 'Trust',
  wonder: 'Wonder',
  neutral: 'Neutral',
  hope: 'Hope',
  despair: 'Despair',
  tension: 'Tension',
  relief: 'Relief',
};

export default function EmotionalArc({
  scenes,
  className,
}: EmotionalArcProps) {
  if (scenes.length === 0) return null;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-lg">Emotional Arc</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-end gap-1 h-24">
          {scenes.map((scene) => {
            const color =
              emotionColors[scene.emotionalBeat.toLowerCase()] ||
              'bg-slate-400';
            return (
              <div
                key={scene.sceneNumber}
                className="flex-1 flex flex-col items-center gap-1"
              >
                <div
                  className={`w-full rounded-t ${color} transition-all duration-300`}
                  style={{
                    height: `${Math.max(20, Math.min(100, scene.sceneNumber * 15))}%`,
                  }}
                />
                <span className="text-[10px] text-muted-foreground">
                  {scene.sceneNumber}
                </span>
              </div>
            );
          })}
        </div>

        <div className="space-y-1">
          {scenes.map((scene) => {
            const beat = scene.emotionalBeat.toLowerCase();
            const color = emotionColors[beat] || 'bg-slate-400';
            const label = emotionLabels[beat] || beat;
            return (
              <div
                key={scene.sceneNumber}
                className="flex items-center gap-2 text-xs"
              >
                <span className="w-6 text-muted-foreground text-right">
                  {scene.sceneNumber}
                </span>
                <div className={`w-2 h-2 rounded-full ${color}`} />
                <span className="font-medium truncate">{scene.title}</span>
                <Badge variant="outline" className="ml-auto">
                  {label}
                </Badge>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
