import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { opsQueries } from '@/lib/supabase-ops';

export const dynamic = 'force-dynamic';

async function getPlatformData() {
  try {
    const projects = await opsQueries.getAllProjects();
    
    // Get run counts for last 24h
    const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    
    const runCounts = await Promise.all(
      projects.map(async (project) => {
        const runs = await opsQueries.getRunsByProject(project.project_id, 100);
        const recentRuns = runs.filter(r => r.created_at > twentyFourHoursAgo);
        const successRuns = recentRuns.filter(r => r.status === 'success').length;
        const failedRuns = recentRuns.filter(r => r.status === 'failed').length;
        const runningRuns = recentRuns.filter(r => r.status === 'running').length;
        
        return {
          projectId: project.project_id,
          total: recentRuns.length,
          success: successRuns,
          failed: failedRuns,
          running: runningRuns
        };
      })
    );

    return { projects, runCounts };
  } catch (error) {
    console.error('Failed to fetch platform data:', error);
    return { projects: [], runCounts: [] };
  }
}

export default async function PlatformPage() {
  const { projects, runCounts } = await getPlatformData();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">InsightPulse Control Plane</h1>
            <p className="text-muted-foreground mt-2">
              Odoo.sh-equivalent platform for managing CE 19 instances
            </p>
          </div>
          <Button asChild>
            <Link href="/platform/new">+ New Project</Link>
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => {
            const runStats = runCounts.find(r => r.projectId === project.project_id);
            
            return (
              <Link
                key={project.project_id}
                href={`/platform/${project.project_id}`}
                className="block group"
              >
                <Card className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="group-hover:text-primary transition-colors">
                          {project.name}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          {project.repo_slug}
                        </CardDescription>
                      </div>
                      <Badge variant="outline">{project.odoo_version}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Last 24h:</span>
                        <span className="font-medium">{runStats?.total || 0} runs</span>
                      </div>
                      
                      {runStats && runStats.total > 0 && (
                        <div className="flex gap-2">
                          {runStats.success > 0 && (
                            <Badge variant="success" className="text-xs">
                              ✓ {runStats.success}
                            </Badge>
                          )}
                          {runStats.failed > 0 && (
                            <Badge variant="destructive" className="text-xs">
                              ✗ {runStats.failed}
                            </Badge>
                          )}
                          {runStats.running > 0 && (
                            <Badge variant="warning" className="text-xs">
                              ⏳ {runStats.running}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}

          {projects.length === 0 && (
            <Card className="col-span-full">
              <CardHeader>
                <CardTitle>No projects yet</CardTitle>
                <CardDescription>
                  Create your first Odoo project to get started
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild>
                  <Link href="/platform/new">Create Project</Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="mt-12 border-t pt-8">
          <h2 className="text-2xl font-semibold mb-4">Quick Links</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Link href="/api/bugbot" className="block">
              <Card className="hover:bg-accent transition-colors">
                <CardHeader>
                  <CardTitle className="text-lg">BugBot API</CardTitle>
                  <CardDescription>AI-powered bug analysis</CardDescription>
                </CardHeader>
              </Card>
            </Link>
            <Link href="/api/vercel-bot" className="block">
              <Card className="hover:bg-accent transition-colors">
                <CardHeader>
                  <CardTitle className="text-lg">Vercel Bot API</CardTitle>
                  <CardDescription>Deployment automation</CardDescription>
                </CardHeader>
              </Card>
            </Link>
            <Link href="/api/control-plane" className="block">
              <Card className="hover:bg-accent transition-colors">
                <CardHeader>
                  <CardTitle className="text-lg">Control Plane API</CardTitle>
                  <CardDescription>Platform orchestration</CardDescription>
                </CardHeader>
              </Card>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
