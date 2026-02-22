"use client"

import { StatCard } from "@/components/stat-card"
import { DataTable } from "@/components/ui/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { Activity, Server, ShieldCheck, Zap, ArrowUpRight, Clock, Box } from "lucide-react"
import { Button } from "@/components/ui/button"

type Deployment = {
  id: string
  env: "prod" | "stage"
  version: string
  status: "success" | "running" | "failed"
  time: string
}

const deployments: Deployment[] = [
  { id: "1", env: "prod", version: "v1.4.2", status: "success", time: "10 mins ago" },
  { id: "2", env: "stage", version: "v1.5.0-rc1", status: "running", time: "Just now" },
  { id: "3", env: "prod", version: "v1.4.1", status: "success", time: "4 hours ago" },
  { id: "4", env: "stage", version: "v1.4.9", status: "failed", time: "Yesterday" },
]

const columns: ColumnDef<Deployment>[] = [
  {
    accessorKey: "env",
    header: "Environment",
    cell: ({ row }) => {
      const env = row.getValue("env") as string
      return (
        <div className="flex items-center space-x-2">
          <div className={cn(
            "h-2 w-2 rounded-full",
            env === "prod" ? "bg-purple-500 shadow-md shadow-purple-500/20" : "bg-blue-500 shadow-md shadow-blue-500/20"
          )} />
          <span className="font-semibold uppercase text-xs tracking-wider">{env}</span>
        </div>
      )
    },
  },
  {
    accessorKey: "version",
    header: "Version",
    cell: ({ row }) => <code className="text-xs font-mono bg-white/5 px-2 py-1 rounded text-primary">{row.getValue("version")}</code>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      return (
        <span className={cn(
          "text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full border",
          status === "success" ? "bg-green-500/10 text-green-500 border-green-500/20" :
          status === "running" ? "bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse" :
          "bg-red-500/10 text-red-500 border-red-500/20"
        )}>
          {status}
        </span>
      )
    },
  },
  {
    accessorKey: "time",
    header: "Time",
    cell: ({ row }) => (
      <div className="flex items-center text-muted-foreground text-xs font-medium">
        <Clock className="mr-2 h-3 w-3" />
        {row.getValue("time")}
      </div>
    ),
  },
  {
    id: "actions",
    cell: () => (
      <Button variant="ghost" size="sm" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <ArrowUpRight className="h-4 w-4" />
      </Button>
    ),
  },
]

import { cn } from "@/lib/utils"

export default function OverviewPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gradient">Platform Overview</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">Real-time status of your Odoo.sh-equivalent stack.</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm" className="glass border-white/5">
            <Box className="mr-2 h-4 w-4" /> Export Report
          </Button>
          <Button variant="premium" size="sm">
            <Zap className="mr-2 h-4 w-4" /> Trigger Preflight
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Global Health"
          value="99.9%"
          description="Across 2 clusters"
          icon={Activity}
          trend={{ value: "+0.2%", positive: true }}
          className="glass-card"
        />
        <StatCard
          title="Active Nodes"
          value="4"
          description="Droplets & DBs"
          icon={Server}
          className="glass-card"
        />
        <StatCard
          title="Audit Pass Rate"
          value="100%"
          description="OCA Allowlist compliant"
          icon={ShieldCheck}
          className="glass-card"
        />
        <StatCard
          title="Daily Deploys"
          value="12"
          description="Avg 4.2 mins / deploy"
          icon={Zap}
          trend={{ value: "-20s", positive: true }}
          className="glass-card"
        />
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tight text-gradient">Recent Activity</h2>
          <Button variant="link" size="sm" className="text-xs text-primary font-bold uppercase tracking-wider">View All Logs</Button>
        </div>
        <DataTable columns={columns} data={deployments} />
      </div>
    </div>
  )
}
