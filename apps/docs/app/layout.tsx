import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'OdooOps Platform Docs',
  description: 'Generated from Runtime SSOT',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex min-h-screen">
            {/* Sidebar Placeholder - Real impl would read from docs.manifest.yaml */}
            <aside className="w-64 bg-gray-50 border-r p-4 hidden md:block">
                <div className="font-bold mb-4">OdooOps Platform</div>
                <nav className="space-y-2 text-sm">
                    <div><a href="/overview" className="block p-2 hover:bg-gray-200 rounded">Overview</a></div>
                    <div><a href="/apps" className="block p-2 hover:bg-gray-200 rounded">Apps</a></div>
                    <div><a href="/reference" className="block p-2 hover:bg-gray-200 rounded">Reference</a></div>
                </nav>
            </aside>
            <main className="flex-1 p-8">
                {children}
            </main>
        </div>
      </body>
    </html>
  )
}
