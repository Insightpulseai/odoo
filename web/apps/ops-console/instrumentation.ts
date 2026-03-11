/**
 * Next.js OpenTelemetry instrumentation entry point.
 *
 * Registers @vercel/otel for distributed tracing on Vercel.
 * Auto-configures to Vercel Observability when deployed; no OTLP endpoint needed.
 */
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { registerOTel } = await import('@vercel/otel')
    registerOTel({ serviceName: 'odooops-console' })
  }
}
