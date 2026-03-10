import React from 'react';

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar - TODO: Fetch from nav.json */}
      <aside className="w-64 border-r bg-gray-50 hidden md:flex flex-col h-screen sticky top-0">
        <div className="p-4 border-b font-bold text-lg">
          OdooOps Docs
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Platform
          </div>
          <a href="/docs" className="block px-3 py-2 text-sm font-medium text-gray-900 rounded-md hover:bg-gray-100">
            Overview
          </a>

          <div className="mt-6 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Stack
          </div>
          <a href="/docs/stack/runtime" className="block px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-100">
            Runtime Snapshot
          </a>
          <a href="/docs/stack/skills" className="block px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-100">
            Agent Skills
          </a>
        </nav>
      </aside>

      {/* Content Area */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
