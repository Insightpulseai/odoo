"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GitBranch,
  Package,
  FileText,
  Terminal,
  Database,
  Key,
  Users,
  HardDrive,
  Gauge,
  Archive,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Tab {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface ProjectTabsProps {
  projectId: string;
}

export function ProjectTabs({ projectId }: ProjectTabsProps) {
  const pathname = usePathname();

  const tabs: Tab[] = [
    {
      name: "Overview",
      href: `/app/projects/${projectId}`,
      icon: LayoutDashboard,
    },
    {
      name: "Branches",
      href: `/app/projects/${projectId}/branches`,
      icon: GitBranch,
    },
    {
      name: "Builds",
      href: `/app/projects/${projectId}/builds`,
      icon: Package,
    },
    {
      name: "Logs",
      href: `/app/projects/${projectId}/logs`,
      icon: FileText,
    },
    {
      name: "Shell",
      href: `/app/projects/${projectId}/shell`,
      icon: Terminal,
    },
    {
      name: "Database",
      href: `/app/projects/${projectId}/database`,
      icon: Database,
    },
    {
      name: "Secrets",
      href: `/app/projects/${projectId}/secrets`,
      icon: Key,
    },
    {
      name: "Auth",
      href: `/app/projects/${projectId}/auth`,
      icon: Users,
    },
    {
      name: "Storage",
      href: `/app/projects/${projectId}/storage`,
      icon: HardDrive,
    },
    {
      name: "Performance",
      href: `/app/projects/${projectId}/performance`,
      icon: Gauge,
    },
    {
      name: "Backups",
      href: `/app/projects/${projectId}/backups`,
      icon: Archive,
    },
    {
      name: "Settings",
      href: `/app/projects/${projectId}/settings`,
      icon: Settings,
    },
  ];

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
      {/* Desktop: Horizontal Tabs */}
      <div className="hidden md:block">
        <nav className="flex space-x-1 px-4 overflow-x-auto" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = pathname === tab.href;

            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
                  isActive
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300"
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Mobile: Horizontal Scroll */}
      <div className="md:hidden">
        <nav
          className="flex space-x-1 px-2 py-2 overflow-x-auto"
          aria-label="Tabs"
        >
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = pathname === tab.href;

            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "flex flex-col items-center justify-center min-w-[72px] px-3 py-2 text-xs font-medium rounded-md transition-colors",
                  isActive
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                    : "text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-800"
                )}
              >
                <Icon className="h-5 w-5 mb-1" />
                <span className="text-[10px] leading-tight text-center">
                  {tab.name}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
