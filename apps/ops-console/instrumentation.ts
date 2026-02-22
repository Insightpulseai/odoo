/**
 * Next.js OpenTelemetry instrumentation entry point.
 *
 * This file is loaded automatically by Next.js before the app starts.
 * Tracing is disabled by default. To enable:
 *
 *   1. Install @vercel/otel:
 *        npm install @vercel/otel
 *
 *   2. Set the following environment variable (Vercel or .env.local):
 *        OTEL_EXPORTER_OTLP_ENDPOINT=https://your-otel-collector/v1/traces
 *
 *   3. Uncomment the body below.
 */
export async function register() {
  if (
    process.env.NEXT_RUNTIME === 'nodejs' &&
    process.env.OTEL_EXPORTER_OTLP_ENDPOINT
  ) {
    // Uncomment when @vercel/otel is installed:
    // const { registerOTel } = await import('@vercel/otel')
    // registerOTel({ serviceName: 'odooops-console' })
    //
    // Until then, log a reminder so it's visible in build logs.
    console.warn(
      '[instrumentation] OTEL_EXPORTER_OTLP_ENDPOINT is set but @vercel/otel is not installed. ' +
        'Install it to enable distributed tracing.'
    )
  }
}
