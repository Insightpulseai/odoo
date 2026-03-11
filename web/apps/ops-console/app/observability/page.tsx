'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Server, BarChart3, ArrowUpRight } from 'lucide-react'

interface ObservabilitySource {
  title: string
  description: string
  badge: string
  href: string
  icon: React.ElementType
  status: 'scaffold' | 'live'
}

const sources: ObservabilitySource[] = [
  {
    title: 'DigitalOcean',
    description: 'Droplet health, CPU/memory/disk metrics, and alert policies for odoo-production.',
    badge: 'DO Monitoring API',
    href: '/observability/digitalocean',
    icon: Server,
    status: 'scaffold',
  },
  {
    title: 'Supabase Metrics',
    description: 'Prometheus-compatible metrics endpoint scrape. See /metrics for scrape config.',
    badge: 'Prometheus',
    href: '/metrics',
    icon: BarChart3,
    status: 'scaffold',
  },
]

export default function ObservabilityPage() {
  return (
    <div className="space-y-8 animate-in zoom-in-95 duration-700">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Observability</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Infrastructure health, metrics, and alerts across the platform.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {sources.map((source) => {
          const Icon = source.icon
          return (
            <Card key={source.title} className="border-dashed border-muted-foreground/30">
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-muted">
                      <Icon className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div>
                      <CardTitle className="text-base flex items-center gap-2">
                        {source.title}
                        {source.status === 'scaffold' && (
                          <Badge variant="outline" className="text-[10px] font-mono">
                            scaffold
                          </Badge>
                        )}
                      </CardTitle>
                      <CardDescription className="text-xs mt-0.5">
                        {source.description}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge variant="secondary" className="text-[10px] shrink-0">
                    {source.badge}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" size="sm" className="h-7 text-xs px-2" asChild>
                  <a href={source.href}>
                    View <ArrowUpRight className="ml-1 h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
