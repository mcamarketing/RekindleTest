import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // In production, you might want to log this to an error reporting service
    // Example: logErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-[#1A1F2E] flex items-center justify-center p-4">
          <div className="max-w-2xl w-full glass-card p-8 border-2 border-red-500/30">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-4 bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl shadow-2xl">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-2">
                  Something Went Wrong
                </h1>
                <p className="text-lg text-gray-400">
                  We encountered an unexpected error. Please try again or contact support if the problem persists.
                </p>
              </div>
            </div>

            {/* Error Details (only in development) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <h2 className="text-sm font-bold text-red-400 uppercase tracking-wider mb-2">
                  Error Details (Development Only)
                </h2>
                <pre className="text-xs text-red-300 overflow-auto max-h-40">
                  {this.state.error.toString()}
                  {this.state.errorInfo && (
                    <>
                      {'\n\n'}
                      {this.state.errorInfo.componentStack}
                    </>
                  )}
                </pre>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={this.handleReset}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-xl shadow-lg hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 active:scale-95 transition-all duration-300"
              >
                Try Again
              </button>
              <button
                onClick={() => {
                  window.location.href = '/';
                }}
                className="px-6 py-3 glass-card glass-card-hover text-white font-bold rounded-xl border border-white/10 hover:border-[#FF6B35]/50 transition-all"
              >
                Go Home
              </button>
            </div>

            {/* Support Link */}
            <div className="mt-6 pt-6 border-t border-white/10">
              <p className="text-sm text-gray-400 text-center">
                Need help?{' '}
                <a
                  href="mailto:support@rekindle.com"
                  className="text-[#FF6B35] hover:text-[#F7931E] font-bold transition-colors"
                >
                  Contact Support
                </a>
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
