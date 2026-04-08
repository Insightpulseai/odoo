import { useParams } from 'react-router-dom';
import {
  makeStyles,
  tokens,
  Text,
  Card,
  CardHeader,
  Badge,
  Button,
  ProgressBar,
  Divider,
  Accordion,
  AccordionItem,
  AccordionHeader,
  AccordionPanel,
} from '@fluentui/react-components';
import {
  CheckmarkCircleRegular,
  ArrowLeftRegular,
} from '@fluentui/react-icons';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { EvidencePanel } from '../patterns/EvidencePanel';
import { ApprovalDrawer } from '../patterns/ApprovalDrawer';

const useStyles = makeStyles({
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
    marginBottom: tokens.spacingVerticalL,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 380px',
    gap: tokens.spacingHorizontalL,
  },
  section: {
    marginBottom: tokens.spacingVerticalL,
  },
  krRow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
    padding: `${tokens.spacingVerticalS} 0`,
  },
  krName: {
    flex: 1,
  },
  krProgress: {
    width: '200px',
  },
});

const mockGoal = {
  id: 1,
  name: 'Achieve 80% EE Parity',
  owner: 'Platform Team',
  status: 'on_track' as const,
  confidence: 0.82,
  description: 'Close the Enterprise Edition feature gap to 80% coverage using CE + OCA + ipai_* modules.',
  keyResults: [
    { id: 1, name: 'Install 56 must-have OCA modules', progress: 0.75 },
    { id: 2, name: 'Implement 5 ipai_diva modules', progress: 0.20 },
    { id: 3, name: 'Pass EE parity audit', progress: 0.45 },
    { id: 4, name: 'Complete Copilot integration', progress: 0.60 },
  ],
  statusNarrative: 'Goal is tracking well. 42 of 56 OCA modules installed and verified. Key risk: ipai_diva module development is behind schedule. Evidence freshness: 2 days.',
};

export function GoalDetailPage() {
  const { goalId } = useParams();
  const navigate = useNavigate();
  const styles = useStyles();
  const [approvalOpen, setApprovalOpen] = useState(false);

  return (
    <div>
      <div className={styles.header}>
        <Button
          icon={<ArrowLeftRegular />}
          appearance="subtle"
          onClick={() => navigate('/')}
        />
        <Text size={600} weight="semibold">{mockGoal.name}</Text>
        <Badge color="success" appearance="filled">{mockGoal.status.replace('_', ' ')}</Badge>
        <Text size={300} style={{ marginLeft: 'auto' }}>
          Confidence: {Math.round(mockGoal.confidence * 100)}%
        </Text>
      </div>

      <div className={styles.grid}>
        <div>
          <Card className={styles.section}>
            <CardHeader header={<Text weight="semibold">Status Synthesis</Text>} />
            <Text>{mockGoal.statusNarrative}</Text>
            <Divider style={{ margin: `${tokens.spacingVerticalM} 0` }} />
            <Button
              icon={<CheckmarkCircleRegular />}
              appearance="primary"
              onClick={() => setApprovalOpen(true)}
            >
              Review & Approve
            </Button>
          </Card>

          <Card className={styles.section}>
            <CardHeader header={<Text weight="semibold">Key Results</Text>} />
            {mockGoal.keyResults.map((kr) => (
              <div key={kr.id} className={styles.krRow}>
                <Text className={styles.krName}>{kr.name}</Text>
                <div className={styles.krProgress}>
                  <ProgressBar value={kr.progress} />
                </div>
                <Text size={200}>{Math.round(kr.progress * 100)}%</Text>
              </div>
            ))}
          </Card>

          <Accordion collapsible>
            <AccordionItem value="description">
              <AccordionHeader>Description</AccordionHeader>
              <AccordionPanel>{mockGoal.description}</AccordionPanel>
            </AccordionItem>
          </Accordion>
        </div>

        <EvidencePanel goalId={Number(goalId)} />
      </div>

      <ApprovalDrawer
        open={approvalOpen}
        onClose={() => setApprovalOpen(false)}
        goalName={mockGoal.name}
        confidence={mockGoal.confidence}
      />
    </div>
  );
}
