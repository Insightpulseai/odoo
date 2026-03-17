'use client';

import {
  Card,
  Text,
  Badge,
  Button,
  Spinner,
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  ProgressBar,
  makeStyles,
  tokens,
  mergeClasses,
} from '@fluentui/react-components';
import { ArrowSyncRegular } from '@fluentui/react-icons';
import { StatusBadge, type StatusLevel } from '@/components/ui/status-badge';
import { ServiceHeatmap } from '@/components/charts/service-heatmap';
import { useServices, useMicrosoftCloud } from '@/lib/hooks';
import { getDomainLabel } from '@/lib/providers';
import { services as fallbackServices } from '@/lib/data';

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
  meta: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
  },
  checkedAt: {
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  sourceBadge: {
    fontSize: tokens.fontSizeBase100,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
    gap: tokens.spacingHorizontalL,
  },
  serviceCard: {
    padding: tokens.spacingVerticalL,
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  cardTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  nameRow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  healthDot: {
    width: '8px',
    height: '8px',
    borderRadius: tokens.borderRadiusCircular,
    display: 'inline-block',
    flexShrink: 0,
  },
  healthLive: {
    backgroundColor: tokens.colorPaletteGreenBackground2,
    boxShadow: `0 0 6px ${tokens.colorPaletteGreenBackground2}`,
  },
  healthStub: {
    backgroundColor: tokens.colorPaletteYellowBackground2,
  },
  healthScaffolded: {
    backgroundColor: tokens.colorPaletteBerryBackground2,
  },
  endpoint: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailLabel: {
    color: tokens.colorNeutralForeground3,
  },
  typeBadge: {
    fontFamily: tokens.fontFamilyMonospace,
    textTransform: 'uppercase',
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground2,
    backgroundColor: tokens.colorNeutralBackground3,
    padding: `${tokens.spacingVerticalXXS} ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusSmall,
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },
  sectionTitle: {
    marginBottom: tokens.spacingVerticalM,
    marginTop: tokens.spacingVerticalXXL,
  },
  msTable: {
    padding: tokens.spacingVerticalL,
  },
  maturityBar: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    minWidth: '120px',
  },
  maturityFill: {
    height: '8px',
    borderRadius: '4px',
    backgroundColor: tokens.colorBrandBackground,
  },
  maturityTrack: {
    height: '8px',
    borderRadius: '4px',
    backgroundColor: tokens.colorNeutralBackground5,
    flex: 1,
    overflow: 'hidden',
  },
});

function msStatusToLevel(status: string): StatusLevel {
  if (status === 'operational') return 'live';
  if (status === 'partial' || status === 'degraded') return 'partial';
  if (status === 'down') return 'stub';
  return 'scaffolded';
}

export default function ServicesPage() {
  const styles = useStyles();
  const { services, checkedAt, source, isLoading, refresh } = useServices();
  const { services: msServices, isLoading: msLoading } = useMicrosoftCloud();

  const displayServices = services.length > 0 ? services : fallbackServices;

  const getHealthDotClass = (status: string) => {
    if (status === 'live') return styles.healthLive;
    if (status === 'stub') return styles.healthStub;
    return styles.healthScaffolded;
  };

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading services..." size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <Text as="h1" size={800} weight="bold">
            Platform Services
          </Text>
          <div className={styles.meta}>
            {checkedAt && (
              <Text className={styles.checkedAt}>
                Checked: {new Date(checkedAt).toLocaleTimeString()}
              </Text>
            )}
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
              aria-label="Refresh services"
            >
              Refresh
            </Button>
          </div>
        </div>
        <Text className={styles.subtitle} size={400}>
          Service inventory and health status across the IPAI platform
        </Text>
      </div>

      <ServiceHeatmap
        services={displayServices.map((svc) => ({
          name: svc.name,
          status: svc.status,
        }))}
        height={140}
      />

      <div className={styles.grid}>
        {displayServices.map((svc) => (
          <Card key={svc.name} className={styles.serviceCard}>
            <div className={styles.cardTop}>
              <div className={styles.nameRow}>
                <span className={mergeClasses(styles.healthDot, getHealthDotClass(svc.status))} />
                <Text weight="bold" size={400}>
                  {svc.name}
                </Text>
              </div>
              <StatusBadge status={svc.status as StatusLevel} size="small" />
            </div>
            <Text className={styles.endpoint}>{svc.endpoint}</Text>
            <div className={styles.detailRow}>
              <Text size={200} className={styles.detailLabel}>Type</Text>
              <span className={styles.typeBadge}>{svc.type}</span>
            </div>
          </Card>
        ))}
      </div>

      {/* Microsoft Cloud Services */}
      {msServices?.length > 0 && (
        <div>
          <Text weight="semibold" size={600} className={styles.sectionTitle} as="h2">
            Microsoft Cloud Services
          </Text>
          <Card className={styles.msTable}>
            <Table aria-label="Microsoft Cloud services table">
              <TableHeader>
                <TableRow>
                  <TableHeaderCell>Name</TableHeaderCell>
                  <TableHeaderCell>Domain</TableHeaderCell>
                  <TableHeaderCell>Status</TableHeaderCell>
                  <TableHeaderCell>Maturity</TableHeaderCell>
                  <TableHeaderCell>Last Sync</TableHeaderCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {msServices.map((svc) => (
                  <TableRow key={svc.id}>
                    <TableCell>
                      <Text weight="semibold">{svc.displayName}</Text>
                    </TableCell>
                    <TableCell>
                      <Badge appearance="outline" color="informative">
                        {getDomainLabel(svc.domain)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={msStatusToLevel(svc.status)} size="small" />
                    </TableCell>
                    <TableCell>
                      <div className={styles.maturityBar}>
                        <div className={styles.maturityTrack}>
                          <div
                            className={styles.maturityFill}
                            style={{ width: `${Math.round((svc.maturityScore ?? 0) * 100)}%` }}
                          />
                        </div>
                        <Text size={200}>{Math.round((svc.maturityScore ?? 0) * 100)}%</Text>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>
                        {svc.lastSync ? new Date(svc.lastSync).toLocaleString() : '-'}
                      </Text>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>
      )}
      {msLoading && (
        <Spinner label="Loading Microsoft Cloud services..." size="small" />
      )}
    </div>
  );
}
