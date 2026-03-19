'use client'

import {
  Card,
  Text,
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Button,
  Spinner,
  makeStyles,
  tokens,
} from '@fluentui/react-components'
import { ArrowSyncRegular, ArrowRightRegular } from '@fluentui/react-icons'
import { useTaskBus, useMicrosoftCloud, useOrchestrationRegistry } from '@/lib/hooks'
import { AgentGraph } from '@/components/charts/agent-graph'

/* ------------------------------------------------------------------ */
/*  Agent topology metadata                                            */
/* ------------------------------------------------------------------ */

interface AgentNode {
  id: string
  label: string
  role: string
  color: string
}

const AGENTS: AgentNode[] = [
  { id: 'mcp-coordinator', label: 'MCP Coordinator', role: 'Hub / Router', color: '#7B2FF2' },
  { id: 'odoo-copilot', label: 'Odoo Copilot', role: 'Tool Execution', color: '#2264D1' },
  { id: 'foundry', label: 'Foundry Agent', role: 'LLM Inference', color: '#0078D4' },
  { id: 'kb-search', label: 'KB Search', role: 'Index Queries', color: '#107C10' },
  { id: 'n8n', label: 'n8n Orchestrator', role: 'Workflow Automation', color: '#FF6D5A' },
  { id: 'github-actions', label: 'GitHub Actions', role: 'CI/CD Pipeline', color: '#24292F' },
  { id: 'slack-agent', label: 'Slack Agent', role: 'Notifications', color: '#4A154B' },
]

/* ------------------------------------------------------------------ */
/*  Styles                                                             */
/* ------------------------------------------------------------------ */

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

  /* Stats row */
  statsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: tokens.spacingHorizontalL,
  },
  statCard: {
    padding: tokens.spacingVerticalL,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: tokens.spacingVerticalXS,
    borderRadius: '12px',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: 700 as const,
    lineHeight: 1,
  },
  statLabel: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },

  /* Topology */
  topologyCard: {
    padding: tokens.spacingVerticalXL,
    borderRadius: '12px',
  },
  topologyTitle: {
    marginBottom: tokens.spacingVerticalL,
  },
  topologyGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr',
    gridTemplateRows: 'auto auto auto',
    gap: tokens.spacingVerticalL,
    alignItems: 'center',
    justifyItems: 'center',
    position: 'relative' as const,
    padding: '20px 0',
  },
  hubNode: {
    gridColumn: '2',
    gridRow: '2',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: tokens.spacingVerticalXS,
    padding: '16px 20px',
    borderRadius: '16px',
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    color: 'white',
    boxShadow: '0 4px 16px rgba(123, 47, 242, 0.3)',
    minWidth: '160px',
    textAlign: 'center' as const,
    position: 'relative' as const,
    zIndex: 2,
  },
  spokeNode: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
    padding: '12px 16px',
    borderRadius: '12px',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    minWidth: '140px',
    textAlign: 'center' as const,
    position: 'relative' as const,
    zIndex: 2,
    transitionProperty: 'box-shadow, border-color',
    transitionDuration: '150ms',
    ':hover': {
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    },
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    display: 'inline-block',
  },
  statusRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  spokeRole: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase100,
  },
  spokeStats: {
    color: tokens.colorNeutralForeground2,
    fontSize: tokens.fontSizeBase100,
    fontFamily: tokens.fontFamilyMonospace,
  },

  /* Connection lines via SVG overlay */
  topologySvg: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none' as const,
    zIndex: 1,
  },

  /* Table */
  tableCard: {
    padding: tokens.spacingVerticalL,
    borderRadius: '12px',
  },
  statusIcon: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },

  /* Pipeline sections */
  sectionCard: {
    padding: tokens.spacingVerticalXL,
    borderRadius: '12px',
  },
  sectionTitle: {
    marginBottom: tokens.spacingVerticalL,
  },
  pipelineGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(480px, 1fr))',
    gap: tokens.spacingVerticalL,
  },
  pipelineCard: {
    padding: tokens.spacingVerticalL,
    borderRadius: '10px',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
  },
  pipelineHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  pipelineDescription: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  stagesFlow: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: '6px',
    padding: `${tokens.spacingVerticalS} 0`,
  },
  stageChip: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '2px',
    padding: '6px 10px',
    borderRadius: '8px',
    backgroundColor: tokens.colorNeutralBackground3,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    fontSize: tokens.fontSizeBase200,
    textAlign: 'center' as const,
  },
  stageTool: {
    fontSize: tokens.fontSizeBase100,
    color: tokens.colorNeutralForeground3,
    fontFamily: tokens.fontFamilyMonospace,
  },
  stageArrow: {
    color: tokens.colorNeutralForeground3,
    display: 'flex',
    alignItems: 'center',
  },
  sourceFilePath: {
    fontSize: tokens.fontSizeBase100,
    color: tokens.colorNeutralForeground3,
    fontFamily: tokens.fontFamilyMonospace,
  },
  docClassTable: {
    marginTop: tokens.spacingVerticalS,
  },
  monoCell: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase200,
  },
})

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function statusColor(status: string): 'success' | 'danger' | 'warning' | 'informative' | 'subtle' {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'processing': return 'warning'
    case 'queued': return 'informative'
    default: return 'subtle'
  }
}

function sourceColor(source: string): string {
  const agent = AGENTS.find(a => a.id === source)
  return agent?.color ?? tokens.colorNeutralForeground2
}

function formatDuration(created: string, updated: string): string {
  const ms = new Date(updated).getTime() - new Date(created).getTime()
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
  } catch {
    return iso
  }
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

// Microsoft Cloud nodes for the agent graph
const MS_CLOUD_AGENTS: AgentNode[] = [
  { id: 'ms-ai-foundry', label: 'AI Foundry', role: 'LLM Inference', color: '#0078D4' },
  { id: 'ms-copilot-studio', label: 'Copilot Studio', role: 'AI Agents', color: '#742774' },
  { id: 'ms-github', label: 'GitHub', role: 'Dev & Delivery', color: '#24292F' },
  { id: 'ms-devops', label: 'Azure DevOps', role: 'CI/CD Pipeline', color: '#0078D4' },
  { id: 'ms-entra', label: 'Entra ID', role: 'Identity', color: '#0078D4' },
  { id: 'ms-power-automate', label: 'Power Automate', role: 'Automation', color: '#0066FF' },
]

// Edges between Microsoft Cloud services
const MS_CLOUD_EDGES = [
  { source: 'AI Foundry', target: 'Copilot Studio', label: 'Model Serving' },
  { source: 'GitHub', target: 'Azure DevOps', label: 'CI/CD' },
  { source: 'GitHub', target: 'Azure', label: 'Deployment' },
  { source: 'Power Automate', target: 'n8n Orchestrator', label: 'Workflow Bridge' },
  { source: 'Entra ID', target: 'MCP Coordinator', label: 'Auth Tokens' },
]

export default function OrchestrationPage() {
  const styles = useStyles()
  const { jobs, stats, source, isLoading, refresh } = useTaskBus()
  const { services: msServices, isLoading: msLoading } = useMicrosoftCloud()
  const {
    pipelines,
    documentClasses,
    source: registrySource,
    isLoading: registryLoading,
  } = useOrchestrationRegistry()

  // Compute per-agent stats from jobs
  const agentJobCounts = new Map<string, number>()
  const agentLastActivity = new Map<string, string>()
  for (const job of jobs) {
    agentJobCounts.set(job.source, (agentJobCounts.get(job.source) ?? 0) + 1)
    const existing = agentLastActivity.get(job.source)
    if (!existing || job.updatedAt > existing) {
      agentLastActivity.set(job.source, job.updatedAt)
    }
  }

  // Determine agent status from recent jobs
  function agentStatus(agentId: string): 'green' | 'yellow' | 'red' {
    const recentJobs = jobs.filter(j => j.source === agentId)
    if (recentJobs.length === 0) return 'yellow'
    const latest = recentJobs[0]
    if (latest.status === 'failed') return 'red'
    if (latest.status === 'processing') return 'yellow'
    return 'green'
  }

  function dotColor(status: 'green' | 'yellow' | 'red'): string {
    switch (status) {
      case 'green': return '#107C10'
      case 'yellow': return '#FFB900'
      case 'red': return '#D13438'
    }
  }

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading orchestration data..." size="large" />
        </div>
      </div>
    )
  }

  // Spoke agents (everything except hub)
  const hub = AGENTS[0] // mcp-coordinator
  const spokes = AGENTS.slice(1)

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <Text as="h1" size={800} weight="bold">
            Agent Orchestration
          </Text>
          <div className={styles.meta}>
            <Badge
              appearance="outline"
              color={source === 'supabase' ? 'success' : 'warning'}
              className={styles.sourceBadge}
            >
              Source: {source}
            </Badge>
            <Button
              appearance="subtle"
              icon={<ArrowSyncRegular />}
              onClick={() => refresh()}
              size="small"
              aria-label="Refresh task bus"
            >
              Refresh
            </Button>
          </div>
        </div>
        <Text className={styles.subtitle} size={400}>
          Document pipelines, agent topology, and task bus orchestration
        </Text>
      </div>

      {/* Stats cards */}
      <div className={styles.statsRow}>
        <Card className={styles.statCard}>
          <span className={styles.statValue} style={{ color: '#0078D4' }}>{stats.queued}</span>
          <span className={styles.statLabel}>Queued</span>
        </Card>
        <Card className={styles.statCard}>
          <span className={styles.statValue} style={{ color: '#FFB900' }}>{stats.processing}</span>
          <span className={styles.statLabel}>Processing</span>
        </Card>
        <Card className={styles.statCard}>
          <span className={styles.statValue} style={{ color: '#107C10' }}>{stats.completed}</span>
          <span className={styles.statLabel}>Completed</span>
        </Card>
        <Card className={styles.statCard}>
          <span className={styles.statValue} style={{ color: '#D13438' }}>{stats.failed}</span>
          <span className={styles.statLabel}>Failed</span>
        </Card>
        <Card className={styles.statCard}>
          <span className={styles.statValue} style={{ color: '#8B0000' }}>{stats.dlqCount}</span>
          <span className={styles.statLabel}>Dead Letter</span>
        </Card>
      </div>

      {/* Document Pipelines (from registry) */}
      {!registryLoading && pipelines.length > 0 && (
        <Card className={styles.sectionCard}>
          <Text as="h2" size={500} weight="semibold" className={styles.sectionTitle}>
            Document Pipelines
          </Text>
          <div className={styles.pipelineGrid}>
            {pipelines.map((pipeline) => (
              <div key={pipeline.id} className={styles.pipelineCard}>
                <div className={styles.pipelineHeader}>
                  <Text weight="bold" size={300}>{pipeline.name}</Text>
                  <Badge appearance="outline" color="informative">{pipeline.documentClass}</Badge>
                </div>
                {pipeline.description && (
                  <Text className={styles.pipelineDescription}>{pipeline.description}</Text>
                )}
                <div className={styles.stagesFlow}>
                  {pipeline.stages.map((stage, idx) => (
                    <span key={idx} style={{ display: 'contents' }}>
                      {idx > 0 && (
                        <span className={styles.stageArrow}>
                          <ArrowRightRegular fontSize={14} />
                        </span>
                      )}
                      <span className={styles.stageChip}>
                        <span>{stage.name}</span>
                        {stage.tool && <span className={styles.stageTool}>{stage.tool}</span>}
                      </span>
                    </span>
                  ))}
                </div>
                <Text className={styles.sourceFilePath}>{pipeline.sourceFile}</Text>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Document Classes (from registry) */}
      {!registryLoading && documentClasses.length > 0 && (
        <Card className={styles.sectionCard}>
          <Text as="h2" size={500} weight="semibold" className={styles.sectionTitle}>
            Document Classes
          </Text>
          <div className={styles.docClassTable}>
            <Table aria-label="Document classes">
              <TableHeader>
                <TableRow>
                  <TableHeaderCell>Class Name</TableHeaderCell>
                  <TableHeaderCell>Display Name</TableHeaderCell>
                  <TableHeaderCell>Doc Intelligence Model</TableHeaderCell>
                  <TableHeaderCell>Odoo Model</TableHeaderCell>
                  <TableHeaderCell>Key Fields</TableHeaderCell>
                  <TableHeaderCell>Confidence</TableHeaderCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documentClasses.map((dc) => (
                  <TableRow key={dc.className}>
                    <TableCell>
                      <Text weight="semibold" size={200}>{dc.className}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{dc.displayName}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200} className={styles.monoCell}>{dc.docintModel}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200} className={styles.monoCell}>
                        {dc.odooModel ?? '\u2014'}
                      </Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{dc.keyFields.join(', ')}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{(dc.confidenceThreshold * 100).toFixed(0)}%</Text>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      )}

      {/* Agent topology */}
      <Card className={styles.topologyCard}>
        <Text as="h2" size={500} weight="semibold" className={styles.topologyTitle}>
          Agent Topology
        </Text>
        <div className={styles.topologyGrid}>
          {/* Row 1: spokes 0, 1, 2 */}
          {spokes.slice(0, 3).map((agent) => {
            const st = agentStatus(agent.id)
            return (
              <div key={agent.id} className={styles.spokeNode}>
                <Text weight="semibold" size={300}>{agent.label}</Text>
                <div className={styles.statusRow}>
                  <span className={styles.statusDot} style={{ backgroundColor: dotColor(st) }} />
                  <span className={styles.spokeRole}>{agent.role}</span>
                </div>
                <span className={styles.spokeStats}>
                  {agentJobCounts.get(agent.id) ?? 0} jobs
                </span>
                {agentLastActivity.get(agent.id) && (
                  <span className={styles.spokeStats}>
                    {formatTime(agentLastActivity.get(agent.id)!)}
                  </span>
                )}
              </div>
            )
          })}

          {/* Row 2: spoke 3, HUB, spoke 4 */}
          {spokes[3] && (() => {
            const agent = spokes[3]
            const st = agentStatus(agent.id)
            return (
              <div key={agent.id} className={styles.spokeNode}>
                <Text weight="semibold" size={300}>{agent.label}</Text>
                <div className={styles.statusRow}>
                  <span className={styles.statusDot} style={{ backgroundColor: dotColor(st) }} />
                  <span className={styles.spokeRole}>{agent.role}</span>
                </div>
                <span className={styles.spokeStats}>
                  {agentJobCounts.get(agent.id) ?? 0} jobs
                </span>
                {agentLastActivity.get(agent.id) && (
                  <span className={styles.spokeStats}>
                    {formatTime(agentLastActivity.get(agent.id)!)}
                  </span>
                )}
              </div>
            )
          })()}
          <div className={styles.hubNode}>
            <Text weight="bold" size={400} style={{ color: 'white' }}>{hub.label}</Text>
            <Text size={200} style={{ color: 'rgba(255,255,255,0.85)' }}>{hub.role}</Text>
            <Text size={200} style={{ color: 'rgba(255,255,255,0.7)', fontFamily: 'monospace' }}>
              {agentJobCounts.get(hub.id) ?? 0} routed
            </Text>
          </div>
          {spokes[4] && (() => {
            const agent = spokes[4]
            const st = agentStatus(agent.id)
            return (
              <div key={agent.id} className={styles.spokeNode}>
                <Text weight="semibold" size={300}>{agent.label}</Text>
                <div className={styles.statusRow}>
                  <span className={styles.statusDot} style={{ backgroundColor: dotColor(st) }} />
                  <span className={styles.spokeRole}>{agent.role}</span>
                </div>
                <span className={styles.spokeStats}>
                  {agentJobCounts.get(agent.id) ?? 0} jobs
                </span>
                {agentLastActivity.get(agent.id) && (
                  <span className={styles.spokeStats}>
                    {formatTime(agentLastActivity.get(agent.id)!)}
                  </span>
                )}
              </div>
            )
          })()}

          {/* Row 3: remaining spoke */}
          <div style={{ gridColumn: '2' }}>
            {spokes[5] && (() => {
              const agent = spokes[5]
              const st = agentStatus(agent.id)
              return (
                <div key={agent.id} className={styles.spokeNode} style={{ margin: '0 auto' }}>
                  <Text weight="semibold" size={300}>{agent.label}</Text>
                  <div className={styles.statusRow}>
                    <span className={styles.statusDot} style={{ backgroundColor: dotColor(st) }} />
                    <span className={styles.spokeRole}>{agent.role}</span>
                  </div>
                  <span className={styles.spokeStats}>
                    {agentJobCounts.get(agent.id) ?? 0} jobs
                  </span>
                  {agentLastActivity.get(agent.id) && (
                    <span className={styles.spokeStats}>
                      {formatTime(agentLastActivity.get(agent.id)!)}
                    </span>
                  )}
                </div>
              )
            })()}
          </div>
        </div>
      </Card>

      {/* Agent Graph (ECharts force-directed) */}
      <Card className={styles.topologyCard}>
        <Text as="h2" size={500} weight="semibold" className={styles.topologyTitle}>
          Agent Network Graph
        </Text>
        <AgentGraph
          nodes={[
            ...AGENTS.map((agent) => ({
              name: agent.label,
              status: agentStatus(agent.id) === 'green' ? 'live' : agentStatus(agent.id) === 'yellow' ? 'degraded' : 'down',
              category: agent.role,
              messageCount: agentJobCounts.get(agent.id) ?? 0,
            })),
            ...(msServices?.length ? MS_CLOUD_AGENTS.map((agent) => ({
              name: agent.label,
              status: 'live' as const,
              category: agent.role,
              messageCount: 0,
            })) : []),
          ]}
          edges={[
            ...spokes.map((agent) => ({
              source: hub.label,
              target: agent.label,
              label: agent.role,
            })),
            ...(msServices?.length ? MS_CLOUD_EDGES : []),
          ]}
          height={500}
        />
      </Card>

      {/* Task bus table */}
      <Card className={styles.tableCard}>
        <Text as="h2" size={500} weight="semibold" style={{ marginBottom: tokens.spacingVerticalM }}>
          Task Bus Queue
        </Text>
        <Table aria-label="Task bus jobs">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Source</TableHeaderCell>
              <TableHeaderCell>Job Type</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Priority</TableHeaderCell>
              <TableHeaderCell>Created</TableHeaderCell>
              <TableHeaderCell>Duration</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.id}>
                <TableCell>
                  <Text
                    weight="semibold"
                    size={200}
                    style={{ color: sourceColor(job.source) }}
                  >
                    {job.source}
                  </Text>
                </TableCell>
                <TableCell>
                  <Text font="monospace" size={200}>{job.jobType}</Text>
                </TableCell>
                <TableCell>
                  <Badge
                    appearance="filled"
                    color={statusColor(job.status)}
                  >
                    {job.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Text size={200}>{job.priority}</Text>
                </TableCell>
                <TableCell>
                  <Text size={200}>{formatTime(job.createdAt)}</Text>
                </TableCell>
                <TableCell>
                  <Text font="monospace" size={200}>
                    {formatDuration(job.createdAt, job.updatedAt)}
                  </Text>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  )
}
