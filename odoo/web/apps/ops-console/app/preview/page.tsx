import Link from "next/link"
import { MonitorDot, Palette, Code, Globe, Zap } from "lucide-react"

const previewTargets = [
  {
    id: "components",
    title: "Component Library",
    description: "Browse and preview shadcn/ui components with live props editing",
    icon: Palette,
    status: "ready" as const,
  },
  {
    id: "pages",
    title: "Page Preview",
    description: "Live preview of ops-console pages with diagnostics",
    icon: MonitorDot,
    status: "ready" as const,
  },
  {
    id: "api",
    title: "API Explorer",
    description: "Interactive API endpoint testing and response inspection",
    icon: Code,
    status: "planned" as const,
  },
  {
    id: "public-site",
    title: "Public Site Preview",
    description: "Preview insightpulseai.com landing pages with hot reload",
    icon: Globe,
    status: "planned" as const,
  },
  {
    id: "agent-playground",
    title: "Agent Playground",
    description: "Test Foundry agent interactions with trace visibility",
    icon: Zap,
    status: "planned" as const,
  },
]

export default function PreviewPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Preview Shell</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Fast live-preview with inline diagnostics, error overlays, and console flagging.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {previewTargets.map((target) => {
          const Icon = target.icon
          const isReady = target.status === "ready"

          return isReady ? (
            <Link
              key={target.id}
              href={`/preview/${target.id}`}
              className="group border border-border rounded-lg p-5 hover:border-primary/50 hover:bg-accent/50 transition-all"
            >
              <div className="flex items-start gap-3">
                <Icon className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <h3 className="font-medium text-sm">{target.title}</h3>
                  <p className="text-xs text-muted-foreground mt-1">{target.description}</p>
                </div>
              </div>
            </Link>
          ) : (
            <div
              key={target.id}
              className="border border-border/50 rounded-lg p-5 opacity-50"
            >
              <div className="flex items-start gap-3">
                <Icon className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <h3 className="font-medium text-sm">{target.title}</h3>
                  <p className="text-xs text-muted-foreground mt-1">{target.description}</p>
                  <span className="inline-block mt-2 text-[10px] font-medium uppercase tracking-wider text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                    Planned
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
