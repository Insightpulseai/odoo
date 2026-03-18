'use client'

import { useState, useEffect } from 'react'
import { useMobile } from '@/hooks/use-mobile'
import { Button } from '@/components/ui/button'
import SupabaseManagerDialog from '@/components/supabase-manager'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, Database, HardDrive, Shield, Users, KeyRound, ScrollText, Lightbulb, Zap } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { getProjectRefConfig } from '@/lib/supabase-config'

const features = [
  { title: 'Database', description: 'Manage tables, columns, and data with an intuitive interface', icon: Database },
  { title: 'Storage', description: 'Upload, organize, and manage files and media assets', icon: HardDrive },
  { title: 'Authentication', description: 'Configure auth providers and manage user sign-up flows', icon: Shield },
  { title: 'Users', description: 'View, manage, and monitor all registered users', icon: Users },
  { title: 'Secrets', description: 'Securely store and manage environment secrets', icon: KeyRound },
  { title: 'Logs', description: 'Monitor and analyze application logs in real-time', icon: ScrollText },
  { title: 'AI Suggestions', description: 'Get AI-powered SQL query suggestions and optimization', icon: Lightbulb },
]

export default function SupabasePage() {
  const [open, setOpen] = useState(false)
  const isMobile = useMobile()
  const [mounted, setMounted] = useState(false)

  const [projectConfig, setProjectConfig] = useState<ReturnType<typeof getProjectRefConfig>>({
    projectRef: null,
    isValid: false,
    source: 'none',
  })

  useEffect(() => {
    setProjectConfig(getProjectRefConfig())
    setMounted(true)
  }, [])

  const projectRef = projectConfig.projectRef ?? ''
  const hasValidProject = projectConfig.isValid

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gradient">Supabase Manager</h1>
          <p className="text-sm text-muted-foreground mt-1 font-medium">
            Manage database, auth, storage, users, secrets, and logs in one place.
          </p>
        </div>
        <Button onClick={() => setOpen(true)} size="lg" className="gap-2" disabled={mounted && !hasValidProject}>
          <Zap className="h-4 w-4" /> Open Manager
        </Button>
      </div>

      {/* Config error */}
      {mounted && !hasValidProject && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Configuration Required</AlertTitle>
          <AlertDescription className="mt-2">
            <p className="mb-2">{projectConfig.error}</p>
            <p className="text-sm opacity-80">
              Set <code className="bg-destructive/20 px-1 rounded">NEXT_PUBLIC_SUPABASE_PROJECT_REF</code> in your environment or add <code className="bg-destructive/20 px-1 rounded">?ref=your_project_ref</code> to the URL.
            </p>
          </AlertDescription>
        </Alert>
      )}

      {/* Feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((feature) => {
          const Icon = feature.icon
          return (
            <Card
              key={feature.title}
              className="glass border-border hover:border-primary/30 transition-colors cursor-pointer"
              onClick={() => mounted && hasValidProject && setOpen(true)}
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Icon className="h-5 w-5 text-primary" />
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* CTA */}
      <Card className="glass border-primary/20 bg-primary/5">
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Ready to manage your Supabase backend?</CardTitle>
          <CardDescription className="text-base mt-1">
            Database · Auth · Storage · Users · Secrets · Logs · AI
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center">
          <Button onClick={() => setOpen(true)} size="lg" className="gap-2" disabled={mounted && !hasValidProject}>
            Open Full Manager
            <Zap className="h-4 w-4" />
          </Button>
        </CardContent>
      </Card>

      <SupabaseManagerDialog
        projectRef={projectRef}
        open={open}
        onOpenChange={setOpen}
        isMobile={isMobile}
      />
    </div>
  )
}
