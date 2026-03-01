import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, Plug, Eye, Activity, Construction } from "lucide-react"
import Link from "next/link"

export const dynamic = "force-static"

const dataLinks: Array<{
  label: string
  href: string
  table: string
  description: string
  icon: React.ElementType
}> = [
  {
    label: "Integrations",
    href: "/integrations",
    table: "ops.integrations_catalog",
    description:
      "Ops console integration catalog — all provider connections with plan tier and cost band.",
    icon: Plug,
  },
  {
    label: "Monitoring",
    href: "/observability",
    table: "ops.platform_events",
    description:
      "Unified observability — platform event stream, DO droplet health, and mail catcher.",
    icon: Eye,
  },
  {
    label: "Metrics",
    href: "/metrics",
    table: "ops.do_droplets",
    description: "Infrastructure metrics — DO droplet resource usage, uptime, and daily bandwidth.",
    icon: Activity,
  },
]

export default function WebAppsPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono uppercase tracking-wider">
              Use Cases
            </Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Web Apps</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            Ops console integrations, observability streams, and infrastructure monitoring.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3">
        {dataLinks.map(({ label, href, table, description, icon: Icon }) => (
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
            Unified Web Apps view — consolidated dashboard with real-time health and integration
            status coming online. All linked surfaces are live now.
          </span>
        </div>
      </div>
    </div>
  )
}
