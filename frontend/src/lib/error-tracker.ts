/**
* Error tracker helper for client-side errors (React ErrorBoundary / unhandled promise rejections).
* Sends collected errors to a local reporting endpoint as baseline; pluggable for Sentry later.
*/

const ERROR_REPORT_URL = '/api/errors/report';

interface ClientErrorPayload {
  type: 'react' | 'unhandled_rejection' | 'unhandled_error';
  message: string;
  stack?: string;
  componentStack?: string;
  url: string;
  timestamp: string;
  userAgent: string;
  environment: string;
}

/** Send an error to the backend (fire-and-forget, survives page unload). */
export async function reportClientError(payload: Omit<ClientErrorPayload, 'url' | 'timestamp' | 'userAgent' | 'environment'>) {
  const body: ClientErrorPayload = {
    ...payload,
    url: typeof window !== 'undefined' ? window.location.href : '',
    environment: process.env.NODE_ENV ?? 'development',
    timestamp: new Date().toISOString(),
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
  };

  // Use navigator.sendBeacon for best reliability on page unload / error states
  if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
    try {
      const blob = new Blob([JSON.stringify(body)], { type: 'application/json' });
      navigator.sendBeacon(ERROR_REPORT_URL, blob);
      return;
    } catch {
      // fall through to fetch fallback
    }
  }

  // Fallback: fire-and-forget fetch with keepalive
  try {
    await fetch(ERROR_REPORT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      keepalive: true,
    });
  } catch {
    // fail-closed: errors are best-effort, we do not throw here
  }
}

/** Default onError handler for ErrorBoundary. Wires React errors into the telemetry layer. */
export function makeErrorReporter(onReport?: (error: Error, errorInfo: React.ErrorInfo) => void) {
  return async function onError(error: Error, errorInfo: React.ErrorInfo) {
    const payload = {
      type: 'react' as const,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack ?? undefined,
    };
    
    if (onReport) {
      onReport(error, errorInfo);
    }
    await reportClientError({ ...payload });
  };
}
