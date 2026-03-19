'use client';

import {
  makeStyles,
  Text,
  tokens,
  mergeClasses,
} from '@fluentui/react-components';

export interface MaturityBarProps {
  current: number;
  target: number;
  label?: string;
}

const SEGMENT_COUNT = 5;

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    width: '100%',
  },
  labelRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  barContainer: {
    display: 'flex',
    gap: '2px',
    height: '8px',
    width: '100%',
  },
  segment: {
    flex: 1,
    borderRadius: tokens.borderRadiusSmall,
    backgroundColor: tokens.colorNeutralBackground5,
    position: 'relative',
  },
  segmentFilled: {
    backgroundColor: tokens.colorBrandBackground,
  },
  segmentTarget: {
    '::after': {
      content: '""',
      position: 'absolute',
      top: '-2px',
      bottom: '-2px',
      right: '-1px',
      width: '2px',
      backgroundColor: tokens.colorNeutralForeground1,
    },
  },
  segmentWarning: {
    backgroundColor: tokens.colorPaletteYellowBackground2,
  },
  segmentSuccess: {
    backgroundColor: tokens.colorPaletteGreenBackground2,
  },
});

export function MaturityBar({ current, target, label }: MaturityBarProps) {
  const styles = useStyles();

  const segments = Array.from({ length: SEGMENT_COUNT }, (_, i) => {
    const isFilled = i < current;
    const isTarget = i === Math.floor(target) - 1;
    const segmentColor = current >= target
      ? styles.segmentSuccess
      : current >= target - 1
        ? styles.segmentWarning
        : styles.segmentFilled;

    return (
      <div
        key={i}
        className={mergeClasses(
          styles.segment,
          isFilled && segmentColor,
          isTarget && styles.segmentTarget,
        )}
      />
    );
  });

  return (
    <div className={styles.root}>
      {label && (
        <div className={styles.labelRow}>
          <Text size={200} weight="semibold">
            {label}
          </Text>
          <Text size={200}>
            {current} / {target}
          </Text>
        </div>
      )}
      <div className={styles.barContainer}>{segments}</div>
    </div>
  );
}
