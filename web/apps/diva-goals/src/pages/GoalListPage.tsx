import {
  makeStyles,
  tokens,
  Text,
  Card,
  CardHeader,
  Badge,
  Button,
  DataGrid,
  DataGridHeader,
  DataGridRow,
  DataGridHeaderCell,
  DataGridBody,
  DataGridCell,
  TableColumnDefinition,
  createTableColumn,
} from '@fluentui/react-components';
import { AddRegular } from '@fluentui/react-icons';
import { useNavigate } from 'react-router-dom';

interface GoalRow {
  id: number;
  name: string;
  owner: string;
  status: string;
  confidence: number;
  keyResults: number;
  lastUpdated: string;
}

const mockGoals: GoalRow[] = [
  { id: 1, name: 'Achieve 80% EE Parity', owner: 'Platform Team', status: 'on_track', confidence: 0.82, keyResults: 4, lastUpdated: '2026-03-21' },
  { id: 2, name: 'Deploy Diva Copilot to Production', owner: 'Agent Team', status: 'at_risk', confidence: 0.65, keyResults: 3, lastUpdated: '2026-03-19' },
  { id: 3, name: 'BIR Q1 Filing Complete', owner: 'Finance', status: 'on_track', confidence: 0.91, keyResults: 5, lastUpdated: '2026-03-22' },
  { id: 4, name: 'Onboard 3 New Agent Skills', owner: 'Agent Team', status: 'blocked', confidence: 0.40, keyResults: 2, lastUpdated: '2026-03-15' },
];

const statusColor: Record<string, 'success' | 'warning' | 'danger' | 'informative'> = {
  on_track: 'success',
  at_risk: 'warning',
  blocked: 'danger',
  draft: 'informative',
};

const columns: TableColumnDefinition<GoalRow>[] = [
  createTableColumn({ columnId: 'name', renderHeaderCell: () => 'Goal', renderCell: (item) => item.name }),
  createTableColumn({ columnId: 'owner', renderHeaderCell: () => 'Owner', renderCell: (item) => item.owner }),
  createTableColumn({
    columnId: 'status',
    renderHeaderCell: () => 'Status',
    renderCell: (item) => <Badge color={statusColor[item.status] ?? 'informative'} appearance="filled">{item.status.replace('_', ' ')}</Badge>,
  }),
  createTableColumn({
    columnId: 'confidence',
    renderHeaderCell: () => 'Confidence',
    renderCell: (item) => `${Math.round(item.confidence * 100)}%`,
  }),
  createTableColumn({ columnId: 'keyResults', renderHeaderCell: () => 'KRs', renderCell: (item) => String(item.keyResults) }),
  createTableColumn({ columnId: 'lastUpdated', renderHeaderCell: () => 'Updated', renderCell: (item) => item.lastUpdated }),
];

const useStyles = makeStyles({
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: tokens.spacingVerticalL,
  },
});

export function GoalListPage() {
  const styles = useStyles();
  const navigate = useNavigate();

  return (
    <div>
      <div className={styles.header}>
        <Text size={600} weight="semibold">Goals</Text>
        <Button icon={<AddRegular />} appearance="primary">New Goal</Button>
      </div>
      <Card>
        <CardHeader header={<Text weight="semibold">Active Goals</Text>} />
        <DataGrid items={mockGoals} columns={columns} getRowId={(item) => String(item.id)}>
          <DataGridHeader>
            <DataGridRow>
              {({ renderHeaderCell }) => <DataGridHeaderCell>{renderHeaderCell()}</DataGridHeaderCell>}
            </DataGridRow>
          </DataGridHeader>
          <DataGridBody<GoalRow>>
            {({ item, rowId }) => (
              <DataGridRow<GoalRow>
                key={rowId}
                onClick={() => navigate(`/goals/${item.id}`)}
                style={{ cursor: 'pointer' }}
              >
                {({ renderCell }) => <DataGridCell>{renderCell(item)}</DataGridCell>}
              </DataGridRow>
            )}
          </DataGridBody>
        </DataGrid>
      </Card>
    </div>
  );
}
