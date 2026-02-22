import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Activity, ExternalLink, Lock, AlertTriangle } from 'lucide-react'

// Project ref is non-secret (NEXT_PUBLIC_*); safe in server component
const PROJECT_REF = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF ?? ''
const GRAFANA_URL = process.env.GRAFANA_DASHBOARD_URL ?? ''

export default function MetricsPage() {
  const scrapeEndpoint = PROJECT_REF
    ? `https://${PROJECT_REF}.supabase.co/customer/v1/privileged/metrics`
    : null

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in zoom-in-95 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Metrics</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Prometheus-compatible metrics via Supabase Metrics API.
          </p>
        </div>
        {GRAFANA_URL && (
          <Button variant="outline" size="sm" asChild>
            <a href={GRAFANA_URL} target="_blank" rel="noopener noreferrer">
              Open Grafana <ExternalLink className="ml-2 h-3.5 w-3.5" />
            </a>
          </Button>
        )}
      </div>

      {/* Scrape endpoint info (non-secret) */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Scrape Endpoint
          </CardTitle>
          <CardDescription>
            Prometheus scrape target. Auth is HTTP Basic (service_role / sb_secret_...) — configured
            in your Prometheus/Grafana Agent config, never exposed here.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {scrapeEndpoint ? (
            <div className="flex items-center justify-between gap-4 bg-muted rounded-md px-4 py-2.5">
              <code className="text-xs font-mono break-all">{scrapeEndpoint}</code>
              <Badge variant="secondary" className="shrink-0 text-[10px]">
                60 s interval
              </Badge>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-xs text-amber-500 bg-amber-500/10 border border-amber-500/20 rounded-md px-3 py-2">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
              <span>
                <code className="font-mono">NEXT_PUBLIC_SUPABASE_PROJECT_REF</code> is not set.
              </span>
            </div>
          )}

          <div className="flex items-start gap-2 text-xs text-muted-foreground bg-muted/50 rounded-md px-3 py-2">
            <Lock className="h-3.5 w-3.5 shrink-0 mt-0.5" />
            <span>
              Raw Prometheus metrics are <strong>not proxied through this app</strong>. Metrics flow
              directly from Supabase to your collector (Prometheus / Grafana Agent). This page shows
              the configured endpoint and links to the Grafana dashboard.
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Grafana link or setup guidance */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <ExternalLink className="h-4 w-4" />
            Visualization
          </CardTitle>
          <CardDescription>
            Connect your Prometheus collector to Grafana to view dashboards and set up alerts.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {GRAFANA_URL ? (
            <Button asChild>
              <a href={GRAFANA_URL} target="_blank" rel="noopener noreferrer">
                Open Grafana Dashboard <ExternalLink className="ml-2 h-3.5 w-3.5" />
              </a>
            </Button>
          ) : (
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>No Grafana dashboard configured.</p>
              <p>
                Set <code className="font-mono text-xs bg-muted px-1 py-0.5 rounded">GRAFANA_DASHBOARD_URL</code>{' '}
                in Vercel env vars to enable the link.
              </p>
              <p className="text-xs">
                See{' '}
                <code className="font-mono">docs/ops/SUPABASE_METRICS.md</code> for collector setup
                options (Grafana Cloud, self-hosted Prometheus, Datadog).
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Scrape config reference */}
      <Card className="border-dashed border-muted-foreground/30">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Scrape config template
          </CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-xs font-mono bg-muted rounded-md p-4 overflow-x-auto leading-relaxed">
            {`# infra/observability/supabase/prometheus-scrape.supabase.yml
scrape_configs:
  - job_name: supabase
    scrape_interval: 60s
    metrics_path: /customer/v1/privileged/metrics
    scheme: https
    basic_auth:
      username: service_role
      password_file: /etc/prometheus/secrets/supabase_metrics_password
    static_configs:
      - targets:
          - ${PROJECT_REF || '<project-ref>'}.supabase.co:443`}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}
