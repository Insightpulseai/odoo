'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { OpsRun, OpsRunEvent } from '@/lib/supabase-ops';

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.run_id as string;
  
  const [run, setRun] = useState<OpsRun | null>(null);
  const [events, setEvents] = useState<OpsRunEvent[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let eventSource: EventSource;

    async function fetchRunData() {
      try {
        // Fetch run details
        const runRes = await fetch(`/api/ops/runs/${runId}`);
        if (!runRes.ok) throw new Error('Failed to fetch run');
        const runData = await runRes.json();
        setRun(runData);

        // Fetch initial events
        const eventsRes = await fetch(`/api/ops/runs/${runId}/events`);
        if (!eventsRes.ok) throw new Error('Failed to fetch events');
        const eventsData = await eventsRes.json();
        setEvents(eventsData);
        
        setIsLoading(false);

        // Subscribe to real-time events
        eventSource = new EventSource(`/api/ops/runs/${runId}/stream`);
        
        eventSource.onmessage = (event) => {
          const newEvent: OpsRunEvent = JSON.parse(event.data);
          setEvents(prev => [...prev, newEvent]);
        };

        eventSource.onerror = (error) => {
          console.error('SSE error:', error);
          eventSource.close();
        };

      } catch (error) {
        console.error('Failed to load run data:', error);
        setIsLoading(false);
      }
    }

    fetchRunData();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [runId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground">Loading run details...</div>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-destructive">Failed to load run</div>
      </div>
    );
  }

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.level === filter);

  const statusBadge = {
    success: <Badge variant="success">✅ Success</Badge>,
    running: <Badge variant="warning">🔄 Running</Badge>,
    failed: <Badge variant="destructive">❌ Failed</Badge>,
    queued: <Badge variant="outline">⏳ Queued</Badge>,
    cancelled: <Badge variant="outline">❌ Cancelled</Badge>
  }[run.status] || <Badge>Unknown</Badge>;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href={`/platform/${run.project_id}`} className="text-muted-foreground hover:text-foreground">
            ← Back to Project
          </Link>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-mono">{run.run_id}</CardTitle>
                <CardDescription>
                  {run.git_ref} • {run.git_sha.substring(0, 7)}
                </CardDescription>
              </div>
              {statusBadge}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Queued:</span>{' '}
                {new Date(run.queued_at).toLocaleString()}
              </div>
              {run.started_at && (
                <div>
                  <span className="text-muted-foreground">Started:</span>{' '}
                  {new Date(run.started_at).toLocaleString()}
                </div>
              )}
              {run.finished_at && (
                <div>
                  <span className="text-muted-foreground">Finished:</span>{' '}
                  {new Date(run.finished_at).toLocaleString()}
                </div>
              )}
              {run.claimed_by && (
                <div>
                  <span className="text-muted-foreground">Worker:</span> {run.claimed_by}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Event Log</CardTitle>
                <CardDescription>{filteredEvents.length} events</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={filter === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('all')}
                >
                  All
                </Button>
                <Button
                  variant={filter === 'info' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('info')}
                >
                  Info
                </Button>
                <Button
                  variant={filter === 'warn' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('warn')}
                >
                  Warn
                </Button>
                <Button
                  variant={filter === 'error' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('error')}
                >
                  Error
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-[600px] overflow-y-auto font-mono text-sm">
              {filteredEvents.map((event, i) => {
                const levelColors = {
                  debug: 'text-muted-foreground',
                  info: 'text-blue-600',
                  warn: 'text-yellow-600',
                  error: 'text-red-600'
                };

                return (
                  <div key={event.event_id || i} className="flex gap-2 py-1">
                    <span className="text-muted-foreground text-xs">
                      {new Date(event.created_at).toLocaleTimeString()}
                    </span>
                    <span className={`${levelColors[event.level]} font-semibold uppercase text-xs`}>
                      [{event.level}]
                    </span>
                    <span className="flex-1">{event.message}</span>
                  </div>
                );
              })}

              {filteredEvents.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No {filter === 'all' ? '' : filter} events yet
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
