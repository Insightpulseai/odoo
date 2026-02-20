import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { opsQueries } from '@/lib/supabase-ops';
import { ExternalLink, PlayCircle, Terminal, FileText } from 'lucide-react';

export const dynamic = 'force-dynamic';

interface PageProps {
  params: {
    project_id: string;
  };
}

async function getProjectDetail(projectId: string) {
  try {
    const [project, environments, runs] = await Promise.all([
      opsQueries.getProject(projectId),
      opsQueries.getEnvironmentsByProject(projectId),
      opsQueries.getRunsByProject(projectId, 10)
    ]);

    const envRuns = await Promise.all(
      environments.map(async (env) => {
        const envRuns = await opsQueries.getRunsByEnvironment(env.env_id, 1);
        return { env, latestRun: envRuns[0] || null };
      })
    );

    return { project, environments: envRuns, runs };
  } catch (error) {
    console.error('Failed to fetch project detail:', error);
    throw error;
  }
}

function getStatusBadge(status: string) {
  const variants: Record<string, { variant: any; label: string }> = {
    success: { variant: 'success', label: '✅ Live' },
    running: { variant: 'warning', label: '🔄 Building' },
    failed: { variant: 'destructive', label: '❌ Failed' },
    queued: { variant: 'outline', label: '⏳ Queued' }
  };

  const config = variants[status] || variants.queued;
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
  return `${Math.floor(minutes / 1440)}d ago`;
}

export default async function ProjectDetailPage({ params }: PageProps) {
  const { project, environments, runs } = await getProjectDetail(params.project_id);

  const sortedEnvs = environments.sort((a, b) => {
    const order = { dev: 0, staging: 1, prod: 2 };
    return order[a.env.env_type as keyof typeof order] - order[b.env.env_type as keyof typeof order];
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/platform" className="text-muted-foreground hover:text-foreground">
            ← Back
          </Link>
          <div className="flex-1">
            <h1 className="text-4xl font-bold tracking-tight">{project.name}</h1>
            <p className="text-muted-foreground mt-1">
              {project.repo_slug} • Odoo {project.odoo_version}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link href={`https://github.com/${project.repo_slug}`} target="_blank">
                <ExternalLink className="mr-2 h-4 w-4" />
                GitHub
              </Link>
            </Button>
            <Button>Actions</Button>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3 mb-12">
          {sortedEnvs.map(({ env, latestRun }) => (
            <Card key={env.env_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg uppercase">
                    {env.env_type}
                  </CardTitle>
                  {latestRun && getStatusBadge(latestRun.status)}
                </div>
                <CardDescription>{env.branch_pattern}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {latestRun ? (
                  <>
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">Last Deploy</div>
                      <div className="text-sm font-mono truncate" title={latestRun.git_sha}>
                        {latestRun.git_sha.substring(0, 7)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatTime(latestRun.created_at)}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <Button variant="outline" size="sm" asChild className="w-full justify-start">
                        <Link href={`/platform/runs/${latestRun.run_id}`}>
                          <PlayCircle className="mr-2 h-4 w-4" />
                          View Run
                        </Link>
                      </Button>
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <Terminal className="mr-2 h-4 w-4" />
                        Shell
                      </Button>
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <FileText className="mr-2 h-4 w-4" />
                        Logs
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="text-sm text-muted-foreground py-4 text-center">
                    No deployments yet
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Runs</CardTitle>
            <CardDescription>Last 10 deployments across all environments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {runs.map((run) => {
                const env = environments.find(e => e.env.env_id === run.env_id)?.env;
                
                return (
                  <Link
                    key={run.run_id}
                    href={`/platform/runs/${run.run_id}`}
                    className="block hover:bg-accent/50 rounded-lg p-4 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        {getStatusBadge(run.status)}
                        <div>
                          <div className="font-medium font-mono text-sm">
                            {run.git_sha.substring(0, 7)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {run.git_ref} • {env?.env_type}
                          </div>
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {formatTime(run.created_at)}
                      </div>
                    </div>
                  </Link>
                );
              })}

              {runs.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No runs yet
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
