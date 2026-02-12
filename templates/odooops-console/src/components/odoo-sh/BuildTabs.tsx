"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface BuildTabsProps {
  projectId: string;
  buildId: string;
}

const tabs = [
  { id: "logs", label: "Logs" },
  { id: "shell", label: "Shell" },
  { id: "editor", label: "Editor" },
  { id: "monitor", label: "Monitor" },
] as const;

export function BuildTabs({ projectId, buildId }: BuildTabsProps) {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="flex space-x-8 px-6">
        {tabs.map((tab) => {
          const href = `/app/projects/${projectId}/builds/${buildId}/${tab.id}`;
          const isActive = pathname === href;

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
