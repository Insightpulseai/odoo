'use client'

import {
  Card,
  CardHeader,
  Text,
  Badge,
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  ProgressBar,
  Divider,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components'
import {
  CheckmarkCircleFilled,
  WarningFilled,
  DismissCircleFilled,
  RocketRegular,
  ShieldCheckmarkFilled,
  ArrowTrendingFilled,
  ErrorCircleFilled,
} from '@fluentui/react-icons'
import { StatusBadge } from '@/components/ui/status-badge'
import { DomainBars } from '@/components/charts/domain-bars'
import { useMicrosoftCloud } from '@/lib/hooks'
import { getDomainMaturity, getDomainLabel } from '@/lib/providers'
import type { CapabilityDomain } from '@/lib/providers'
import {
  DOMAIN_SCORES,
  RELEASE_BLOCKERS,
  REMEDIATION_ACTIONS,
  BENCHMARK_DIMENSIONS,
  computeOverallScore,
  scoreToMaturity,
  maturityLabel,
  timeAgo,
} from '@/lib/leaderboard-data'
import type { DomainMaturityRow, ReleaseBlocker, RemediationAction } from '@/lib/leaderboard-data'

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
  subtitle: {
    color: tokens.colorNeutralForeground3,
  },
  overviewRow: {
    display: 'grid',
    gridTemplateColumns: '280px 1fr',
    gap: tokens.spacingHorizontalXXL,
    alignItems: 'start',
  },
  scoreCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: tokens.spacingVerticalXXL,
    gap: tokens.spacingVerticalM,
  },
  ringContainer: {
    position: 'relative',
    width: '160px',
    height: '160px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  ringSvg: {
    width: '160px',
    height: '160px',
    transform: 'rotate(-90deg)',
  },
  ringTrack: {
    fill: 'none',
    strokeWidth: '12',
  },
  ringFill: {
    fill: 'none',
    strokeWidth: '12',
    strokeLinecap: 'round',
    transitionProperty: 'stroke-dashoffset',
    transitionDuration: tokens.durationUltraSlow,
    transitionTimingFunction: tokens.curveDecelerateMax,
  },
  ringLabel: {
    position: 'absolute',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  ringValue: {
    fontSize: tokens.fontSizeHero900,
    fontWeight: tokens.fontWeightBold,
    lineHeight: tokens.lineHeightHero900,
  },
  ringUnit: {
    color: tokens.colorNeutralForeground3,
  },
  badgeRow: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  chartCard: {
    padding: tokens.spacingVerticalL,
  },
  tableCard: {
    padding: tokens.spacingVerticalL,
  },
  sectionTitle: {
    marginBottom: tokens.spacingVerticalM,
  },
  sectionDivider: {
    marginTop: tokens.spacingVerticalL,
    marginBottom: tokens.spacingVerticalS,
  },
  iconSuccess: {
    color: tokens.colorPaletteGreenForeground1,
  },
  iconWarning: {
    color: tokens.colorPaletteYellowForeground1,
  },
  iconError: {
    color: tokens.colorPaletteRedForeground1,
  },
  progressCell: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    minWidth: '120px',
  },
  trendPositive: {
    color: tokens.colorPaletteGreenForeground1,
    fontSize: tokens.fontSizeBase200,
    fontVariantNumeric: 'tabular-nums',
  },
  trendNegative: {
    color: tokens.colorPaletteRedForeground1,
    fontSize: tokens.fontSizeBase200,
    fontVariantNumeric: 'tabular-nums',
  },
  trendNeutral: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  evidenceText: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
    fontVariantNumeric: 'tabular-nums',
  },
  blockerCard: {
    padding: tokens.spacingVerticalM,
    marginBottom: tokens.spacingVerticalS,
    borderLeft: `4px solid ${tokens.colorPaletteRedBorder2}`,
  },
  blockerHigh: {
    borderLeft: `4px solid ${tokens.colorPaletteYellowBorder1}`,
  },
  blockerMedium: {
    borderLeft: `4px solid ${tokens.colorNeutralStroke1}`,
  },
  blockerHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
    marginBottom: tokens.spacingVerticalXS,
  },
  blockerMeta: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
    marginTop: tokens.spacingVerticalXS,
  },
  metaItem: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  actionCard: {
    padding: tokens.spacingVerticalM,
    marginBottom: tokens.spacingVerticalS,
  },
  actionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
  },
  actionLift: {
    color: tokens.colorPaletteGreenForeground1,
    fontWeight: tokens.fontWeightSemibold,
    fontVariantNumeric: 'tabular-nums',
  },
  actionMeta: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
    marginTop: tokens.spacingVerticalXS,
  },
  benchmarkGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  benchmarkItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    padding: tokens.spacingVerticalS,
  },
  benchmarkLabel: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
  benchmarkScore: {
    display: 'flex',
    alignItems: 'baseline',
    gap: tokens.spacingHorizontalXS,
  },
  thresholdLegend: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
    padding: `${tokens.spacingVerticalS} 0`,
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXXS,
    fontSize: tokens.fontSizeBase200,
  },
  legendDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    display: 'inline-block',
  },
})

// --- Ring color by maturity ---
function ringColor(score: number): string {
  const pct = Math.round(score * 100)
  if (pct >= 90) return '#0E7A0D'
  if (pct >= 75) return tokens.colorPaletteGreenBorder1
  if (pct >= 50) return tokens.colorPaletteYellowBorder1
  if (pct >= 25) return '#CA5010'
  return tokens.colorPaletteRedBorder1
}

// --- Progress bar color ---
function maturityBarColor(score: number): 'success' | 'warning' | 'error' | 'brand' {
  const pct = Math.round(score * 100)
  if (pct >= 75) return 'success'
  if (pct >= 50) return 'warning'
  if (pct >= 25) return 'brand'
  return 'error'
}

const CIRCUMFERENCE = 2 * Math.PI * 62

export default function LeaderboardPage() {
  const styles = useStyles()
  const { services: msServices, isLoading: msLoading } = useMicrosoftCloud()

  const overallScore = computeOverallScore(DOMAIN_SCORES)
  const overallMaturity = scoreToMaturity(overallScore)
  const dashOffset = CIRCUMFERENCE * (1 - overallScore)
  const openBlockers = RELEASE_BLOCKERS.filter(b => b.status !== 'resolved')

  // Microsoft Cloud domain maturity for DomainBars
  const msDomainMaturity = msServices?.length ? getDomainMaturity(msServices) : null
  const msDomainBarsData = msDomainMaturity
    ? (Object.entries(msDomainMaturity) as [CapabilityDomain, number][]).map(([d, v]) => {
        // Find services in this domain for evidence counts
        const domainSvcs = msServices.filter(s => s.domain === d)
        const evidenceTotal = domainSvcs.length
        const evidencePassed = domainSvcs.filter(s => s.status === 'operational').length
        return {
          domain: getDomainLabel(d),
          score: v,
          maturity: scoreToMaturity(v),
          evidencePassed,
          evidenceTotal,
        }
      })
    : []

  // Sort actions by expected lift descending
  const rankedActions = [...REMEDIATION_ACTIONS].sort((a, b) => b.expectedLift - a.expectedLift)

  return (
    <div className={styles.page}>
      {/* ===== SECTION 1: CAPABILITY MATURITY LEADERBOARD ===== */}
      <div className={styles.header}>
        <Text as="h1" size={800} weight="bold">
          Capability Maturity Leaderboard
        </Text>
        <Text className={styles.subtitle} size={400}>
          Auditable maturity scoring across platform domains
        </Text>
      </div>

      {/* Threshold legend */}
      <div className={styles.thresholdLegend}>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ backgroundColor: tokens.colorPaletteRedBackground2 }} />
          Missing (0-24)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ backgroundColor: '#CA5010' }} />
          Scaffolded (25-49)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ backgroundColor: tokens.colorPaletteYellowBackground2 }} />
          Partial (50-74)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ backgroundColor: tokens.colorPaletteGreenBackground2 }} />
          Operational (75-89)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ backgroundColor: '#0E7A0D' }} />
          Hardened (90-100)
        </span>
      </div>

      <div className={styles.overviewRow}>
        {/* Overall ring */}
        <Card className={styles.scoreCard}>
          <div className={styles.ringContainer}>
            <svg className={styles.ringSvg} viewBox="0 0 140 140">
              <circle
                className={styles.ringTrack}
                cx="70" cy="70" r="62"
                stroke={tokens.colorNeutralBackground5}
              />
              <circle
                className={styles.ringFill}
                cx="70" cy="70" r="62"
                stroke={ringColor(overallScore)}
                strokeDasharray={CIRCUMFERENCE}
                strokeDashoffset={dashOffset}
              />
            </svg>
            <div className={styles.ringLabel}>
              <Text className={styles.ringValue}>
                {Math.round(overallScore * 100)}
              </Text>
              <Text className={styles.ringUnit} size={200}>/ 100</Text>
            </div>
          </div>
          <div className={styles.badgeRow}>
            <StatusBadge status={overallMaturity} label={maturityLabel(overallMaturity)} />
            {openBlockers.length > 0 && (
              <Badge appearance="filled" color="danger">
                {openBlockers.length} BLOCKER{openBlockers.length > 1 ? 'S' : ''}
              </Badge>
            )}
          </div>
          <Text size={200} align="center" style={{ color: tokens.colorNeutralForeground3 }}>
            Weighted across {DOMAIN_SCORES.length} domains
          </Text>
        </Card>

        {/* Domain bars chart with provenance */}
        <Card className={styles.chartCard}>
          <Text weight="semibold" size={400} className={styles.sectionTitle} as="h3">
            Domain Scores
          </Text>
          <DomainBars
            scores={DOMAIN_SCORES.map(r => ({
              domain: r.domain,
              score: r.score,
              maturity: maturityLabel(scoreToMaturity(r.score)),
              evidencePassed: r.evidencePassed,
              evidenceTotal: r.evidenceTotal,
              trend: r.trend,
            }))}
            height={320}
          />
        </Card>
      </div>

      {/* Detailed scores table with provenance */}
      <Card className={styles.tableCard}>
        <Text weight="semibold" size={400} className={styles.sectionTitle} as="h3">
          Detailed Scores
        </Text>
        <Table aria-label="Domain maturity scores with provenance">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Domain</TableHeaderCell>
              <TableHeaderCell>Score</TableHeaderCell>
              <TableHeaderCell>Maturity</TableHeaderCell>
              <TableHeaderCell>Evidence</TableHeaderCell>
              <TableHeaderCell>Last Eval</TableHeaderCell>
              <TableHeaderCell>Trend</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {DOMAIN_SCORES.map((row) => {
              const level = scoreToMaturity(row.score)
              return (
                <TableRow key={row.id}>
                  <TableCell>
                    <Text weight="semibold">{row.domain}</Text>
                  </TableCell>
                  <TableCell>
                    <div className={styles.progressCell}>
                      <ProgressBar
                        value={row.score}
                        thickness="large"
                        color={maturityBarColor(row.score)}
                        style={{ flex: 1 }}
                      />
                      <Text size={200}>{Math.round(row.score * 100)}%</Text>
                    </div>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={level} label={maturityLabel(level)} size="small" />
                  </TableCell>
                  <TableCell>
                    <Text className={styles.evidenceText}>
                      {row.evidencePassed}/{row.evidenceTotal} checks
                    </Text>
                  </TableCell>
                  <TableCell>
                    <Text className={styles.evidenceText}>
                      {timeAgo(row.lastEvaluated)}
                    </Text>
                  </TableCell>
                  <TableCell>
                    {row.trend > 0 ? (
                      <Text className={styles.trendPositive}>+{Math.round(row.trend * 100)}%</Text>
                    ) : row.trend < 0 ? (
                      <Text className={styles.trendNegative}>{Math.round(row.trend * 100)}%</Text>
                    ) : (
                      <Text className={styles.trendNeutral}>--</Text>
                    )}
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </Card>

      {/* Microsoft Cloud maturity — derived from normalized services */}
      {msDomainBarsData.length > 0 && (
        <Card className={styles.chartCard}>
          <Text weight="semibold" size={400} className={styles.sectionTitle} as="h3">
            Platform Maturity (Microsoft Cloud)
          </Text>
          <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginBottom: tokens.spacingVerticalS }}>
            Derived from {msServices.length} services across {msDomainBarsData.length} capability domains
          </Text>
          <DomainBars
            scores={msDomainBarsData.map(d => ({
              ...d,
              maturity: maturityLabel(scoreToMaturity(d.score)),
            }))}
            height={280}
          />
        </Card>
      )}

      {/* Odoo Copilot Benchmark */}
      <Card className={styles.tableCard}>
        <Text weight="semibold" size={400} className={styles.sectionTitle} as="h3">
          <ShieldCheckmarkFilled style={{ marginRight: tokens.spacingHorizontalS }} />
          Odoo Copilot Benchmark
        </Text>
        <div className={styles.benchmarkGrid}>
          {BENCHMARK_DIMENSIONS.map(dim => (
            <div key={dim.id} className={styles.benchmarkItem}>
              <Text className={styles.benchmarkLabel}>{dim.label}</Text>
              <div className={styles.benchmarkScore}>
                <Text weight="bold" size={500}>{dim.score}</Text>
                <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>/ {dim.maxScore}</Text>
                {dim.trend > 0 ? (
                  <Text className={styles.trendPositive}>+{dim.trend}</Text>
                ) : dim.trend < 0 ? (
                  <Text className={styles.trendNegative}>{dim.trend}</Text>
                ) : null}
              </div>
              <ProgressBar
                value={dim.score / dim.maxScore}
                thickness="large"
                color={maturityBarColor(dim.score / dim.maxScore)}
              />
            </div>
          ))}
        </div>
      </Card>

      {/* ===== SECTION 2: RELEASE READINESS ===== */}
      <Divider className={styles.sectionDivider} />

      <div className={styles.header}>
        <Text as="h2" size={700} weight="bold">
          Release Readiness
        </Text>
        <Text className={styles.subtitle} size={400}>
          Blockers, remediation actions, and ship criteria
        </Text>
      </div>

      {/* Release Blockers */}
      <div>
        <Text weight="semibold" size={400} className={styles.sectionTitle} as="h3">
          <ErrorCircleFilled style={{ marginRight: tokens.spacingHorizontalS, color: tokens.colorPaletteRedForeground1 }} />
          Release Blockers ({openBlockers.length})
        </Text>
        {RELEASE_BLOCKERS.map((blocker) => {
          const linkedAction = REMEDIATION_ACTIONS.find(a => a.id === blocker.linkedActionId)
          const borderClass = blocker.severity === 'critical'
            ? styles.blockerCard
            : mergeClasses(styles.blockerCard, blocker.severity === 'high' ? styles.blockerHigh : styles.blockerMedium)
          return (
            <Card key={blocker.id} className={borderClass}>
              <div className={styles.blockerHeader}>
                <Text weight="semibold">{blocker.title}</Text>
                <div className={styles.badgeRow}>
                  <Badge
                    appearance="filled"
                    color={blocker.severity === 'critical' ? 'danger' : blocker.severity === 'high' ? 'warning' : 'informative'}
                  >
                    {blocker.severity.toUpperCase()}
                  </Badge>
                  <StatusBadge status={blocker.status === 'in_progress' ? 'in_progress' : blocker.status === 'resolved' ? 'success' : 'error'} label={blocker.status === 'in_progress' ? 'In Progress' : blocker.status === 'resolved' ? 'Resolved' : 'Open'} size="small" />
                </div>
              </div>
              <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                {blocker.evidence}
              </Text>
              <div className={styles.blockerMeta}>
                <Text className={styles.metaItem}>
                  Impacts: {blocker.impactedDomains.map(id => DOMAIN_SCORES.find(d => d.id === id)?.domain ?? id).join(', ')}
                </Text>
                <Text className={styles.metaItem}>Owner: {blocker.owner}</Text>
                {linkedAction && (
                  <Text className={styles.metaItem}>
                    Remediation: {linkedAction.title}
                  </Text>
                )}
              </div>
            </Card>
          )
        })}
      </div>

      {/* Ranked remediation actions */}
      <div>
        <Text weight="semibold" size={400} className={styles.sectionTitle} as="h3">
          <RocketRegular style={{ marginRight: tokens.spacingHorizontalS }} />
          Ranked Remediation Actions
        </Text>
        {rankedActions.map((action, i) => {
          const linkedBlockers = RELEASE_BLOCKERS.filter(b => action.linkedBlockerIds.includes(b.id))
          return (
            <Card key={action.id} className={styles.actionCard}>
              <div className={styles.actionHeader}>
                <Text weight="semibold">
                  #{i + 1} {action.title}
                </Text>
                <div className={styles.badgeRow}>
                  <Text className={styles.actionLift}>
                    +{Math.round(action.expectedLift * 100)}% lift
                  </Text>
                  <StatusBadge
                    status={action.status === 'done' ? 'success' : action.status === 'in_progress' ? 'in_progress' : 'planned'}
                    size="small"
                  />
                </div>
              </div>
              <div className={styles.actionMeta}>
                <Text className={styles.metaItem}>
                  Domains: {action.affectedDomains.map(id => DOMAIN_SCORES.find(d => d.id === id)?.domain ?? id).join(', ')}
                </Text>
                <Text className={styles.metaItem}>Owner: {action.owner}</Text>
                {linkedBlockers.length > 0 && (
                  <Text className={styles.metaItem}>
                    Resolves: {linkedBlockers.map(b => b.title.split(':')[0]).join(', ')}
                  </Text>
                )}
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
