import { describe, it, expect } from 'vitest';
import {
  cn,
  formatDuration,
  formatDate,
  getStageLabel,
  getStageOrder,
  getOverallProgress,
} from './utils';

describe('cn', () => {
  it('merges class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', 'visible')).toBe('base visible');
  });

  it('merges tailwind classes (last wins)', () => {
    expect(cn('px-4', 'px-2')).toBe('px-2');
  });
});

describe('formatDuration', () => {
  it('formats seconds into m:ss', () => {
    expect(formatDuration(0)).toBe('0:00');
    expect(formatDuration(5)).toBe('0:05');
    expect(formatDuration(60)).toBe('1:00');
    expect(formatDuration(90)).toBe('1:30');
    expect(formatDuration(3600)).toBe('60:00');
  });
});

describe('formatDate', () => {
  it('formats ISO date string', () => {
    const result = formatDate('2026-06-30T12:00:00Z');
    expect(result).toContain('Jun');
    expect(result).toContain('30');
  });
});

describe('getStageLabel', () => {
  it('returns human-readable labels', () => {
    expect(getStageLabel('research')).toBe('Internet Research');
    expect(getStageLabel('story')).toBe('Story Generation');
    expect(getStageLabel('scenes')).toBe('Scene Breakdown');
    expect(getStageLabel('unknown')).toBe('unknown');
  });
});

describe('getStageOrder', () => {
  it('returns correct order indices', () => {
    expect(getStageOrder('research')).toBe(0);
    expect(getStageOrder('story')).toBe(1);
    expect(getStageOrder('scenes')).toBe(2);
    expect(getStageOrder('unknown')).toBe(-1);
  });
});

describe('getOverallProgress', () => {
  it('returns 0 for empty stages', () => {
    expect(getOverallProgress([])).toBe(0);
  });

  it('calculates progress percentage', () => {
    const stages = [
      { status: 'completed' },
      { status: 'completed' },
      { status: 'running' },
      { status: 'pending' },
    ];
    expect(getOverallProgress(stages)).toBe(50);
  });

  it('counts skipped as completed', () => {
    const stages = [
      { status: 'completed' },
      { status: 'skipped' },
      { status: 'pending' },
    ];
    expect(getOverallProgress(stages)).toBe(67);
  });
});