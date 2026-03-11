"use client"

import Link from "next/link"
import { ArrowLeft, ClipboardList, Smartphone } from "lucide-react"

const WORKBOOKS = [
  {
    id: "mobile",
    href: "/advisor/workbooks/mobile",
    icon: Smartphone,
    title: "Mobile Release Readiness",
    description: "iOS App Store submission checklist — build, privacy labels, TestFlight groups, crash-free rate.",
    status: "available",
    tags: ["ios", "app-store", "fastlane"],
  },
]

export default function WorkbooksPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/advisor" className="text-muted-foreground hover:text-white transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h2 className="text-2xl font-bold">Workbooks</h2>
        <span className="text-xs text-muted-foreground">{WORKBOOKS.length} available</span>
      </div>

      <p className="text-sm text-muted-foreground">
        Structured checklists for specific release and compliance scenarios.
        Each workbook evaluates a dedicated ruleset and presents pass/fail status
        with remediation guidance.
      </p>

      <div className="grid gap-4">
        {WORKBOOKS.map(({ id, href, icon: Icon, title, description, status, tags }) => (
          <Link
            key={id}
            href={href}
            className="glass border border-white/5 rounded-xl p-5 hover:border-white/20 transition-all group"
          >
            <div className="flex items-start gap-4">
              <div className="h-10 w-10 rounded-lg bg-white/5 flex items-center justify-center shrink-0 group-hover:bg-white/10 transition-colors">
                <Icon className="h-5 w-5 text-muted-foreground group-hover:text-white transition-colors" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-semibold">{title}</h3>
                  {status === "available" && (
                    <span className="text-[10px] bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded font-bold">
                      Ready
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{description}</p>
                <div className="flex gap-1.5 mt-2">
                  {tags.map((t) => (
                    <span key={t} className="text-[10px] bg-white/5 text-muted-foreground px-1.5 py-0.5 rounded font-mono">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <ClipboardList className="h-4 w-4 text-muted-foreground shrink-0 group-hover:text-white transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
