import { NextResponse } from 'next/server';
import { createServerClient, type MCPJobStats } from '@/lib/supabase';

export async function GET() {
  try {
    const supabase = createServerClient();

    // Get job counts by status (last 24 hours)
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const [jobsResult, deadLetterResult, avgDurationResult] = await Promise.all([
      // Jobs by status
      supabase
        .from('jobs')
        .select('status')
        .gte('created_at', oneDayAgo),

      // Dead letter queue count
      supabase
        .from('dead_letter_queue')
        .select('id', { count: 'exact', head: true })
        .eq('resolved', false),

      // Average duration of completed jobs
      supabase
        .from('job_runs')
        .select('duration_ms')
        .eq('status', 'completed')
        .gte('started_at', oneDayAgo)
        .not('duration_ms', 'is', null),
    ]);

    // Calculate counts
    const jobs = jobsResult.data || [];
    const statusCounts = jobs.reduce(
      (acc, job) => {
        acc[job.status] = (acc[job.status] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>
    );

    // Calculate average duration
    const durations = (avgDurationResult.data || []).map((r) => r.duration_ms);
    const avgDurationMs =
      durations.length > 0
        ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
        : 0;

    // Calculate success rate
    const completed = statusCounts['completed'] || 0;
    const failed = statusCounts['failed'] || 0;
    const total = completed + failed;
    const successRate = total > 0 ? Math.round((completed / total) * 100) : 100;

    const stats: MCPJobStats = {
      total: jobs.length,
      queued: statusCounts['queued'] || 0,
      processing: statusCounts['processing'] || 0,
      completed: statusCounts['completed'] || 0,
      failed: statusCounts['failed'] || 0,
      deadLetter: deadLetterResult.count || 0,
      avgDurationMs,
      successRate,
    };

    return NextResponse.json(stats);
  } catch (error) {
    console.error('MCP Jobs Stats API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
