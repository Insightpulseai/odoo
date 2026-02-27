import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { Toaster } from "sonner"
import { Bell, Search, User } from "lucide-react"
import "@/lib/datasource/guard"
import { DataSourceBadge } from "@/components/platform/DataSourceBadge"
import { Sidebar } from "@/components/navigation/sidebar"
import { cn } from "@/lib/utils"
import { Analytics } from "@vercel/analytics/react"
import { SpeedInsights } from "@vercel/speed-insights/next"

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
            <Sidebar />

            {/* Main Content */}
            <main className="flex-1 lg:ml-64 min-h-screen">
              {/* Top Bar */}
              <header className="h-16 glass border-b border-white/5 flex items-center justify-between px-4 lg:px-8 sticky top-0 z-40">
                <div className="flex items-center space-x-4 flex-1 ml-12 lg:ml-0">
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

              <div className="p-4 lg:p-8 pb-20 overflow-x-hidden">
                {children}
              </div>
            </main>
          </div>
          <Toaster richColors position="top-right" />
          <DataSourceBadge />
          <Analytics />
          <SpeedInsights />
        </Providers>
      </body>
    </html>
  )
}
