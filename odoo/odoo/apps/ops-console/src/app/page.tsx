'use client'

import {
  makeStyles,
  tokens,
  Text,
  Badge,
  Spinner,
} from '@fluentui/react-components'
import {
  Sparkle24Filled,
} from '@fluentui/react-icons'
import { StatCard } from '@/components/cards/stat-card'
import { DomainChart } from '@/components/cards/domain-chart'
import { ActivityFeed } from '@/components/cards/activity-feed'
import { QuickActions } from '@/components/cards/quick-actions'
import { ReadinessGauge } from '@/components/charts/readiness-gauge'
import { DomainBars } from '@/components/charts/domain-bars'
import { useEval, useServices, useKnowledgeBases, useOdoosh, useMicrosoftCloud } from '@/lib/hooks'
import { getDomainMaturity, getDomainLabel } from '@/lib/providers'
import type { CapabilityDomain } from '@/lib/providers'
import {
  copilotEvalData as fallbackEvalData,
  services as fallbackServices,
  knowledgeBases as fallbackKBs,
  formatScore,
  countByStatus,
} from '@/lib/data'

const useStyles = makeStyles({
  page: {
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
    maxWidth: '1400px',
  },
  welcomeBanner: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    animation: 'copilotSlideUp 500ms cubic-bezier(0.33, 0, 0.67, 1) both',
  },
  sparkleIcon: {
    color: '#7B2FF2',
    display: 'flex',
    alignItems: 'center',
    flexShrink: 0,
  },
  titleGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  pageTitle: {
    fontWeight: tokens.fontWeightSemibold,
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  subtitle: {
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightRegular,
  },
  sourceBadge: {
    fontSize: tokens.fontSizeBase100,
  },
  statsRow: {
    display: 'flex',
    gap: '20px',
    flexWrap: 'wrap',
  },
  gaugeRow: {
    display: 'flex',
    gap: '20px',
    flexWrap: 'wrap',
    alignItems: 'flex-start',
  },
  gaugeCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    padding: '16px',
    borderRadius: '12px',
    border: '1px solid #E8E8E8',
    backgroundColor: '#FAFAFA',
    minWidth: '220px',
  },
  providerBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  contentRow: {
    display: 'flex',
    gap: '20px',
    flexWrap: 'wrap',
    alignItems: 'flex-start',
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },
})

export default function OverviewPage() {
  const styles = useStyles()
  const { eval: evalData, isLoading: evalLoading, source: evalSource } = useEval()
  const { services, isLoading: svcLoading, source: svcSource } = useServices()
  const { knowledgeBases, isLoading: kbLoading, source: kbSource } = useKnowledgeBases()

  const { summary: odooshSummary } = useOdoosh()
  const { services: msServices, health: msHealth, isLoading: msLoading } = useMicrosoftCloud()

  const isLoading = evalLoading || svcLoading || kbLoading

  // Microsoft Cloud domain maturity for DomainBars
  const msDomainMaturity = msServices?.length
    ? getDomainMaturity(msServices)
    : null
  const msDomainBarsData = msDomainMaturity
    ? (Object.entries(msDomainMaturity) as [CapabilityDomain, number][]).map(([d, v]) => ({
        domain: getDomainLabel(d),
        score: v,
      }))
    : []

  const displayEval = evalData ?? fallbackEvalData
  const displayServices = services.length > 0 ? services : fallbackServices
  const displayKBs = knowledgeBases.length > 0 ? knowledgeBases : fallbackKBs

  const liveServices = countByStatus(displayServices, 'live')
  const operationalKBs = countByStatus(displayKBs, 'operational')

  const primarySource = evalSource !== 'loading' ? evalSource : svcSource !== 'loading' ? svcSource : kbSource

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading overview..." size="large" />
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className={styles.welcomeBanner}>
        <span className={styles.sparkleIcon}>
          <Sparkle24Filled />
        </span>
        <div className={styles.titleGroup}>
          <div className={styles.titleRow}>
            <Text className={styles.pageTitle} size={700}>
              Copilot Ops Console
            </Text>
            <Badge
              appearance="outline"
              color={primarySource === 'live' ? 'success' : 'warning'}
              className={styles.sourceBadge}
            >
              Source: {primarySource}
            </Badge>
          </div>
          <Text className={styles.subtitle} size={300} block>
            Agent development readiness and platform health
          </Text>
        </div>
      </div>

      <div className={styles.statsRow}>
        <StatCard
          title="Agent Readiness"
          value={formatScore(displayEval.overall_score)}
          label={`Maturity: ${displayEval.maturity_band}`}
          badge={{
            text: displayEval.release_blocked ? 'Blocked' : 'Clear',
            color: displayEval.release_blocked ? 'danger' : 'success',
          }}
          accent
        />
        <StatCard
          title="Active Services"
          value={liveServices}
          label={`${displayServices.length} total configured`}
          badge={{ text: 'Healthy', color: 'success' }}
        />
        <StatCard
          title="KB Coverage"
          value={`${operationalKBs}/${displayKBs.length}`}
          label="Knowledge bases operational"
          badge={{
            text: operationalKBs === displayKBs.length ? 'Complete' : 'Partial',
            color: operationalKBs === displayKBs.length ? 'success' : 'warning',
          }}
        />
        <StatCard
          title="Release Blockers"
          value={displayEval.blockers.length}
          label="Domains below threshold"
          badge={{ text: 'Action needed', color: 'danger' }}
        />
      </div>

      <div className={styles.gaugeRow}>
        <div className={styles.gaugeCard}>
          <ReadinessGauge score={displayEval.overall_score} label="Agent Readiness" height={180} />
        </div>
        {odooshSummary?.health && (
          <div className={styles.gaugeCard}>
            <div className={styles.providerBadge}>
              <Badge
                appearance="filled"
                color={odooshSummary.health.status === 'healthy' ? 'success' : odooshSummary.health.status === 'degraded' ? 'warning' : 'danger'}
              >
                {odooshSummary.config?.name ?? 'Odoo.sh'}: {odooshSummary.health.status}
              </Badge>
            </div>
            <Text size={200}>
              {odooshSummary.health.components?.length ?? 0} components checked
            </Text>
          </div>
        )}
        {msHealth && (
          <div className={styles.gaugeCard}>
            <div className={styles.providerBadge}>
              <Badge
                appearance="filled"
                color={msHealth.status === 'healthy' ? 'success' : msHealth.status === 'degraded' ? 'warning' : 'danger'}
              >
                Microsoft Cloud: {msHealth.status}
              </Badge>
            </div>
            <Text size={200}>
              {msServices?.length ?? 0} services | {msHealth.components?.length ?? 0} components
            </Text>
          </div>
        )}
      </div>

      {msDomainBarsData.length > 0 && (
        <div>
          <Text weight="semibold" size={500} style={{ marginBottom: '12px', display: 'block' }}>
            Microsoft Cloud Domain Maturity
          </Text>
          <DomainBars scores={msDomainBarsData} height={240} />
        </div>
      )}

      <div className={styles.contentRow}>
        <DomainChart />
        <ActivityFeed />
      </div>

      <QuickActions />
    </div>
  )
}
