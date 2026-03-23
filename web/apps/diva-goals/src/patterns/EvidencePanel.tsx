import {
  makeStyles,
  tokens,
  Text,
  Card,
  CardHeader,
  Badge,
  Tree,
  TreeItem,
  TreeItemLayout,
} from '@fluentui/react-components';
import {
  DocumentRegular,
  DatabaseRegular,
  BookRegular,
} from '@fluentui/react-icons';

const useStyles = makeStyles({
  root: {
    height: '100%',
    overflow: 'auto',
  },
  section: {
    marginBottom: tokens.spacingVerticalM,
  },
});

interface EvidencePanelProps {
  goalId: number;
}

const mockEvidence = [
  { id: 'e1', type: 'odoo_record', label: 'OCA Module Inventory (Odoo)', freshness: 'fresh', icon: <DatabaseRegular /> },
  { id: 'e2', type: 'databricks_query', label: 'EE Parity Score (Databricks)', freshness: 'fresh', icon: <DatabaseRegular /> },
  { id: 'e3', type: 'kb_segment', label: 'kb_strategy — OKR Framework', freshness: 'fresh', icon: <BookRegular /> },
  { id: 'e4', type: 'attachment', label: 'EE Audit Report 2026-03-08.pdf', freshness: 'stale', icon: <DocumentRegular /> },
];

const freshnessColor: Record<string, 'success' | 'warning'> = {
  fresh: 'success',
  stale: 'warning',
};

export function EvidencePanel({ goalId }: EvidencePanelProps) {
  const styles = useStyles();

  return (
    <div className={styles.root}>
      <Card className={styles.section}>
        <CardHeader
          header={<Text weight="semibold">Evidence</Text>}
          description={<Text size={200}>Goal #{goalId} — {mockEvidence.length} sources</Text>}
        />
        <Tree aria-label="Evidence sources">
          {mockEvidence.map((ev) => (
            <TreeItem key={ev.id} itemType="leaf">
              <TreeItemLayout
                iconBefore={ev.icon}
                aside={
                  <Badge
                    color={freshnessColor[ev.freshness]}
                    appearance="outline"
                    size="small"
                  >
                    {ev.freshness}
                  </Badge>
                }
              >
                {ev.label}
              </TreeItemLayout>
            </TreeItem>
          ))}
        </Tree>
      </Card>
    </div>
  );
}
