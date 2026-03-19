'use client';

import {
  Card,
  Text,
  Badge,
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Spinner,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  WrenchRegular,
  BotRegular,
  SearchRegular,
  BookRegular,
  ArrowSyncRegular,
  DocumentRegular,
  AlertRegular,
  AppGenericRegular,
  MoreHorizontalRegular,
} from '@fluentui/react-icons';
import { StatusBadge, type StatusLevel } from '@/components/ui/status-badge';
import { useAgents } from '@/lib/hooks';

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
  moduleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
    gap: tokens.spacingHorizontalL,
  },
  moduleCard: {
    padding: tokens.spacingVerticalL,
  },
  moduleHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: tokens.spacingVerticalM,
  },
  moduleName: {
    fontFamily: tokens.fontFamilyMonospace,
  },
  moduleDesc: {
    color: tokens.colorNeutralForeground2,
    marginBottom: tokens.spacingVerticalM,
  },
  moduleDetails: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailLabel: {
    color: tokens.colorNeutralForeground3,
  },
  categoryBadge: {
    textTransform: 'capitalize',
  },
  categoryIcon: {
    marginRight: tokens.spacingHorizontalXS,
    fontSize: '14px',
    verticalAlign: 'middle',
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '300px',
  },
});

const categoryIcons: Record<string, typeof WrenchRegular> = {
  read: BookRegular,
  search: SearchRegular,
  kb: BookRegular,
  write: WrenchRegular,
  workflow: ArrowSyncRegular,
  finance: WrenchRegular,
  knowledge: BookRegular,
  document: DocumentRegular,
  notification: AlertRegular,
  odoo: AppGenericRegular,
  other: MoreHorizontalRegular,
};

const categoryColors: Record<string, 'informative' | 'important' | 'subtle' | 'brand' | 'success'> = {
  read: 'informative',
  search: 'brand',
  kb: 'important',
  write: 'success',
  workflow: 'subtle',
  finance: 'success',
  knowledge: 'important',
  document: 'informative',
  notification: 'important',
  odoo: 'brand',
  other: 'subtle',
};

const promotionStateColors: Record<string, 'success' | 'brand' | 'informative' | 'subtle' | 'warning'> = {
  prod: 'success',
  staging: 'brand',
  dev: 'informative',
  draft: 'subtle',
  unknown: 'warning',
};

export default function AgentsPage() {
  const styles = useStyles();
  const { agents, tools, source, isLoading } = useAgents();

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingContainer}>
          <Spinner label="Loading agent tools..." size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <Text as="h1" size={800} weight="bold">
            Agents & Tools
          </Text>
          <Badge
            appearance="outline"
            color={source === 'registry' ? 'success' : source === 'live' ? 'success' : 'warning'}
            className={styles.sourceBadge}
          >
            Source: {source}
          </Badge>
        </div>
        <Text className={styles.subtitle} size={400}>
          Copilot tool registry and agent module inventory
        </Text>
      </div>

      {agents.length > 0 && (
        <div>
          <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
            <BotRegular style={{ marginRight: tokens.spacingHorizontalS }} />
            Foundry Agents
          </Text>
          <div className={styles.moduleGrid}>
            {agents.map((agent) => (
              <Card key={agent.name} className={styles.moduleCard}>
                <div className={styles.moduleHeader}>
                  <Text weight="bold" size={400} className={styles.moduleName}>
                    {agent.name}
                  </Text>
                  <Badge
                    appearance="outline"
                    color={promotionStateColors[agent.promotionState] ?? 'warning'}
                  >
                    {agent.promotionState}
                  </Badge>
                </div>
                {agent.description && (
                  <Text size={300} className={styles.moduleDesc}>
                    {agent.description}
                  </Text>
                )}
                <div className={styles.moduleDetails}>
                  <div className={styles.detailRow}>
                    <Text size={200} className={styles.detailLabel}>Version</Text>
                    <Text size={200} font="monospace">{agent.version}</Text>
                  </div>
                  <div className={styles.detailRow}>
                    <Text size={200} className={styles.detailLabel}>Owner</Text>
                    <Text size={200}>{agent.owner}</Text>
                  </div>
                  <div className={styles.detailRow}>
                    <Text size={200} className={styles.detailLabel}>Runtime</Text>
                    <Text size={200} font="monospace">{agent.runtime}</Text>
                  </div>
                  <div className={styles.detailRow}>
                    <Text size={200} className={styles.detailLabel}>Model Alias</Text>
                    <Text size={200} font="monospace">{agent.modelAlias}</Text>
                  </div>
                  <div className={styles.detailRow}>
                    <Text size={200} className={styles.detailLabel}>Tools</Text>
                    <Text size={200}>{agent.tools.length}</Text>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      <div>
        <Text weight="semibold" size={500} className={styles.sectionTitle} as="h2">
          Copilot Tool Registry
        </Text>
        <Card className={styles.tableCard}>
          <Table aria-label="Copilot tools table">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Tool Name</TableHeaderCell>
                <TableHeaderCell>Category</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tools.map((tool) => {
                const Icon = categoryIcons[tool.category] ?? WrenchRegular;
                return (
                  <TableRow key={tool.name}>
                    <TableCell>
                      <Text weight="semibold" font="monospace">
                        {tool.name}
                      </Text>
                    </TableCell>
                    <TableCell>
                      <Badge
                        appearance="outline"
                        color={categoryColors[tool.category] ?? 'subtle'}
                        className={styles.categoryBadge}
                        icon={<Icon className={styles.categoryIcon} />}
                      >
                        {tool.category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={tool.status as StatusLevel} size="small" />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
