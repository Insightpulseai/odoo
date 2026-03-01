"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Server,
  ShieldCheck,
  History,
  Settings,
  Database,
  Eye,
  Package,
  BookOpen,
  Sparkles,
  ChevronRight,
  Menu,
  X,
  BarChart3,
  Cpu,
  Plug,
  HardDrive,
  Hammer,
  FileText,
  Bot,
  Globe,
  Layers,
  MonitorDot,
  FileCode2,
  SearchCode,
  HardHat,
  Paintbrush,
  KeyRound,
} from "lucide-react"
import { useState, useCallback, useEffect } from "react"

type NavSection = {
  label: string
  items: NavItem[]
}

type NavItem = {
  href: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  badge?: string
}

const navSections: NavSection[] = [
  {
    label: "Operations",
    items: [
      { href: "/", icon: LayoutDashboard, label: "Overview" },
      { href: "/environments", icon: Server, label: "Environments" },
      { href: "/deployments", icon: History, label: "Deployments" },
      { href: "/builds", icon: Hammer, label: "Builds", badge: "New" },
      { href: "/logs", icon: FileText, label: "Logs" },
      { href: "/gates", icon: ShieldCheck, label: "Policy Gates" },
    ],
  },
  {
    label: "Platform",
    items: [
      { href: "/database", icon: Database, label: "Database" },
      { href: "/backups", icon: HardDrive, label: "Backups", badge: "New" },
      { href: "/platform", icon: Cpu, label: "Control Plane" },
      { href: "/platform/secrets", icon: KeyRound, label: "Secrets" },
      { href: "/modules", icon: Package, label: "Modules" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { href: "/advisor", icon: Sparkles, label: "Advisor" },
      { href: "/observability", icon: Eye, label: "Observability" },
      { href: "/metrics", icon: BarChart3, label: "Metrics" },
    ],
  },
  {
    label: "Resources",
    items: [
      { href: "/integrations", icon: Plug, label: "Integrations" },
      { href: "/runbooks", icon: BookOpen, label: "Runbooks" },
      { href: "/settings", icon: Settings, label: "Settings" },
    ],
  },
  {
    label: "Explore",
    items: [
      { href: "/use-cases/ai-apps", icon: Bot, label: "AI Apps" },
      { href: "/use-cases/marketing-sites", icon: Globe, label: "Marketing Sites" },
      { href: "/use-cases/multi-tenant-platforms", icon: Layers, label: "Multi-Tenant" },
      { href: "/use-cases/web-apps", icon: MonitorDot, label: "Web Apps" },
      { href: "/tools/templates", icon: FileCode2, label: "Templates" },
      { href: "/tools/partner-finder", icon: SearchCode, label: "Partner Finder" },
      { href: "/users/platform-engineers", icon: HardHat, label: "Platform Engineers" },
      { href: "/users/design-engineers", icon: Paintbrush, label: "Design Engineers" },
    ],
  },
]

function isRouteActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/"
  return pathname === href || pathname.startsWith(href + "/")
}

function SidebarLink({
  href,
  icon: Icon,
  label,
  active = false,
  badge,
  collapsed = false,
  onClick,
}: {
  href: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  active?: boolean
  badge?: string
  collapsed?: boolean
  onClick?: () => void
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        "flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative",
        active
          ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
          : "text-muted-foreground hover:bg-black/5 hover:text-foreground"
      )}
    >
      <Icon
        className={cn(
          "h-4 w-4 shrink-0",
          !active && "group-hover:scale-110 transition-transform"
        )}
      />
      {!collapsed && (
        <>
          <span className="text-xs font-semibold uppercase tracking-wider truncate">
            {label}
          </span>
          {badge && (
            <span className="ml-auto text-[9px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/30">
              {badge}
            </span>
          )}
          {active && (
            <ChevronRight className="ml-auto h-3 w-3 opacity-60" />
          )}
        </>
      )}
    </Link>
  )
}

export function Sidebar() {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)

  const closeMobile = useCallback(() => setMobileOpen(false), [])

  // Close mobile nav on route change
  useEffect(() => {
    setMobileOpen(false)
  }, [pathname])

  // Prevent body scroll when mobile nav is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }
    return () => {
      document.body.style.overflow = ""
    }
  }, [mobileOpen])

  const sidebarContent = (
    <>
      <div className="p-6">
        <div className="flex items-center space-x-3 mb-8">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <LayoutDashboard className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-gradient">
            OdooOps
          </span>
        </div>

        <nav className="space-y-6">
          {navSections.map((section) => (
            <div key={section.label}>
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground/50 px-3 mb-2">
                {section.label}
              </div>
              <div className="space-y-0.5">
                {section.items.map((item) => (
                  <SidebarLink
                    key={item.href}
                    href={item.href}
                    icon={item.icon}
                    label={item.label}
                    badge={item.badge}
                    active={isRouteActive(pathname, item.href)}
                    onClick={closeMobile}
                  />
                ))}
              </div>
            </div>
          ))}
        </nav>
      </div>

      <div className="mt-auto p-6 border-t border-border">
        <div className="flex items-center space-x-3 p-2 rounded-lg bg-black/5">
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 shadow-lg shadow-purple-500/20" />
          <div>
            <div className="text-xs font-semibold">TBWA Ops</div>
            <div className="text-[10px] text-muted-foreground uppercase tracking-wider">
              Maintainer
            </div>
          </div>
        </div>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed top-4 left-4 z-[60] lg:hidden p-2 rounded-lg glass border border-border"
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] lg:hidden"
          onClick={closeMobile}
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-[70] w-64 glass border-r border-border flex flex-col transition-transform duration-300 lg:hidden",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <button
          onClick={closeMobile}
          className="absolute top-4 right-4 p-1 rounded-lg hover:bg-black/10 transition-colors"
          aria-label="Close navigation"
        >
          <X className="h-4 w-4" />
        </button>
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-64 glass border-r border-border flex-col fixed inset-y-0 left-0 z-50">
        {sidebarContent}
      </aside>
    </>
  )
}
