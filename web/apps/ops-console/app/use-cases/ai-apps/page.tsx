import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, Bot, Cpu, FileBox, Construction } from "lucide-react"
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
    label: "Agent Runs",
    href: "/runs",
    table: "ops.runs",
    description: "Task bus run ledger — every agent invocation with status, source, and artifacts.",
    icon: Bot,
  },
  {
    label: "AI Providers",
    href: "/integrations",
    table: "ops.ai_models",
    description: "AI model inventory: provider, model ID, tier, and activation status.",
    icon: Cpu,
  },
  {
    label: "Artifacts",
    href: "/builds",
    table: "ops.advisor_findings",
    description: "Build and run artifacts — logs, summaries, and evidence bundles.",
    icon: FileBox,
  },
]

export default function AiAppsPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono uppercase tracking-wider">
              Use Cases
            </Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">AI Apps</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            Agent runs, AI provider inventory, and build artifacts — all in one view.
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
            Unified AI Apps view — consolidated dashboard coming online. Each card above links to its
            live data table now.
          </span>
        </div>
      </div>
    </div>
  )
}
