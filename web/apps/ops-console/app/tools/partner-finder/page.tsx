import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, Wrench, BookOpen, Users, Construction } from "lucide-react"

export const dynamic = "force-static"

const guides: Array<{
  label: string
  description: string
  alternatives: string[]
  icon: React.ElementType
  learnMoreHref: string
}> = [
  {
    label: "Self-Hosted Alternatives",
    description: "OSS tools that replace paid SaaS vendors — lower cost, full data ownership.",
    icon: Wrench,
    alternatives: [
      "n8n — Zapier / Make alternative (self-hosted automation)",
      "Superset — Tableau / Looker alternative (BI + dashboards)",
      "Odoo CE + OCA — Salesforce / NetSuite alternative (ERP)",
      "Zoho Mail — Mailgun/SendGrid alternative (transactional mail)",
    ],
    learnMoreHref: "/integrations",
  },
  {
    label: "DIY Guides",
    description: "Step-by-step runbooks for setting up vendor alternatives.",
    icon: BookOpen,
    alternatives: [
      "Mail catcher setup (Mailgun relay, Zoho SMTP)",
      "OCR pipeline (PaddleOCR-VL + Supabase Storage)",
      "Auth bridge (Supabase Auth + Odoo LDAP/OIDC)",
      "Backup restore drill (monthly cadence)",
    ],
    learnMoreHref: "/runbooks",
  },
  {
    label: "Vendor Evaluation Matrix",
    description: "Decision framework used in the Integration Catalog Policy.",
    icon: Users,
    alternatives: [
      "1. Supabase primitive (preferred)",
      "2. Supabase partner integration",
      "3. Vercel marketplace integration",
      "4. Custom Edge Function bridge",
    ],
    learnMoreHref: "/integrations",
  },
]

export default function PartnerFinderPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono uppercase tracking-wider">
              Tools
            </Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Partner Finder</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            DIY guides, vendor alternatives, and the integration decision framework.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3">
        {guides.map(({ label, description, alternatives, icon: Icon, learnMoreHref }) => (
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
            <CardContent className="space-y-4">
              <ul className="space-y-1.5">
                {alternatives.map((alt) => (
                  <li key={alt} className="text-xs text-muted-foreground flex items-start gap-1.5">
                    <span className="mt-1.5 h-1 w-1 rounded-full bg-muted-foreground/50 shrink-0" />
                    {alt}
                  </li>
                ))}
              </ul>
              <Button variant="ghost" size="sm" className="h-7 text-xs px-2" asChild>
                <a href={learnMoreHref}>
                  View details <ArrowUpRight className="ml-1 h-3 w-3" />
                </a>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
        <div className="flex items-center gap-2 text-xs text-amber-500">
          <Construction className="h-3.5 w-3.5 shrink-0" />
          <span>
            Interactive partner search — filter by category, cost band, and vendor lock-in score
            coming online. Static guide content is available now.
          </span>
        </div>
      </div>
    </div>
  )
}
