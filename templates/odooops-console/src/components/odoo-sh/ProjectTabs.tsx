"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface ProjectTabsProps {
  projectId: string;
}

const tabs = [
  { id: "branches", label: "Branches" },
  { id: "builds", label: "Builds" },
  { id: "backups", label: "Backups" },
  { id: "upgrade", label: "Upgrade" },
  { id: "settings", label: "Settings" },
  { id: "monitor", label: "Monitor" },
] as const;

export function ProjectTabs({ projectId }: ProjectTabsProps) {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="flex space-x-8 px-6">
        {tabs.map((tab) => {
          const href = `/app/projects/${projectId}/${tab.id}`;
          const isActive = pathname === href || pathname.startsWith(`${href}/`);

          return (
            <Link
              key={tab.id}
              href={href}
              className={`
                border-b-2 py-4 px-1 text-sm font-medium
                ${
                  isActive
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                }
              `}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
