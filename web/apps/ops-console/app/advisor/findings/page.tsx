"use client"

import { useEffect, useState } from "react"
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from "@tanstack/react-table"
import Link from "next/link"
import { ArrowLeft, ArrowUpDown } from "lucide-react"
import { cn } from "@/lib/utils"

interface Finding {
  id: string
  rule_id: string
  pillar: string
  severity: string
  title: string
  description?: string
  remediation?: string
  resource_ref?: string
  created_at: string
}

const SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-500/20 text-red-400",
  high: "bg-orange-500/20 text-orange-400",
  medium: "bg-yellow-500/20 text-yellow-400",
  low: "bg-blue-500/20 text-blue-400",
  info: "bg-white/10 text-muted-foreground",
}

const columnHelper = createColumnHelper<Finding>()

const columns = [
  columnHelper.accessor("severity", {
    header: ({ column }) => (
      <button
        className="flex items-center gap-1 text-[10px] uppercase tracking-widest font-semibold text-muted-foreground"
        onClick={() => column.toggleSorting()}
      >
        Severity <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: (info) => (
      <span className={cn("text-[10px] font-bold px-1.5 py-0.5 rounded uppercase", SEVERITY_COLORS[info.getValue()])}>
        {info.getValue()}
      </span>
    ),
    sortingFn: (a, b) =>
      SEVERITY_ORDER.indexOf(a.original.severity) - SEVERITY_ORDER.indexOf(b.original.severity),
  }),
  columnHelper.accessor("pillar", {
    header: () => <span className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground">Pillar</span>,
    cell: (info) => <span className="text-xs capitalize">{info.getValue().replace(/_/g, " ")}</span>,
  }),
  columnHelper.accessor("title", {
    header: () => <span className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground">Finding</span>,
    cell: (info) => (
      <div>
        <div className="text-xs font-medium">{info.getValue()}</div>
        <div className="text-[10px] font-mono text-muted-foreground mt-0.5">{info.row.original.rule_id}</div>
      </div>
    ),
  }),
  columnHelper.accessor("resource_ref", {
    header: () => <span className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground">Resource</span>,
    cell: (info) => <span className="text-[10px] font-mono text-muted-foreground">{info.getValue() ?? "—"}</span>,
  }),
  columnHelper.accessor("created_at", {
    header: () => <span className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground">Detected</span>,
    cell: (info) => <span className="text-[10px] text-muted-foreground">{new Date(info.getValue()).toLocaleDateString()}</span>,
  }),
]

export default function FindingsPage() {
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)
  const [pillarFilter, setPillarFilter] = useState("")
  const [severityFilter, setSeverityFilter] = useState("")
  const [sorting, setSorting] = useState<SortingState>([{ id: "severity", desc: false }])

  useEffect(() => {
    const params = new URLSearchParams()
    if (pillarFilter) params.set("pillar", pillarFilter)
    if (severityFilter) params.set("severity", severityFilter)
    setLoading(true)
    fetch(`/api/advisor/findings?${params.toString()}`)
      .then((r) => r.json())
      .then(({ findings: f }) => setFindings(f ?? []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [pillarFilter, severityFilter])

  const table = useReactTable({
    data: findings,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  const PILLARS = ["", "cost", "security", "reliability", "operational_excellence", "performance"]
  const SEVERITIES = ["", "critical", "high", "medium", "low", "info"]

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/advisor" className="text-muted-foreground hover:text-white transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h2 className="text-2xl font-bold">All Findings</h2>
        <span className="text-xs text-muted-foreground">
          {loading ? "…" : `${findings.length} finding${findings.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <select
          value={pillarFilter}
          onChange={(e) => setPillarFilter(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-primary/50"
        >
          {PILLARS.map((p) => (
            <option key={p} value={p}>{p ? p.replace(/_/g, " ") : "All pillars"}</option>
          ))}
        </select>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-primary/50"
        >
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>{s || "All severities"}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="glass border border-white/5 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground text-sm">Loading findings…</div>
        ) : findings.length === 0 ? (
          <div className="p-12 text-center text-muted-foreground">
            <div className="text-2xl mb-2">✅</div>
            <div className="text-sm">No findings match your filters.</div>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              {table.getHeaderGroups().map((hg) => (
                <tr key={hg.id} className="border-b border-white/5">
                  {hg.headers.map((header) => (
                    <th key={header.id} className="text-left px-4 py-3">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
