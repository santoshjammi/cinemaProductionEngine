'use client';

import React from 'react';
import { Button } from './Button';
import { reportClientError, makeErrorReporter } from '@/lib/error-tracker';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  static UNHANDLED_ERROR_PREFIX = '[unhandled] ';

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  componentDidMount(): void {
    // Install global unhandled rejection listener once on mount
    window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
      const reason = event.reason;
      const message =
        typeof reason === 'string'
          ? reason
          : typeof reason?.message === 'string'
            ? reason.message
            : `Unhandled rejection: ${String(reason)}`;
      reportClientError({
        type: 'unhandled_rejection',
        message: ErrorBoundary.UNHANDLED_ERROR_PREFIX + message,
        stack:
          typeof reason?.stack === 'string'
            ? reason.stack
            : undefined,
      });
    });

    // Install global error listener for inline script / sync DOM errors
    window.addEventListener('error', (event: Event) => {
      if (event instanceof ErrorEvent && event.error) {
        reportClientError({
          type: 'unhandled_error',
          message: ErrorBoundary.UNHANDLED_ERROR_PREFIX + event.message,
          stack: event.error.stack,
        });
      }
    });
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Report to default telemetry layer, then delegate to user-provided callback
    reportClientError({
      type: 'react',
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack ?? undefined,
    });
    
    const onReport = makeErrorReporter(this.props.onError);
    onReport(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center rounded-lg border border-destructive/50 bg-destructive/5 p-8 text-center">
          <div className="mb-4 text-destructive">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="40"
              height="40"
              viewBox="0 0 24: 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Something went wrong
          </h3>
          <p className="text-sm text-muted-foreground mb-4 max-w-md">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <Button variant="outline" onClick={this.handleReset}>
            Try again
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
