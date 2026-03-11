"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

interface BreadcrumbSegment {
  label: string;
  href?: string;
}

export function Breadcrumbs() {
  const pathname = usePathname();

  const generateBreadcrumbs = (): BreadcrumbSegment[] => {
    const segments = pathname.split("/").filter(Boolean);
    const breadcrumbs: BreadcrumbSegment[] = [];

    // Skip if we're at home
    if (segments.length === 0 || pathname === "/") {
      return breadcrumbs;
    }

    // Build breadcrumbs from path segments
    let currentPath = "";
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;

      // Skip "app" segment (route group)
      if (segment === "app") return;

      // Format segment label
      let label = segment
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");

      // Special handling for UUIDs (project IDs)
      if (
        segment.match(
          /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
        )
      ) {
        // Try to fetch project name from context or use shortened ID
        label = `Project ${segment.slice(0, 8)}...`;
      }

      // Don't link the last segment (current page)
      breadcrumbs.push({
        label,
        href: index === segments.length - 1 ? undefined : currentPath,
      });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  // Don't render if no breadcrumbs
  if (breadcrumbs.length === 0) {
    return null;
  }

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
      {/* Home Icon */}
      <Link
        href="/"
        className="flex items-center hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <Home className="h-4 w-4" />
      </Link>

      {/* Breadcrumb Segments */}
      {breadcrumbs.map((crumb, index) => (
        <div key={index} className="flex items-center space-x-2">
          <ChevronRight className="h-4 w-4 flex-shrink-0" />
          {crumb.href ? (
            <Link
              href={crumb.href}
              className="hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="text-gray-900 dark:text-white font-medium">
              {crumb.label}
            </span>
          )}
        </div>
      ))}
    </nav>
  );
}
