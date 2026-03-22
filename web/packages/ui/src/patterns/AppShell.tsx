import type { ReactNode } from "react";

interface NavItem {
  label: string;
  href: string;
}

interface AppShellProps {
  appName: string;
  navItems: NavItem[];
  children: ReactNode;
}

export function AppShell({ appName, navItems, children }: AppShellProps) {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-60 bg-gray-900 text-white flex flex-col">
        <div className="px-4 py-5 border-b border-gray-700">
          <h1 className="text-lg font-semibold">{appName}</h1>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 transition-colors"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="px-4 py-3 border-t border-gray-700 text-xs text-gray-400">
          InsightPulse AI Platform
        </div>
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b bg-white flex items-center px-6">
          <span className="text-sm text-gray-500">{appName}</span>
        </header>
        <main className="flex-1 bg-gray-50 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
