'use client';

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
  Spinner,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  CheckmarkCircleFilled,
  DismissCircleFilled,
  QuestionCircleRegular,
  RocketRegular,
  ClockRegular,
} from '@fluentui/react-icons';
import { PipelineStages, type PipelineStage } from '@/components/ui/pipeline-stages';
import { useDeployments } from '@/lib/hooks';

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
  tableCard: {
    padding: tokens.spacingVerticalL,
  },
  pipelineCard: {
    padding: tokens.spacingVerticalL,
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  statusSuccess: {
    color: tokens.colorPaletteGreenForeground1,
    fontSize: '16px',
  },
  statusPending: {
    color: tokens.colorNeutralForeground3,
    fontSize: '16px',
  },
  statusInProgress: {
    color: tokens.colorPaletteDarkOrangeForeground1,
    fontSize: '16px',
  },
  statusCell: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
  },
  mono: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase200,
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },
  truncated: {
    maxWidth: '180px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
});

interface ContainerImage {
  service: string;
  image: string;
  registry: string;
  lastBuild: string;
  tag: string;
}

const containerImages: ContainerImage[] = [
  { service: 'Odoo Web', image: 'ipai-odoo-web', registry: 'ipaidevacr.azurecr.io', lastBuild: '2026-03-14 22:15', tag: '19.0-latest' },
  { service: 'n8n', image: 'ipai-n8n', registry: 'ipaidevacr.azurecr.io', lastBuild: '2026-03-12 10:30', tag: '1.30.0' },
  { service: 'Keycloak', image: 'ipai-keycloak', registry: 'ipaidevacr.azurecr.io', lastBuild: '2026-03-10 14:00', tag: '24.0.0' },
  { service: 'Superset', image: 'ipai-superset', registry: 'ipaidevacr.azurecr.io', lastBuild: '2026-03-08 09:00', tag: '3.1.0' },
  { service: 'MCP Coordinator', image: 'ipai-mcp', registry: 'ipaidevacr.azurecr.io', lastBuild: '2026-03-05 16:45', tag: '0.1.0' },
  { service: 'OCR Service', image: 'ipai-ocr', registry: 'ipaidevacr.azurecr.io', lastBuild: '2026-02-28 11:20', tag: '0.2.0' },
];

const deploymentStages: PipelineStage[] = [
  { name: 'Build', status: 'completed' },
  { name: 'Push ACR', status: 'completed' },
  { name: 'Deploy ACA', status: 'in-progress' },
  { name: 'Health Check', status: 'pending' },
  { name: 'Verify', status: 'pending' },
];

export default function DeploymentsPage() {
  const styles = useStyles();
  const { deployments, modelAliases, policies, source, isLoading } = useDeployments();

  const StatusIcon = ({ status }: { status: string }) => {
    if (status === 'success' || status === 'prod') return <CheckmarkCircleFilled className={styles.statusSuccess} />;
    if (status === 'in_progress' || status === 'staging') return <ClockRegular className={styles.statusInProgress} />;
    if (status === 'pending' || status === 'dev' || status === 'draft') return <QuestionCircleRegular className={styles.statusPending} />;
    return <QuestionCircleRegular className={styles.statusPending} />;
  };

  const envBadgeColor = (env: string): 'success' | 'warning' | 'informative' | 'subtle' => {
    if (env === 'prod') return 'success';
    if (env === 'staging') return 'warning';
    if (env === 'dev') return 'informative';
    return 'subtle';
  };

  const costTierColor = (tier: string): 'success' | 'warning' | 'important' | 'subtle' => {
    if (tier === 'economy') return 'success';
    if (tier === 'standard') return 'warning';
    if (tier === 'premium') return 'important';
    return 'subtle';
  };

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading deployments..." size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <Text as="h1" size={800} weight="bold">
            Deployment &amp; Governance
          </Text>
          <Badge
            appearance="outline"
            color={source === 'registry' ? 'success' : source === 'error' ? 'danger' : 'warning'}
            className={styles.sourceBadge}
          >
            Source: {source}
          </Badge>
        </div>
        <Text className={styles.subtitle} size={400}>
          Agent promotion state, model aliases, governance policies, and infrastructure
        </Text>
      </div>

      {/* Section 1: Agent Promotion State */}
      <div>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          Agent Promotion State
        </Text>
        <Card className={styles.tableCard}>
          <Table aria-label="Agent promotion state table">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Agent Name</TableHeaderCell>
                <TableHeaderCell>Version</TableHeaderCell>
                <TableHeaderCell>Environment</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell>Model Alias</TableHeaderCell>
                <TableHeaderCell>Owner</TableHeaderCell>
                <TableHeaderCell>Source File</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {deployments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7}>
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                      No agent deployments found in registry
                    </Text>
                  </TableCell>
                </TableRow>
              ) : (
                deployments.map((dep) => (
                  <TableRow key={dep.id}>
                    <TableCell>
                      <Text weight="semibold">{dep.name}</Text>
                    </TableCell>
                    <TableCell>
                      <Text className={styles.mono}>{dep.version}</Text>
                    </TableCell>
                    <TableCell>
                      <Badge appearance="outline" color={envBadgeColor(dep.environment)}>
                        {dep.environment}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className={styles.statusCell}>
                        <StatusIcon status={dep.status} />
                        <Text size={200}>{dep.status}</Text>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Text className={styles.mono}>{dep.modelAlias}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{dep.owner}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200} className={styles.truncated} title={dep.sourceFile}>
                        {dep.sourceFile}
                      </Text>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </div>

      {/* Section 2: Model Aliases */}
      <div>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          Model Aliases
        </Text>
        <Card className={styles.tableCard}>
          <Table aria-label="Model aliases table">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Alias</TableHeaderCell>
                <TableHeaderCell>Current Model</TableHeaderCell>
                <TableHeaderCell>Fallback</TableHeaderCell>
                <TableHeaderCell>Cost Tier</TableHeaderCell>
                <TableHeaderCell>Use Cases</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {modelAliases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5}>
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                      No model aliases found in registry
                    </Text>
                  </TableCell>
                </TableRow>
              ) : (
                modelAliases.map((m) => (
                  <TableRow key={m.alias}>
                    <TableCell>
                      <Text className={styles.mono} weight="semibold">{m.alias}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{m.currentModel}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{m.fallback ?? '--'}</Text>
                    </TableCell>
                    <TableCell>
                      <Badge appearance="outline" color={costTierColor(m.costTier)} size="small">
                        {m.costTier}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Text size={200}>{m.useCases.join(', ')}</Text>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </div>

      {/* Section 3: Governance Policies */}
      <div>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          Governance Policies
        </Text>
        <Card className={styles.tableCard}>
          <Table aria-label="Governance policies table">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Policy Name</TableHeaderCell>
                <TableHeaderCell>Kind</TableHeaderCell>
                <TableHeaderCell>Version</TableHeaderCell>
                <TableHeaderCell>Source File</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {policies.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4}>
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                      No governance policies found in registry
                    </Text>
                  </TableCell>
                </TableRow>
              ) : (
                policies.map((p) => (
                  <TableRow key={p.name}>
                    <TableCell>
                      <Text weight="semibold">{p.name}</Text>
                    </TableCell>
                    <TableCell>
                      <Badge appearance="outline" color="informative" size="small">
                        {p.kind}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Text className={styles.mono}>{p.version}</Text>
                    </TableCell>
                    <TableCell>
                      <Text size={200} className={styles.truncated} title={p.sourceFile}>
                        {p.sourceFile}
                      </Text>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </div>

      {/* Section 4: Container Images (hardcoded infrastructure data) */}
      <div>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          Container Images
        </Text>
        <Card className={styles.tableCard}>
          <Table aria-label="Container images table">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Service</TableHeaderCell>
                <TableHeaderCell>Image</TableHeaderCell>
                <TableHeaderCell>Registry</TableHeaderCell>
                <TableHeaderCell>Tag</TableHeaderCell>
                <TableHeaderCell>Last Build</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {containerImages.map((img) => (
                <TableRow key={img.service}>
                  <TableCell>
                    <Text weight="semibold">{img.service}</Text>
                  </TableCell>
                  <TableCell>
                    <Text font="monospace" size={200}>{img.image}</Text>
                  </TableCell>
                  <TableCell>
                    <Text font="monospace" size={200}>{img.registry}</Text>
                  </TableCell>
                  <TableCell>
                    <Badge appearance="outline" color="informative">
                      {img.tag}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Text size={200}>{img.lastBuild}</Text>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>

      {/* Section 5: Deployment Pipeline (hardcoded infrastructure data) */}
      <div>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          <RocketRegular style={{ marginRight: tokens.spacingHorizontalS }} />
          Deployment Pipeline
        </Text>
        <Card className={styles.pipelineCard}>
          <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>
            Current deployment cycle for the latest image push
          </Text>
          <PipelineStages stages={deploymentStages} />
        </Card>
      </div>
    </div>
  );
}
