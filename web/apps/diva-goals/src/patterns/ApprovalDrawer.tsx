import {
  makeStyles,
  tokens,
  Text,
  Button,
  Textarea,
  Badge,
  Divider,
  OverlayDrawer,
  DrawerHeader,
  DrawerHeaderTitle,
  DrawerBody,
  DrawerFooter,
} from '@fluentui/react-components';
import {
  CheckmarkCircleRegular,
  DismissCircleRegular,
  DismissRegular,
} from '@fluentui/react-icons';
import { useState } from 'react';

const useStyles = makeStyles({
  section: {
    marginBottom: tokens.spacingVerticalL,
  },
  confidenceRow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
    marginBottom: tokens.spacingVerticalM,
  },
  actions: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
  },
});

interface ApprovalDrawerProps {
  open: boolean;
  onClose: () => void;
  goalName: string;
  confidence: number;
}

export function ApprovalDrawer({ open, onClose, goalName, confidence }: ApprovalDrawerProps) {
  const styles = useStyles();
  const [comment, setComment] = useState('');
  const needsReview = confidence < 0.85;

  return (
    <OverlayDrawer
      open={open}
      onOpenChange={(_, data) => { if (!data.open) onClose(); }}
      position="end"
      size="medium"
    >
      <DrawerHeader>
        <DrawerHeaderTitle
          action={
            <Button
              icon={<DismissRegular />}
              appearance="subtle"
              onClick={onClose}
            />
          }
        >
          Review & Approve
        </DrawerHeaderTitle>
      </DrawerHeader>
      <DrawerBody>
        <div className={styles.section}>
          <Text weight="semibold" size={400}>{goalName}</Text>
        </div>

        <div className={styles.confidenceRow}>
          <Text>Confidence:</Text>
          <Badge
            color={confidence >= 0.85 ? 'success' : confidence >= 0.70 ? 'warning' : 'danger'}
            appearance="filled"
          >
            {Math.round(confidence * 100)}%
          </Badge>
          {needsReview && (
            <Text size={200} style={{ color: tokens.colorPaletteYellowForeground1 }}>
              Human review required (below 85%)
            </Text>
          )}
        </div>

        <Divider />

        <div className={styles.section}>
          <Text weight="semibold" size={300}>Proposal State</Text>
          <br />
          <Badge color="brand" appearance="outline">
            {needsReview ? 'needs_human_review' : 'judged'}
          </Badge>
          <Text size={200} style={{ display: 'block', marginTop: tokens.spacingVerticalXS }}>
            Per constitution D3, proposals with confidence below 0.85 require human review before approval.
          </Text>
        </div>

        <div className={styles.section}>
          <Text weight="semibold" size={300}>Review Comment</Text>
          <Textarea
            placeholder="Add your review comment..."
            value={comment}
            onChange={(_, data) => setComment(data.value)}
            resize="vertical"
            style={{ width: '100%', marginTop: tokens.spacingVerticalS }}
          />
        </div>
      </DrawerBody>
      <DrawerFooter>
        <div className={styles.actions}>
          <Button
            icon={<CheckmarkCircleRegular />}
            appearance="primary"
            onClick={onClose}
          >
            Approve
          </Button>
          <Button
            icon={<DismissCircleRegular />}
            appearance="secondary"
            onClick={onClose}
          >
            Request Revision
          </Button>
        </div>
      </DrawerFooter>
    </OverlayDrawer>
  );
}
