'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Server, Cpu, HardDrive, Wifi, Bell, Construction, ArrowUpRight } from 'lucide-react'

// Server-side data plumbing (uncomment when DIGITALOCEAN_API_TOKEN is set):
// import { listDroplets, listAlertPolicies, getDropletMetrics } from '@/lib/do-client'
// See: docs/ops/DIGITALOCEAN_OBSERVABILITY.md

interface MetricCardProps {
  icon: React.ElementType
  label: string
  description: string
  surfaces: string[]
}

function MetricCard({ icon: Icon, label, description, surfaces }: MetricCardProps) {
  return (
    <Card className="border-dashed border-muted-foreground/30">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-muted">
            <Icon className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              {label}
              <Badge variant="outline" className="text-[10px] font-mono">
                scaffold
              </Badge>
            </CardTitle>
            <CardDescription className="text-xs mt-0.5">{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-xs text-amber-500 bg-amber-500/10 border border-amber-500/20 rounded-md px-3 py-2">
          <Construction className="h-3.5 w-3.5 shrink-0" />
          <span>Set DIGITALOCEAN_API_TOKEN to enable live data.</span>
        </div>
        <ul className="space-y-1">
          {surfaces.map((s) => (
            <li key={s} className="text-xs text-muted-foreground flex items-start gap-1.5">
              <span className="mt-1.5 h-1 w-1 rounded-full bg-muted-foreground/50 shrink-0" />
              {s}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

export default function DigitalOceanObservabilityPage() {
  return (
    <div className="space-y-8 animate-in zoom-in-95 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">DigitalOcean</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Droplet health and monitoring for odoo-production (178.128.112.214, SGP1).
          </p>
        </div>
        <Button variant="outline" size="sm" className="text-xs hidden md:flex" asChild>
          <a
            href="https://cloud.digitalocean.com/monitoring"
            target="_blank"
            rel="noopener noreferrer"
          >
            DO Dashboard <ArrowUpRight className="ml-1 h-3 w-3" />
          </a>
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-2">
        <MetricCard
          icon={Server}
          label="Droplets"
          description="odoo-production — status, region, resource spec."
          surfaces={[
            'Droplet name, status (active / off / archive)',
            'Region: SGP1 (Singapore)',
            'vCPUs, memory (GB), disk (GB)',
            'Public IP: 178.128.112.214',
          ]}
        />

        <MetricCard
          icon={Cpu}
          label="CPU & Memory"
          description="Real-time and 1h/6h/24h CPU and memory utilization."
          surfaces={[
            'CPU utilization % (1-minute intervals)',
            'Memory utilization % (1-minute intervals)',
            'Sparkline over last 1h / 6h / 24h',
            'Alert threshold marker',
          ]}
        />

        <MetricCard
          icon={HardDrive}
          label="Disk"
          description="Disk utilization for odoo data, PostgreSQL, and Docker volumes."
          surfaces={[
            'Disk utilization % per mounted volume',
            'I/O read / write rates',
            'Alert at 85% (configurable)',
          ]}
        />

        <MetricCard
          icon={Wifi}
          label="Network"
          description="Outbound bandwidth — Cloudflare origin traffic."
          surfaces={[
            'Public outbound bandwidth (Mbps)',
            'Transfer totals per day',
            'Spike detection vs baseline',
          ]}
        />
      </div>

      <div>
        <MetricCard
          icon={Bell}
          label="Alert Policies"
          description="Active alert policies and trigger state from DO Monitoring API."
          surfaces={[
            'Policy name, type, threshold, window',
            'Enabled / disabled status',
            'Notification channels (email, Slack)',
            'Last triggered timestamp',
          ]}
        />
      </div>
    </div>
  )
}
