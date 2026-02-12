import Link from "next/link";
import { createSupabaseServerClient } from "@/lib/supabase/server";

function formatRelativeTime(date: string | null): string {
  if (!date) return "Never";
  const ms = Date.now() - new Date(date).getTime();
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(ms / 3600000);
  const days = Math.floor(ms / 86400000);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return "Just now";
}

function getStatusBadge(lastBuildStatus: string | null) {
  if (!lastBuildStatus) return { label: "No builds", className: "bg-gray-100 text-gray-800" };

  switch (lastBuildStatus) {
    case "success":
      return { label: "Healthy", className: "bg-green-100 text-green-800" };
    case "running":
      return { label: "Building", className: "bg-blue-100 text-blue-800" };
    case "failed":
      return { label: "Failed", className: "bg-red-100 text-red-800" };
    case "queued":
      return { label: "Queued", className: "bg-yellow-100 text-yellow-800" };
    default:
      return { label: lastBuildStatus, className: "bg-gray-100 text-gray-800" };
  }
}

export default async function ProjectsPage() {
  const supabase = createSupabaseServerClient();

  const { data: projects, error } = await supabase.rpc("ops.list_projects");

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-red-50 p-4">
          <h3 className="text-sm font-medium text-red-800">Error loading projects</h3>
          <p className="mt-2 text-sm text-red-700">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your Odoo deployments and environments
          </p>
        </div>
        <button className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          New Project
        </button>
      </div>

      {!projects || projects.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <h3 className="text-lg font-medium text-gray-900">No projects yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Get started by creating your first Odoo project.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project: any) => {
            const status = getStatusBadge(project.last_build_status);

            return (
              <Link
                key={project.id}
                href={`/app/projects/${project.id}/branches`}
                className="block rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {project.name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">{project.slug}</p>
                  </div>
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${status.className}`}>
                    {status.label}
                  </span>
                </div>

                <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                  <span>{project.branch_count || 0} branches</span>
                  <span>Last: {formatRelativeTime(project.last_build_at)}</span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
