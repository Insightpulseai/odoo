import Link from "next/link";
import { ProjectTabs } from "@/components/odoo-sh/ProjectTabs";

export default function ProjectLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { projectId: string };
}) {
  // TODO: Fetch project from Supabase (ops.projects table)
  const projectName = "Production ERP"; // Placeholder

  return (
    <div>
      {/* Breadcrumbs */}
      <div className="border-b border-gray-200 bg-gray-50 px-6 py-3">
        <nav className="flex" aria-label="Breadcrumb">
          <ol className="flex items-center space-x-2 text-sm">
            <li>
              <Link
                href="/app/projects"
                className="text-gray-500 hover:text-gray-700"
              >
                Projects
              </Link>
            </li>
            <li>
              <span className="text-gray-400">/</span>
            </li>
            <li>
              <span className="font-medium text-gray-900">{projectName}</span>
            </li>
          </ol>
        </nav>
      </div>

      {/* Project tabs */}
      <ProjectTabs projectId={params.projectId} />

      {/* Tab content */}
      <div>{children}</div>
    </div>
  );
}
