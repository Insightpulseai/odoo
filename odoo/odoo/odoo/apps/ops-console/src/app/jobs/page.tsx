'use client'

import { useState } from 'react'
import {
  Card,
  Text,
  TabList,
  Tab,
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Button,
  Spinner,
  ProgressBar,
  makeStyles,
  tokens,
} from '@fluentui/react-components'
import {
  CheckmarkCircleFilled,
  DismissCircleFilled,
  ClockRegular,
  PauseCircleRegular,
  ArrowSyncRegular,
  ArrowCircleRightFilled,
  CircleFilled,
  PlugConnectedRegular,
} from '@fluentui/react-icons'
import type { SelectTabData, SelectTabEvent } from '@fluentui/react-components'
import { useJobs, useMicrosoftCloud } from '@/lib/hooks'
import { cronJobs as fallbackCronJobs } from '@/lib/data'
import { StatusBadge } from '@/components/ui/status-badge'
import {
  PIPELINES,
  pipelineStats,
  engineLabel,
  medallionLabel,
} from '@/lib/pipelines-data'
import type { Pipeline, PipelineStatus, MedallionStage } from '@/lib/pipelines-data'

const useStyles = makeStyles({
  page: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXL,
    maxWidth: '1200px',
  },
  header: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
  },
  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  meta: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
  },
  subtitle: {
    color: tokens.colorNeutralForeground3,
  },
  sourceBadge: {
    fontSize: tokens.fontSizeBase100,
  },
  tableCard: {
    padding: tokens.spacingVerticalL,
  },
  tabContent: {
    marginTop: tokens.spacingVerticalL,
  },
  statusIcon: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
  },
  iconSuccess: {
    color: tokens.colorPaletteGreenForeground1,
    fontSize: '16px',
  },
  iconError: {
    color: tokens.colorPaletteRedForeground1,
    fontSize: '16px',
  },
  iconPaused: {
    color: tokens.colorNeutralForeground3,
    fontSize: '16px',
  },
  iconPending: {
    color: tokens.colorPaletteYellowForeground1,
    fontSize: '16px',
  },
  placeholderCard: {
    padding: tokens.spacingVerticalXXL,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  typeBadge: {
    textTransform: 'capitalize',
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },
  // Pipeline-specific styles
  statsRow: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
    marginBottom: tokens.spacingVerticalM,
  },
  statCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
    minWidth: '80px',
  },
  statValue: {
    fontVariantNumeric: 'tabular-nums',
  },
  statLabel: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase100,
  },
  filterRow: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
    marginBottom: tokens.spacingVerticalM,
  },
  pipelineDesc: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  pipelineFlow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
  flowArrow: {
    color: tokens.colorNeutralForeground3,
    fontSize: '12px',
  },
  durationText: {
    fontVariantNumeric: 'tabular-nums',
    fontSize: tokens.fontSizeBase200,
  },
  medallionBadge: {
    textTransform: 'capitalize',
  },
})

// Badge color for pipeline status
const pipelineStatusMap: Record<PipelineStatus, { color: string; label: string }> = {
  flowing: { color: 'success', label: 'Flowing' },
  idle: { color: 'warning', label: 'Idle' },
  error: { color: 'danger', label: 'Error' },
  paused: { color: 'informative', label: 'Paused' },
  unconfigured: { color: 'warning', label: 'Unconfigured' },
  planned: { color: 'informative', label: 'Planned' },
  deprecated: { color: 'danger', label: 'Deprecated' },
}

// Medallion stage colors
const medallionColors: Record<MedallionStage, string> = {
  'ingest': 'subtle',
  'bronze': 'warning',
  'silver': 'informative',
  'gold': 'brand',
  'platinum': 'success',
  'n/a': 'subtle',
}

const cronTypeColors: Record<string, 'informative' | 'brand' | 'subtle'> = {
  'odoo-cron': 'informative',
  'github-action': 'brand',
  'n8n-workflow': 'subtle',
  'github-actions': 'brand',
  'azure-devops': 'informative',
  'power-automate': 'subtle',
  'ai-foundry': 'informative',
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '--'
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
}

function timeAgo(iso: string | null): string {
  if (!iso) return '--'
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export default function JobsPage() {
  const styles = useStyles()
  const [selectedTab, setSelectedTab] = useState<string>('pipelines')
  const [statusFilter, setStatusFilter] = useState<PipelineStatus | 'all'>('all')
  const [engineFilter, setEngineFilter] = useState<string>('all')
  const { jobs, crons, source, isLoading, refresh } = useJobs()
  const { jobs: msJobs, isLoading: msJobsLoading } = useMicrosoftCloud()

  const displayCrons = crons.length > 0 ? crons : fallbackCronJobs
  const msCronRows = (msJobs ?? []).map((j) => ({
    name: j.name,
    schedule: j.schedule,
    type: j.model ?? 'microsoft-cloud',
    status: j.status,
    provider: j.provider,
  }))
  const allCrons = [
    ...displayCrons.map((c) => ({ ...c, provider: 'Odoo.sh' })),
    ...msCronRows,
  ]

  // Pipeline filtering
  const stats = pipelineStats(PIPELINES)
  const filteredPipelines = PIPELINES.filter(p => {
    if (statusFilter !== 'all' && p.status !== statusFilter) return false
    if (engineFilter !== 'all' && p.engine !== engineFilter) return false
    return true
  })

  // Unique engines for filter
  const uniqueEngines = [...new Set(PIPELINES.map(p => p.engine))].sort()

  const handleTabSelect = (_: SelectTabEvent, data: SelectTabData) => {
    setSelectedTab(data.value as string)
  }

  const CronStatusIcon = ({ status }: { status: string }) => {
    if (status === 'active') return <CheckmarkCircleFilled className={styles.iconSuccess} />
    if (status === 'paused') return <PauseCircleRegular className={styles.iconPaused} />
    return <DismissCircleFilled className={styles.iconError} />
  }

  const JobStatusIcon = ({ status }: { status: string }) => {
    if (status === 'completed' || status === 'success') return <CheckmarkCircleFilled className={styles.iconSuccess} />
    if (status === 'pending' || status === 'queued') return <ClockRegular className={styles.iconPending} />
    return <DismissCircleFilled className={styles.iconError} />
  }

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading jobs..." size="large" />
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <Text as="h1" size={800} weight="bold">
            Jobs, Pipelines & Integrations
          </Text>
          <div className={styles.meta}>
            <Badge
              appearance="outline"
              color={source === 'live' ? 'success' : 'warning'}
              className={styles.sourceBadge}
            >
              Source: {source}
            </Badge>
            <Button
              appearance="subtle"
              icon={<ArrowSyncRegular />}
              onClick={() => refresh()}
              size="small"
              aria-label="Refresh jobs"
            >
              Refresh
            </Button>
          </div>
        </div>
        <Text className={styles.subtitle} size={400}>
          All integration pipelines, ETL workflows, cron jobs, and background tasks
        </Text>
      </div>

      <Card className={styles.tableCard}>
        <TabList
          selectedValue={selectedTab}
          onTabSelect={handleTabSelect}
          aria-label="Job categories"
        >
          <Tab value="pipelines" icon={<PlugConnectedRegular />}>
            Pipelines ({PIPELINES.length})
          </Tab>
          <Tab value="cron">Cron Jobs ({allCrons.length})</Tab>
          <Tab value="runs">Live Runs ({jobs.length})</Tab>
          <Tab value="tasks">Background Tasks</Tab>
        </TabList>

        <div className={styles.tabContent}>
          {/* ===== PIPELINES TAB ===== */}
          {selectedTab === 'pipelines' && (
            <>
              {/* Stats summary */}
              <div className={styles.statsRow}>
                {[
                  { label: 'Total', value: stats.total, color: tokens.colorNeutralForeground1 },
                  { label: 'Flowing', value: stats.flowing, color: tokens.colorPaletteGreenForeground1 },
                  { label: 'Idle', value: stats.idle, color: tokens.colorPaletteYellowForeground1 },
                  { label: 'Error', value: stats.error, color: tokens.colorPaletteRedForeground1 },
                  { label: 'Planned', value: stats.planned, color: tokens.colorNeutralForeground3 },
                  { label: 'Unconfigured', value: stats.unconfigured, color: tokens.colorPaletteYellowForeground1 },
                ].map(s => (
                  <Card key={s.label} className={styles.statCard}>
                    <Text weight="bold" size={600} className={styles.statValue} style={{ color: s.color }}>
                      {s.value}
                    </Text>
                    <Text className={styles.statLabel}>{s.label}</Text>
                  </Card>
                ))}
              </div>

              {/* Filters */}
              <div className={styles.filterRow}>
                <Button
                  appearance={statusFilter === 'all' ? 'primary' : 'subtle'}
                  size="small"
                  onClick={() => setStatusFilter('all')}
                >
                  All
                </Button>
                {(['flowing', 'idle', 'error', 'planned', 'unconfigured', 'paused', 'deprecated'] as PipelineStatus[]).map(s => (
                  <Button
                    key={s}
                    appearance={statusFilter === s ? 'primary' : 'subtle'}
                    size="small"
                    onClick={() => setStatusFilter(s)}
                  >
                    {pipelineStatusMap[s].label}
                  </Button>
                ))}
                <Text style={{ margin: `0 ${tokens.spacingHorizontalS}`, color: tokens.colorNeutralForeground3 }}>|</Text>
                <Button
                  appearance={engineFilter === 'all' ? 'primary' : 'subtle'}
                  size="small"
                  onClick={() => setEngineFilter('all')}
                >
                  All Engines
                </Button>
                {uniqueEngines.map(e => (
                  <Button
                    key={e}
                    appearance={engineFilter === e ? 'primary' : 'subtle'}
                    size="small"
                    onClick={() => setEngineFilter(e)}
                  >
                    {engineLabel(e as any)}
                  </Button>
                ))}
              </div>

              {/* Pipeline table */}
              <Table aria-label="Integration pipelines table">
                <TableHeader>
                  <TableRow>
                    <TableHeaderCell>Pipeline</TableHeaderCell>
                    <TableHeaderCell>Engine</TableHeaderCell>
                    <TableHeaderCell>Flow</TableHeaderCell>
                    <TableHeaderCell>Stage</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>Last Run</TableHeaderCell>
                    <TableHeaderCell>Duration</TableHeaderCell>
                    <TableHeaderCell>Schedule</TableHeaderCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPipelines.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell>
                        <div>
                          <Text weight="semibold" size={300}>{p.name}</Text>
                          <br />
                          <Text className={styles.pipelineDesc}>{p.description}</Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge appearance="outline" color="informative" className={styles.typeBadge}>
                          {engineLabel(p.engine)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className={styles.pipelineFlow}>
                          <Text size={200}>{p.source}</Text>
                          <ArrowCircleRightFilled className={styles.flowArrow} />
                          <Text size={200}>{p.destination}</Text>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          appearance="filled"
                          color={medallionColors[p.medallionStage] as any}
                          className={styles.medallionBadge}
                        >
                          {medallionLabel(p.medallionStage)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <StatusBadge
                          status={p.status === 'flowing' ? 'active' : p.status === 'error' ? 'error' : p.status === 'idle' ? 'paused' : p.status}
                          label={pipelineStatusMap[p.status]?.label ?? p.status}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <div>
                          {p.lastRun ? (
                            <>
                              <Text size={200}>{timeAgo(p.lastRun)}</Text>
                              {p.lastStatus && (
                                <div className={styles.statusIcon}>
                                  {p.lastStatus === 'success' ? (
                                    <CheckmarkCircleFilled className={styles.iconSuccess} />
                                  ) : p.lastStatus === 'running' ? (
                                    <ArrowSyncRegular className={styles.iconPending} />
                                  ) : (
                                    <DismissCircleFilled className={styles.iconError} />
                                  )}
                                </div>
                              )}
                            </>
                          ) : (
                            <Text className={styles.pipelineDesc}>Never</Text>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Text className={styles.durationText}>
                          {formatDuration(p.lastDuration)}
                        </Text>
                      </TableCell>
                      <TableCell>
                        <Text font="monospace" size={200}>{p.schedule}</Text>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          )}

          {/* ===== CRON TAB ===== */}
          {selectedTab === 'cron' && (
            <Table aria-label="Cron jobs table">
              <TableHeader>
                <TableRow>
                  <TableHeaderCell>Name</TableHeaderCell>
                  <TableHeaderCell>Schedule</TableHeaderCell>
                  <TableHeaderCell>Type</TableHeaderCell>
                  <TableHeaderCell>Provider</TableHeaderCell>
                  <TableHeaderCell>Status</TableHeaderCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allCrons.map((job) => (
                  <TableRow key={`${job.provider}-${job.name}`}>
                    <TableCell>
                      <Text weight="semibold">{job.name}</Text>
                    </TableCell>
                    <TableCell>
                      <Text font="monospace" size={200}>{job.schedule}</Text>
                    </TableCell>
                    <TableCell>
                      <Badge
                        appearance="outline"
                        color={cronTypeColors[job.type] ?? 'subtle'}
                        className={styles.typeBadge}
                      >
                        {job.type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        appearance="outline"
                        color={job.provider === 'microsoft-cloud' ? 'brand' : 'subtle'}
                      >
                        {job.provider === 'microsoft-cloud' ? 'MS Cloud' : job.provider ?? 'Odoo.sh'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className={styles.statusIcon}>
                        <CronStatusIcon status={job.status} />
                        <Text size={200}>{job.status}</Text>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {/* ===== RUNS TAB ===== */}
          {selectedTab === 'runs' && (
            <>
              {jobs.length === 0 ? (
                <Card className={styles.placeholderCard}>
                  <Text size={400} style={{ color: tokens.colorNeutralForeground3 }}>
                    No live GitHub Actions runs found. Runs appear here when workflows are active.
                  </Text>
                </Card>
              ) : (
                <Table aria-label="Live job runs table">
                  <TableHeader>
                    <TableRow>
                      <TableHeaderCell>Name</TableHeaderCell>
                      <TableHeaderCell>Type</TableHeaderCell>
                      <TableHeaderCell>Status</TableHeaderCell>
                      <TableHeaderCell>Last Run</TableHeaderCell>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {jobs.map((job) => (
                      <TableRow key={job.id}>
                        <TableCell>
                          <Text weight="semibold">{job.name}</Text>
                        </TableCell>
                        <TableCell>
                          <Badge appearance="outline" color="brand" className={styles.typeBadge}>
                            {job.type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className={styles.statusIcon}>
                            <JobStatusIcon status={job.status} />
                            <Text size={200}>{job.status}</Text>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Text size={200}>{job.lastRun ?? '-'}</Text>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </>
          )}

          {/* ===== TASKS TAB ===== */}
          {selectedTab === 'tasks' && (
            <Card className={styles.placeholderCard}>
              <Text size={400} style={{ color: tokens.colorNeutralForeground3 }}>
                Background task queue will be connected when the MCP Jobs system is fully deployed.
              </Text>
            </Card>
          )}
        </div>
      </Card>
    </div>
  )
}
