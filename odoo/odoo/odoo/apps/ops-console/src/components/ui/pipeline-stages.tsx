'use client';

import {
  makeStyles,
  Text,
  tokens,
  mergeClasses,
} from '@fluentui/react-components';
import {
  CheckmarkCircleFilled,
  CircleRegular,
  ArrowSyncRegular,
} from '@fluentui/react-icons';

export type StageStatus = 'completed' | 'in-progress' | 'pending';

export interface PipelineStage {
  name: string;
  status: StageStatus;
}

interface PipelineStagesProps {
  stages: PipelineStage[];
}

const useStyles = makeStyles({
  root: {
    display: 'flex',
    alignItems: 'center',
    gap: '0',
    overflowX: 'auto',
    padding: `${tokens.spacingVerticalM} 0`,
  },
  stage: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: tokens.spacingVerticalXS,
    minWidth: '100px',
    position: 'relative',
  },
  iconCompleted: {
    color: tokens.colorBrandBackground,
    fontSize: '28px',
  },
  iconInProgress: {
    color: tokens.colorPaletteYellowForeground1,
    fontSize: '28px',
  },
  iconPending: {
    color: tokens.colorNeutralForeground4,
    fontSize: '28px',
  },
  connector: {
    width: '40px',
    height: '2px',
    backgroundColor: tokens.colorNeutralStroke2,
    alignSelf: 'center',
    marginBottom: tokens.spacingVerticalL,
  },
  connectorCompleted: {
    backgroundColor: tokens.colorBrandBackground,
  },
  stageLabel: {
    textAlign: 'center',
    maxWidth: '100px',
  },
});

export function PipelineStages({ stages }: PipelineStagesProps) {
  const styles = useStyles();

  return (
    <div className={styles.root}>
      {stages.map((stage, index) => (
        <div key={stage.name} style={{ display: 'contents' }}>
          <div className={styles.stage}>
            {stage.status === 'completed' && (
              <CheckmarkCircleFilled className={styles.iconCompleted} />
            )}
            {stage.status === 'in-progress' && (
              <ArrowSyncRegular className={styles.iconInProgress} />
            )}
            {stage.status === 'pending' && (
              <CircleRegular className={styles.iconPending} />
            )}
            <Text size={200} weight="semibold" className={styles.stageLabel}>
              {stage.name}
            </Text>
          </div>
          {index < stages.length - 1 && (
            <div
              className={mergeClasses(
                styles.connector,
                stage.status === 'completed' && styles.connectorCompleted,
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
}
