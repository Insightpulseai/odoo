'use client'

import { useState } from 'react'
import type { Run } from '@ipai/taskbus'

const STATUS_COLORS: Record<string, string> = {
  pending:   'text-yellow-600 bg-yellow-50',
  running:   'text-blue-600 bg-blue-50',
  completed: 'text-green-600 bg-green-50',
  failed:    'text-red-600 bg-red-50',
  cancelled: 'text-gray-500 bg-gray-50',
}

function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_COLORS[status] ?? 'text-gray-500 bg-gray-50'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${cls}`}>
      {status}
    </span>
  )
}

function formatDuration(start: string | null, end: string | null): string {
  if (!start || !end) return '—'
  const ms = new Date(end).getTime() - new Date(start).getTime()
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function RunRow({ run, onClick }: { run: Run; onClick: () => void }) {
  return (
    <tr
      className="hover:bg-muted/50 cursor-pointer border-b border-border"
      onClick={onClick}
    >
      <td className="py-2 px-3 font-mono text-xs text-muted-foreground">{run.id.slice(0, 8)}</td>
      <td className="py-2 px-3 text-sm">{run.agent ?? run.run_type}</td>
      <td className="py-2 px-3 text-sm text-muted-foreground">{run.run_type}</td>
      <td className="py-2 px-3"><StatusBadge status={run.status} /></td>
      <td className="py-2 px-3 text-xs text-muted-foreground">
        {formatDuration(run.started_at, run.completed_at)}
      </td>
      <td className="py-2 px-3 text-xs text-muted-foreground">
        {new Date(run.created_at).toLocaleString()}
      </td>
    </tr>
  )
}

type RunLike = Partial<Run> & { id: string; status: string; run_type: string; created_at: string }

interface RunDetailProps {
  run: RunLike
  events: EventLike[]
  onClose: () => void
}

type EventLike = {
  id: string
  event_type: string
  payload: Record<string, unknown>
  timestamp: string
}

function RunDetail({ run, events, onClose }: RunDetailProps) {
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-end justify-center p-4" onClick={onClose}>
      <div
        className="bg-background rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-auto"
        onClick={e => e.stopPropagation()}
      >
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div>
            <div className="font-mono text-sm text-muted-foreground">{run.id}</div>
            <div className="font-medium mt-0.5">{(run as Run).agent ?? run.run_type}</div>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={run.status} />
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-xl leading-none">×</button>
          </div>
        </div>

        {(run as Run).error_json && (
          <div className="m-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            <strong>Error:</strong> {JSON.stringify((run as Run).error_json)}
          </div>
        )}

        <div className="p-4">
          <h4 className="text-sm font-medium mb-2">Event Stream</h4>
          {events.length === 0 ? (
            <p className="text-sm text-muted-foreground">No events yet.</p>
          ) : (
            <ol className="space-y-2">
              {events.map(e => (
                <li key={e.id} className="text-xs flex gap-3">
                  <span className="text-muted-foreground shrink-0 font-mono">
                    {new Date(e.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="font-medium">{e.event_type}</span>
                  <span className="text-muted-foreground truncate">
                    {JSON.stringify(e.payload)}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  )
}

export default function RunsClient({ initialRuns }: { initialRuns: RunLike[] }) {
  const [selectedRun, setSelectedRun] = useState<RunLike | null>(null)
  const [events, setEvents] = useState<EventLike[]>([])
  const [loadingEvents, setLoadingEvents] = useState(false)

  async function openRun(run: RunLike) {
    setSelectedRun(run)
    setLoadingEvents(true)
    try {
      const res = await fetch(`/api/runs/${run.id}/events`)
      if (res.ok) setEvents(await res.json())
    } catch {
      setEvents([])
    } finally {
      setLoadingEvents(false)
    }
  }

  return (
    <>
      {selectedRun && (
        <RunDetail
          run={selectedRun}
          events={loadingEvents ? [] : events}
          onClose={() => setSelectedRun(null)}
        />
      )}

      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-xs text-muted-foreground uppercase tracking-wide">
            <tr>
              <th className="py-2 px-3 text-left font-medium">ID</th>
              <th className="py-2 px-3 text-left font-medium">Agent</th>
              <th className="py-2 px-3 text-left font-medium">Type</th>
              <th className="py-2 px-3 text-left font-medium">Status</th>
              <th className="py-2 px-3 text-left font-medium">Duration</th>
              <th className="py-2 px-3 text-left font-medium">Created</th>
            </tr>
          </thead>
          <tbody>
            {initialRuns.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-sm text-muted-foreground">
                  No runs yet. Enable a schedule or trigger the cron endpoint.
                </td>
              </tr>
            ) : (
              initialRuns.map(run => (
                <RunRow key={run.id} run={run as Run} onClick={() => openRun(run)} />
              ))
            )}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-muted-foreground mt-3">
        Showing last 100 runs. Click a row to view the event stream.
        Cron tick every 5 min via <code>/api/cron/tick</code>.
      </p>
    </>
  )
}
