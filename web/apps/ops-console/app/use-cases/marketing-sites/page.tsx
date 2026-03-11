import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, Globe, GitBranch, Radio, Construction } from "lucide-react"
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
    label: "Vercel Deploys",
    href: "/deployments",
    table: "ops.deployments",
    description:
      "Vercel deployment events — production and preview, with git SHA, PR number, and build status.",
    icon: GitBranch,
  },
  {
    label: "Domains",
    href: "/integrations",
    table: "ops.do_droplets",
    description: "Domain and DNS assignments — active subdomains mapped to DO droplets and Vercel.",
    icon: Globe,
  },
  {
    label: "Edge / DNS Drift",
    href: "/gates",
    table: "ops.convergence_findings",
    description:
      "Convergence findings — DNS mismatches, edge config drift, and unresolved deployment gaps.",
    icon: Radio,
  },
]

export default function MarketingSitesPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono uppercase tracking-wider">
              Use Cases
            </Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Marketing Sites</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            Vercel deploys, domain assignments, and edge / DNS drift — Odoo.sh-style for public sites.
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
            Unified Marketing Sites view — consolidated dashboard with live deploy previews and DNS
            status coming online. Data tables are live now.
          </span>
        </div>
      </div>
    </div>
  )
}
