import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { Toaster } from "sonner"
import { LayoutDashboard, Server, ShieldCheck, History, Settings, Bell, Search, User } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "OdooOps | Insightpulseai",
  description: "Enterprise Odoo Platform Operations",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn(inter.className, "dark")} suppressHydrationWarning>
        <Providers>
          <div className="flex min-h-screen bg-transparent">
            {/* Sidebar */}
            <aside className="w-64 glass border-r border-white/5 flex flex-col fixed inset-y-0 left-0 z-50">
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
                    <LayoutDashboard className="h-5 w-5 text-white" />
                  </div>
                  <span className="text-xl font-bold tracking-tight text-gradient">OdooOps</span>
                </div>

                <nav className="space-y-1">
                  <SidebarLink href="/" icon={LayoutDashboard} label="Overview" active />
                  <SidebarLink href="/environments" icon={Server} label="Environments" />
                  <SidebarLink href="/gates" icon={ShieldCheck} label="Policy Gates" />
                  <SidebarLink href="/deployments" icon={History} label="Deployments" />
                  <SidebarLink href="/settings" icon={Settings} label="Settings" />
                </nav>
              </div>

              <div className="mt-auto p-6 border-t border-white/5">
                <div className="flex items-center space-x-3 p-2 rounded-lg bg-white/5">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 shadow-lg shadow-purple-500/20" />
                  <div>
                    <div className="text-xs font-semibold">TBWA Ops</div>
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Maintainer</div>
                  </div>
                </div>
              </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 ml-64 min-h-screen">
              {/* Top Bar */}
              <header className="h-16 glass border-b border-white/5 flex items-center justify-between px-8 sticky top-0 z-40">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="relative max-w-md w-full">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Search infra, modules, logs..."
                      className="w-full bg-white/5 border border-white/5 rounded-full py-2 pl-10 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-primary/50 transition-all font-medium"
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-6">
                  <button className="relative text-muted-foreground hover:text-white transition-colors">
                    <Bell className="h-4 w-4" />
                    <span className="absolute -top-1 -right-1 h-2 w-2 bg-primary rounded-full border border-background" />
                  </button>
                  <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center border border-white/5 hover:border-white/20 transition-all cursor-pointer">
                    <User className="h-4 w-4" />
                  </div>
                </div>
              </header>

              <div className="p-8 pb-20 overflow-x-hidden">
                {children}
              </div>
            </main>
          </div>
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  )
}

function SidebarLink({ href, icon: Icon, label, active = false }: { href: string, icon: any, label: string, active?: boolean }) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 group",
        active
          ? "bg-primary text-white shadow-lg shadow-primary/20"
          : "text-muted-foreground hover:bg-white/5 hover:text-white"
      )}
    >
      <Icon className={cn("h-4 w-4", !active && "group-hover:scale-110 transition-transform")} />
      <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
    </Link>
  )
}
