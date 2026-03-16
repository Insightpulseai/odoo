"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChartThemeSelector } from "@/components/theme/ChartThemeSelector"

export default function Dashboard() {
  const [selectedBranch, setSelectedBranch] = useState("production")
  const [deploymentStatus, setDeploymentStatus] = useState<"idle" | "deploying" | "success" | "failed">("idle")

  const branches = [
    { name: "production", color: "bg-[#00A09D]", status: "Active", lastDeploy: "2 hours ago" },
    { name: "staging", color: "bg-blue-500", status: "Ready", lastDeploy: "4 hours ago" },
    { name: "development", color: "bg-yellow-500", status: "Building", lastDeploy: "10 minutes ago" },
  ]

  const commits = [
    { id: "abc123", author: "Michael Campbell", initials: "MC", message: "feat: Add BIR compliance module", time: "3 hours ago", status: "Ready", color: "bg-purple-600" },
    { id: "def456", author: "John Smith", initials: "JS", message: "fix: Update invoice processing logic", time: "5 hours ago", status: "Success", color: "bg-blue-600" },
    { id: "ghi789", author: "Alice Brown", initials: "AB", message: "chore: Update dependencies", time: "1 day ago", status: "Success", color: "bg-orange-600" },
  ]

  const builds = [
    { number: "#156", status: "Success", duration: "2m 34s", branch: "main" },
    { number: "#155", status: "Success", duration: "2m 45s", branch: "main" },
    { number: "#154", status: "Failed", duration: "1m 12s", branch: "staging" },
  ]

  const logs = [
    { time: "14:23:45", level: "INFO", message: "Deployment started for production branch" },
    { time: "14:23:46", level: "INFO", message: "Building Docker image..." },
    { time: "14:24:12", level: "SUCCESS", message: "Build completed successfully" },
    { time: "14:24:13", level: "INFO", message: "Running database migrations..." },
    { time: "14:24:45", level: "SUCCESS", message: "Migrations completed" },
    { time: "14:24:46", level: "INFO", message: "Starting application containers..." },
    { time: "14:25:12", level: "SUCCESS", message: "Deployment completed successfully" },
  ]

  const handleDeploy = () => {
    setDeploymentStatus("deploying")
    setTimeout(() => {
      setDeploymentStatus("success")
      setTimeout(() => setDeploymentStatus("idle"), 3000)
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#714B67] text-white border-b border-gray-700">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="text-xl font-bold">InsightPulse.ai</div>
            <nav className="hidden md:flex gap-6 text-sm">
              <a href="/" className="hover:text-gray-300">HOME</a>
              <a href="/dashboard" className="text-[#00A09D]">DASHBOARD</a>
              <a href="#" className="hover:text-gray-300">DEPLOYMENTS</a>
              <a href="#" className="hover:text-gray-300">SETTINGS</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <ChartThemeSelector />
            <span className="text-sm">@insightpulse</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar */}
          <div className="col-span-3 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm text-[#00A09D]">ENVIRONMENTS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {branches.map((branch) => (
                  <button
                    key={branch.name}
                    onClick={() => setSelectedBranch(branch.name)}
                    className={`w-full flex items-center gap-2 p-2 rounded text-sm transition-colors ${
                      selectedBranch === branch.name ? "bg-gray-100" : "hover:bg-gray-50"
                    }`}
                  >
                    <span className={`w-2 h-2 ${branch.color} rounded-full`}></span>
                    <div className="flex-1 text-left">
                      <div className="font-medium capitalize">{branch.name}</div>
                      <div className="text-xs text-gray-500">{branch.status}</div>
                    </div>
                  </button>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm text-[#00A09D]">RECENT BUILDS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {builds.map((build) => (
                  <div key={build.number} className="text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{build.number}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        build.status === "Success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                      }`}>
                        {build.status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">{build.duration} • {build.branch}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="col-span-9 space-y-6">
            {/* Branch Header */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-semibold capitalize">{selectedBranch} Environment</h1>
                    <p className="text-sm text-gray-500">
                      Last deployed {branches.find(b => b.name === selectedBranch)?.lastDeploy}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={handleDeploy}
                      disabled={deploymentStatus === "deploying"}
                      className="bg-[#00A09D] hover:bg-[#008B88]"
                    >
                      {deploymentStatus === "deploying" ? "Deploying..." : "Deploy Now"}
                    </Button>
                    {deploymentStatus === "success" && (
                      <span className="text-green-600 text-sm flex items-center">
                        ✓ Deployed
                      </span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tabs */}
            <Tabs defaultValue="commits" className="w-full">
              <TabsList>
                <TabsTrigger value="commits">Recent Commits</TabsTrigger>
                <TabsTrigger value="logs">Deployment Logs</TabsTrigger>
                <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
                <TabsTrigger value="shell">Web Shell</TabsTrigger>
              </TabsList>

              <TabsContent value="commits">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Commits</CardTitle>
                    <CardDescription>Latest changes to {selectedBranch} branch</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {commits.map((commit) => (
                      <div key={commit.id} className="flex items-start gap-3 p-3 rounded hover:bg-gray-50">
                        <div className={`w-10 h-10 rounded-full ${commit.color} flex items-center justify-center text-white text-sm font-medium`}>
                          {commit.initials}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium">{commit.message}</div>
                          <div className="text-sm text-gray-500">
                            by {commit.author} • {commit.time} • {commit.id}
                          </div>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          commit.status === "Success" ? "bg-green-100 text-green-700" :
                          commit.status === "Ready" ? "bg-[#00A09D]/10 text-[#00A09D]" :
                          "bg-gray-100 text-gray-700"
                        }`}>
                          {commit.status}
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="logs">
                <Card>
                  <CardHeader>
                    <CardTitle>Deployment Logs</CardTitle>
                    <CardDescription>Real-time logs from {selectedBranch} environment</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-900 rounded p-4 font-mono text-sm space-y-1 max-h-96 overflow-y-auto">
                      {logs.map((log, i) => (
                        <div key={i} className={`${
                          log.level === "ERROR" ? "text-red-400" :
                          log.level === "SUCCESS" ? "text-green-400" :
                          "text-gray-300"
                        }`}>
                          <span className="text-gray-500">[{log.time}]</span>{" "}
                          <span className="text-blue-400">{log.level}</span>: {log.message}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="monitoring">
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Monitoring</CardTitle>
                    <CardDescription>Resource usage and health metrics</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <Card className="border-l-4 border-l-green-500">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm text-gray-500">CPU Usage</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">24%</div>
                          <div className="text-xs text-gray-500">of 2 cores</div>
                        </CardContent>
                      </Card>
                      <Card className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm text-gray-500">Memory</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">1.2 GB</div>
                          <div className="text-xs text-gray-500">of 4 GB</div>
                        </CardContent>
                      </Card>
                      <Card className="border-l-4 border-l-purple-500">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm text-gray-500">Response Time</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">142ms</div>
                          <div className="text-xs text-gray-500">avg last 5m</div>
                        </CardContent>
                      </Card>
                      <Card className="border-l-4 border-l-orange-500">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm text-gray-500">Requests/min</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">1,234</div>
                          <div className="text-xs text-gray-500">+12% from avg</div>
                        </CardContent>
                      </Card>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="shell">
                <Card>
                  <CardHeader>
                    <CardTitle>Web Shell</CardTitle>
                    <CardDescription>Direct terminal access to {selectedBranch} environment</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-900 rounded p-4 font-mono text-sm">
                      <div className="text-green-400">insightpulse@{selectedBranch}:~$ _</div>
                      <div className="text-gray-500 mt-4">
                        ⚠️ Interactive shell access available with premium plan
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm">
                    🔄 Restart Services
                  </Button>
                  <Button variant="outline" size="sm">
                    📊 View Analytics
                  </Button>
                  <Button variant="outline" size="sm">
                    🔍 Search Logs
                  </Button>
                  <Button variant="outline" size="sm">
                    ⚙️ Environment Variables
                  </Button>
                  <Button variant="outline" size="sm">
                    🗄️ Database Backup
                  </Button>
                  <Button variant="outline" size="sm">
                    🔐 SSL Certificates
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
