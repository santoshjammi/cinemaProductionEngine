import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePipeline } from './usePipeline';

describe('usePipeline', () => {
  it('returns default state', () => {
    const { result } = renderHook(() => usePipeline());
    expect(result.current.pipeline).toBeNull();
    expect(result.current.history).toEqual([]);
    expect(result.current.isRunning).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('reset clears state', () => {
    const { result } = renderHook(() => usePipeline());
    act(() => {
      result.current.reset();
    });
    expect(result.current.pipeline).toBeNull();
  });
});
