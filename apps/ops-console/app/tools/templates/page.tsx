import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, BookOpen, ScrollText, Construction } from "lucide-react"

export const dynamic = "force-static"

const templateCategories: Array<{
  label: string
  description: string
  items: string[]
  icon: React.ElementType
}> = [
  {
    label: "Spec Kit Bundles",
    description: "Reusable spec bundles for feature-driven development.",
    icon: FileText,
    items: [
      "constitution.md — non-negotiable constraints",
      "prd.md — product requirements",
      "plan.md — implementation plan",
      "tasks.md — work breakdown",
    ],
  },
  {
    label: "Runbook Templates",
    description: "Operational runbooks for repeatable platform tasks.",
    icon: BookOpen,
    items: [
      "Promotion checklist",
      "Rollback playbook",
      "Backup restore drill",
      "Key/token rotation",
    ],
  },
  {
    label: "CI / Policy Templates",
    description: "Reusable GitHub Actions workflows and gate policies.",
    icon: ScrollText,
    items: [
      "DNS SSOT guard workflow",
      "OCA allowlist gate",
      "Secret sync audit workflow",
      "Convergence scan workflow",
    ],
  },
]

export default function TemplatesPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono uppercase tracking-wider">
              Tools
            </Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Templates</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            Spec kit bundles, runbook templates, and reusable CI / policy scaffolds.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3">
        {templateCategories.map(({ label, description, items, icon: Icon }) => (
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
              <CardDescription className="text-xs">{description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5">
                {items.map((item) => (
                  <li key={item} className="text-xs text-muted-foreground flex items-start gap-1.5">
                    <span className="mt-1.5 h-1 w-1 rounded-full bg-muted-foreground/50 shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
        <div className="flex items-center gap-2 text-xs text-amber-500">
          <Construction className="h-3.5 w-3.5 shrink-0" />
          <span>
            Template browser — interactive scaffold picker with one-click generation coming online.
            Templates exist today in <code className="font-mono">spec/</code> and{" "}
            <code className="font-mono">.specify/templates/</code>.
          </span>
        </div>
      </div>
    </div>
  )
}
