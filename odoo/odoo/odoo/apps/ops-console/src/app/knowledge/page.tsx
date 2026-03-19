'use client';

import {
  Card,
  Text,
  Badge,
  ProgressBar,
  Spinner,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  BookRegular,
  DocumentRegular,
} from '@fluentui/react-icons';
import { StatusBadge, type StatusLevel } from '@/components/ui/status-badge';
import { KBTreemap } from '@/components/charts/kb-treemap';
import { useKnowledgeBases, useMicrosoftCloud } from '@/lib/hooks';
import { knowledgeBases as fallbackKBs } from '@/lib/data';

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
  subtitle: {
    color: tokens.colorNeutralForeground3,
  },
  sourceBadge: {
    fontSize: tokens.fontSizeBase100,
  },
  sectionTitle: {
    marginBottom: tokens.spacingVerticalM,
  },
  kbGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: tokens.spacingHorizontalL,
  },
  kbCard: {
    padding: tokens.spacingVerticalL,
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  kbHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  kbNameRow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  kbIcon: {
    fontSize: '20px',
    color: tokens.colorBrandForeground1,
  },
  detailGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: tokens.spacingVerticalXS,
  },
  detailItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  detailLabel: {
    color: tokens.colorNeutralForeground3,
  },
  detailValue: {
    fontVariantNumeric: 'tabular-nums',
  },
  progressSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
  },
  coverageGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
    gap: tokens.spacingHorizontalS,
  },
  coverageCard: {
    padding: tokens.spacingVerticalS,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: tokens.spacingVerticalXS,
  },
  coverageName: {
    textAlign: 'center',
    fontSize: tokens.fontSizeBase200,
  },
  coverageSection: {
    marginTop: tokens.spacingVerticalL,
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },
});

interface CoverageBucket {
  name: string;
  status: StatusLevel;
}

const foundryBuckets: CoverageBucket[] = [
  { name: 'Core ERP', status: 'operational' },
  { name: 'Accounting', status: 'operational' },
  { name: 'Sales & CRM', status: 'operational' },
  { name: 'HR & Payroll', status: 'partial' },
  { name: 'Project Mgmt', status: 'partial' },
  { name: 'Inventory', status: 'partial' },
  { name: 'BIR/Tax', status: 'partial' },
  { name: 'Documents', status: 'scaffolded' },
  { name: 'Knowledge', status: 'scaffolded' },
  { name: 'AI/ML Tools', status: 'scaffolded' },
  { name: 'DevOps/CI', status: 'scaffolded' },
  { name: 'Integrations', status: 'missing' },
];

function freshnessToStatus(freshness: string): StatusLevel {
  if (freshness === 'fresh') return 'operational';
  if (freshness === 'stale') return 'partial';
  return 'missing';
}

export default function KnowledgePage() {
  const styles = useStyles();
  const { knowledgeBases, source, isLoading } = useKnowledgeBases();
  const { kbCoverage: msKbCoverage, isLoading: msKbLoading } = useMicrosoftCloud();

  const displayKBs = knowledgeBases.length > 0 ? knowledgeBases : fallbackKBs;

  // Merge Microsoft Cloud KB coverage into treemap data
  const msTreemapEntries = (msKbCoverage ?? []).map((kb) => ({
    name: kb.name,
    chunks: kb.indexed,
    status: freshnessToStatus(kb.freshness),
  }));

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading knowledge bases..." size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <Text as="h1" size={800} weight="bold">
            Knowledge Bases
          </Text>
          <Badge
            appearance="outline"
            color={source === 'live' ? 'success' : 'warning'}
            className={styles.sourceBadge}
          >
            Source: {source}
          </Badge>
        </div>
        <Text className={styles.subtitle} size={400}>
          Knowledge base indexes, chunk counts, and content coverage
        </Text>
      </div>

      <KBTreemap
        knowledgeBases={[
          ...displayKBs.map((kb) => ({
            name: kb.name,
            chunks: kb.chunks,
            status: kb.status,
          })),
          ...msTreemapEntries,
        ]}
        height={280}
      />

      <div className={styles.kbGrid}>
        {displayKBs.map((kb) => {
          const maturity = (kb as unknown as Record<string, unknown>).maturity as number | undefined;
          const sources = (kb as unknown as Record<string, unknown>).sources as number | undefined;
          return (
            <Card key={kb.name} className={styles.kbCard}>
              <div className={styles.kbHeader}>
                <div className={styles.kbNameRow}>
                  <BookRegular className={styles.kbIcon} />
                  <Text weight="bold" size={400}>
                    {kb.name}
                  </Text>
                </div>
                <StatusBadge status={kb.status as StatusLevel} size="small" />
              </div>

              <Text font="monospace" size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                {kb.index}
              </Text>

              <div className={styles.detailGrid}>
                <div className={styles.detailItem}>
                  <Text size={100} className={styles.detailLabel}>Chunks</Text>
                  <Text size={300} weight="semibold" className={styles.detailValue}>
                    {kb.chunks.toLocaleString()}
                  </Text>
                </div>
                {sources !== undefined && (
                  <div className={styles.detailItem}>
                    <Text size={100} className={styles.detailLabel}>Sources</Text>
                    <Text size={300} weight="semibold" className={styles.detailValue}>
                      {sources}
                    </Text>
                  </div>
                )}
                <div className={styles.detailItem}>
                  <Text size={100} className={styles.detailLabel}>Last Refresh</Text>
                  <Text size={200} className={styles.detailValue}>
                    {kb.lastRefresh ?? 'Never'}
                  </Text>
                </div>
              </div>

              {maturity !== undefined && (
                <div className={styles.progressSection}>
                  <Text size={100} className={styles.detailLabel}>Maturity</Text>
                  <ProgressBar
                    value={maturity}
                    thickness="large"
                    color={
                      maturity >= 0.7
                        ? 'success'
                        : maturity >= 0.4
                          ? 'warning'
                          : 'error'
                    }
                  />
                  <Text size={100} style={{ textAlign: 'right', color: tokens.colorNeutralForeground3 }}>
                    {Math.round(maturity * 100)}%
                  </Text>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      <div className={styles.coverageSection}>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          <DocumentRegular style={{ marginRight: tokens.spacingHorizontalS }} />
          Foundry Documentation Coverage
        </Text>
        <div className={styles.coverageGrid}>
          {foundryBuckets.map((bucket) => (
            <Card key={bucket.name} className={styles.coverageCard}>
              <Text weight="semibold" className={styles.coverageName}>
                {bucket.name}
              </Text>
              <StatusBadge status={bucket.status} size="small" />
            </Card>
          ))}
        </div>
      </div>

      {(msKbCoverage?.length ?? 0) > 0 && (
        <div className={styles.coverageSection}>
          <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
            <DocumentRegular style={{ marginRight: tokens.spacingHorizontalS }} />
            Microsoft Cloud KB Coverage
          </Text>
          <div className={styles.coverageGrid}>
            {msKbCoverage!.map((kb) => (
              <Card key={kb.name} className={styles.coverageCard}>
                <Text weight="semibold" className={styles.coverageName}>
                  {kb.name}
                </Text>
                <ProgressBar
                  value={kb.total > 0 ? kb.indexed / kb.total : 0}
                  thickness="large"
                  color={kb.freshness === 'fresh' ? 'success' : kb.freshness === 'stale' ? 'warning' : 'error'}
                  style={{ width: '100%' }}
                />
                <Text size={100} style={{ color: tokens.colorNeutralForeground3 }}>
                  {kb.indexed}/{kb.total} indexed
                </Text>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
