import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, Server, History, HardDrive, Radio, Wrench, Construction } from "lucide-react"
import Link from "next/link"

export const dynamic = "force-static"

const surfaces: Array<{
  label: string
  href: string
  table: string
  description: string
  icon: React.ElementType
}> = [
  {
    label: "Environments",
    href: "/environments",
    table: "ops.do_droplets",
    description: "Prod and stage environment inventory — host, DB, SHA, health, and actions.",
    icon: Server,
  },
  {
    label: "Deployments",
    href: "/deployments",
    table: "ops.deployments",
    description: "Full deployment history with author, status, duration, and rollback controls.",
    icon: History,
  },
  {
    label: "Backups",
    href: "/backups",
    table: "ops.backups",
    description: "Snapshot manifests, backup job runs, and restore drill schedule.",
    icon: HardDrive,
  },
  {
    label: "Convergence Findings",
    href: "/gates",
    table: "ops.convergence_findings",
    description: "Drift signals — merged-but-not-deployed, failed deploys, and unverified checklists.",
    icon: Radio,
  },
  {
    label: "Maintenance",
    href: "/observability",
    table: "ops.maintenance_runs",
    description: "Periodic maintenance chores — cadence, last run, and audit trail.",
    icon: Wrench,
  },
]

export default function PlatformEngineersPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono uppercase tracking-wider">
              Users
            </Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Platform Engineers</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            Environments, deployments, backups, convergence findings, and maintenance — your ops
            command center.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {surfaces.map(({ label, href, table, description, icon: Icon }) => (
          <Card
            key={label}
            className="glass border-border hover:border-primary/30 transition-colors"
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <div className="p-2 rounded-lg bg-muted">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </div>
                {label}
              </CardTitle>
              <CardDescription className="text-xs">
                SSOT: <code className="font-mono">{table}</code>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">{description}</p>
              <Button variant="ghost" size="sm" className="h-7 text-xs px-2" asChild>
                <Link href={href}>
                  Open {label} <ArrowUpRight className="ml-1 h-3 w-3" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
        <div className="flex items-center gap-2 text-xs text-amber-500">
          <Construction className="h-3.5 w-3.5 shrink-0" />
          <span>
            Platform Engineer persona dashboard — combined view with priority alerts and quick-action
            buttons coming online. All linked surfaces are live now.
          </span>
        </div>
      </div>
    </div>
  )
}
