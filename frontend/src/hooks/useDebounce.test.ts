import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 500));
    expect(result.current).toBe('hello');
  });

  it('updates value after delay', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'hello', delay: 100 } }
    );
    expect(result.current).toBe('hello');

    rerender({ value: 'world', delay: 100 });
    expect(result.current).toBe('hello');

    await act(async () => {
      await new Promise((r) => setTimeout(r, 150));
    });
    expect(result.current).toBe('world');
  });

  it('cancels previous timeout on rapid updates', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'a', delay: 100 } }
    );

    rerender({ value: 'b', delay: 100 });
    rerender({ value: 'c', delay: 100 });

    await act(async () => {
      await new Promise((r) => setTimeout(r, 150));
    });
    expect(result.current).toBe('c');
  });
});
