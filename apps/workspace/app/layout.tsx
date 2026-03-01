import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'IPAI Workspace',
  description: 'System of Work — pages, databases, knowledge',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground">
        <div className="flex h-screen">
          <aside className="w-60 border-r border-border bg-muted/30 flex flex-col">
            <div className="px-4 py-3 border-b border-border">
              <span className="font-semibold text-sm">IPAI Workspace</span>
            </div>
            <nav className="flex-1 p-2 space-y-1">
              <a href="/" className="flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent">
                🏠 Home
              </a>
              <a href="/pages" className="flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent">
                📄 Pages
              </a>
              <a href="/databases" className="flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent">
                🗃 Databases
              </a>
              <a href="/search" className="flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent">
                🔍 Search
              </a>
            </nav>
          </aside>
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
