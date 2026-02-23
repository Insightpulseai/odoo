'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Database, GitBranch, ScrollText, ArrowUpRight, Construction } from 'lucide-react'

// Management API client (server-side via /api/supabase-proxy)
// import { client } from '@/lib/management-api'
// Usage: const { data } = await client.GET('/v1/projects')
// See: docs/ops/SUPABASE_PLATFORM_KIT.md

interface SectionProps {
  icon: React.ElementType
  title: string
  description: string
  badge?: string
  surfaces: string[]
  docsHref: string
}

function SurfaceCard({ icon: Icon, title, description, badge, surfaces, docsHref }: SectionProps) {
  return (
    <Card className="border-dashed border-muted-foreground/30">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <Icon className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                {title}
                <Badge variant="outline" className="text-[10px] font-mono">
                  scaffold
                </Badge>
              </CardTitle>
              <CardDescription className="text-xs mt-0.5">{description}</CardDescription>
            </div>
          </div>
          {badge && (
            <Badge variant="secondary" className="text-[10px] shrink-0">
              {badge}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2 text-xs text-amber-500 bg-amber-500/10 border border-amber-500/20 rounded-md px-3 py-2">
          <Construction className="h-3.5 w-3.5 shrink-0" />
          <span>Implementation in progress — data plumbing established, UI coming.</span>
        </div>
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">Will surface:</p>
          <ul className="space-y-1">
            {surfaces.map((s) => (
              <li key={s} className="text-xs text-muted-foreground flex items-start gap-1.5">
                <span className="mt-1.5 h-1 w-1 rounded-full bg-muted-foreground/50 shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        </div>
        <Button variant="ghost" size="sm" className="h-7 text-xs px-2" asChild>
          <a href={docsHref} target="_blank" rel="noopener noreferrer">
            Runbook <ArrowUpRight className="ml-1 h-3 w-3" />
          </a>
        </Button>
      </CardContent>
    </Card>
  )
}

export default function PlatformPage() {
  return (
    <div className="space-y-8 animate-in zoom-in-95 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Supabase Platform</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Management API control plane — projects, branches, logs, security.
          </p>
        </div>
        <Badge variant="outline" className="text-xs font-mono hidden md:flex">
          /api/supabase-proxy → api.supabase.com
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
        <SurfaceCard
          icon={Database}
          title="Projects"
          description="List and inspect all Supabase projects in the org."
          badge="GET /v1/projects"
          surfaces={[
            'Project name, region, status (active / inactive)',
            'Health check: DB, Auth, Storage, Edge Functions',
            'Create new project (internal org only)',
          ]}
          docsHref="/docs/ops/SUPABASE_PLATFORM_KIT.md"
        />

        <SurfaceCard
          icon={GitBranch}
          title="Branches"
          description="DEV branch lifecycle: create, migrate, merge to production."
          badge="DEV → prod"
          surfaces={[
            'List active DEV branches per project',
            'Create DEV branch from production snapshot',
            'Run schema migrations against DEV branch',
            'Merge DEV branch into production DB',
            'Delete branch after merge or abandon',
          ]}
          docsHref="/docs/ops/SUPABASE_PLATFORM_KIT.md"
        />

        <SurfaceCard
          icon={ScrollText}
          title="Logs & Security"
          description="Management API log queries and security advisor."
          badge="advisor + PITR"
          surfaces={[
            'Structured log queries (service, level, time range)',
            'Security advisor findings (RLS gaps, exposed functions)',
            'PITR restore trigger (disaster recovery only)',
          ]}
          docsHref="/docs/ops/SUPABASE_PLATFORM_KIT.md"
        />
      </div>
    </div>
  )
}
