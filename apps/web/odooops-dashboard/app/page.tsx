import { ProjectCard } from "@/components/ProjectCard";
import { MetricCard } from "@/components/MetricCard";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard title="Projects" value="12" trend="+2" />
          <MetricCard title="Deployments" value="48" trend="+8" />
          <MetricCard title="Health Score" value="98%" trend="+1%" />
          <MetricCard title="WAF Score" value="A+" trend="→" />
        </div>

        {/* Projects List */}
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Projects</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProjectCard name="Production ERP" status="healthy" deployments={12} />
          <ProjectCard name="Staging CMS" status="warning" deployments={8} />
          <ProjectCard name="Dev Portal" status="healthy" deployments={24} />
        </div>
      </div>
    </main>
  );
}
