import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function toCamelCase(obj: any): any {
  if (obj === null || obj === undefined) return obj;
  if (Array.isArray(obj)) return obj.map(toCamelCase);
  if (typeof obj === 'object' && !(obj instanceof Date)) {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
      acc[camelKey] = toCamelCase(obj[key]);
      return acc;
    }, {} as Record<string, any>);
  }
  return obj;
}

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    research: 'Internet Research',
    story: 'Story Generation',
    scenes: 'Scene Breakdown',
    dialogues: 'Dialogue Writing',
    prompts: 'Cinematic Prompts',
    validation: 'Validation & Metrics',
  };
  return labels[stage] || stage;
}

export function getStageOrder(stage: string): number {
  const order: Record<string, number> = {
    research: 0,
    story: 1,
    scenes: 2,
    dialogues: 3,
    prompts: 4,
    validation: 5,
  };
  return order[stage] ?? -1;
}

export function getOverallProgress(stages: { status: string }[]): number {
  if (stages.length === 0) return 0;
  const completed = stages.filter(
    (s) => s.status === 'completed' || s.status === 'skipped'
  ).length;
  return Math.round((completed / stages.length) * 100);
}