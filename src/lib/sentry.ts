import * as Sentry from "@sentry/react";

export function initializeSentry() {
  const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;

  if (SENTRY_DSN) {
    Sentry.init({
      dsn: SENTRY_DSN,
      integrations: [
        // Default integrations
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          // Additional privacy settings
          maskAllText: true,
          blockAllMedia: true,
        }),
      ],
      // Performance Monitoring
      tracesSampleRate: 1.0,
      // Session Replay
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
      
      // Ensure environment is set
      environment: import.meta.env.MODE || 'development',
    });
    console.log("✅ Sentry monitoring initialized.");
  } else {
    console.warn("⚠️ SENTRY_DSN not found. Sentry monitoring is disabled.");
  }
}

