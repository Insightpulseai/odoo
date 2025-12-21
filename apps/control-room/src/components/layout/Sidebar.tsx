'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import {
  LayoutDashboard,
  GitBranch,
  AlertTriangle,
  Lightbulb,
  FolderKanban,
  Settings,
} from 'lucide-react';

const navigation = [
  { name: 'Overview', href: '/overview', icon: LayoutDashboard },
  { name: 'Pipelines', href: '/pipelines', icon: GitBranch },
  { name: 'Data Quality', href: '/data-quality', icon: AlertTriangle },
  { name: 'Advisor', href: '/advisor', icon: Lightbulb },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-surface-900 border-r border-surface-800">
      <div className="flex h-16 items-center gap-3 px-6 border-b border-surface-800">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-500">
          <span className="text-lg font-bold text-white">N</span>
        </div>
        <div>
          <h1 className="text-sm font-semibold text-white">Control Room</h1>
          <p className="text-xs text-surface-200">Notion x Finance PPM</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col p-4">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={clsx(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-500/10 text-primary-400'
                      : 'text-surface-200 hover:bg-surface-800 hover:text-white'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>

        <div className="mt-auto pt-4 border-t border-surface-800">
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-surface-200 hover:bg-surface-800 hover:text-white transition-colors"
          >
            <Settings className="h-5 w-5" />
            Settings
          </Link>
        </div>
      </nav>
    </aside>
  );
}
