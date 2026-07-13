import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from './ErrorBoundary';
import { EmptyState } from './EmptyState';
import { RegenerateButton } from './RegenerateButton';

function BrokenComponent() {
  throw new Error('Test error');
}

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders fallback on error', () => {
    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('shows try again button on error', () => {
    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText('Try again')).toBeInTheDocument();
  });

  it('calls onError when caught', () => {
    const onError = vi.fn();
    render(
      <ErrorBoundary onError={onError}>
        <BrokenComponent />
      </ErrorBoundary>
    );
    expect(onError).toHaveBeenCalled();
  });

  it('renders custom fallback instead of default', () => {
    render(
      <ErrorBoundary fallback={<div>Custom Error UI</div>}>
        <BrokenComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText('Custom Error UI')).toBeInTheDocument();
  });
});

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(<EmptyState title="No items" description="Nothing here yet" />);
    expect(screen.getByText('No items')).toBeInTheDocument();
    expect(screen.getByText('Nothing here yet')).toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="Empty"
        action={{ label: 'Create', onClick }}
      />
    );
    fireEvent.click(screen.getByText('Create'));
    expect(onClick).toHaveBeenCalled();
  });

  it('renders icon when provided', () => {
    render(
      <EmptyState
        title="Empty"
        icon={<span data-testid="custom-icon">X</span>}
      />
    );
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });
});

describe('RegenerateButton', () => {
  it('renders with default text', () => {
    render(<RegenerateButton />);
    expect(screen.getByText('Regenerate')).toBeInTheDocument();
  });

  it('shows loading text when isLoading', () => {
    render(<RegenerateButton isLoading />);
    expect(screen.getByText('Regenerating...')).toBeInTheDocument();
  });

  it('is disabled when isLoading', () => {
    render(<RegenerateButton isLoading />);
    expect(screen.getByText('Regenerating...')).toBeDisabled();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<RegenerateButton onClick={onClick} />);
    fireEvent.click(screen.getByText('Regenerate'));
    expect(onClick).toHaveBeenCalled();
  });
});
