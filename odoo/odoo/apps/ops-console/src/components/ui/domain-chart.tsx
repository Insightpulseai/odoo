'use client';

import {
  makeStyles,
  Text,
  tokens,
  mergeClasses,
} from '@fluentui/react-components';

export interface DomainScore {
  domain: string;
  score: number;
  maturity: 'operational' | 'partial' | 'scaffolded' | 'missing';
}

interface DomainChartProps {
  scores: DomainScore[];
}

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
    width: '100%',
  },
  row: {
    display: 'grid',
    gridTemplateColumns: '180px 1fr 48px',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
  },
  label: {
    textAlign: 'right',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  barTrack: {
    height: '20px',
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground5,
    overflow: 'hidden',
    position: 'relative',
  },
  barFill: {
    height: '100%',
    borderRadius: tokens.borderRadiusMedium,
    transitionProperty: 'width',
    transitionDuration: tokens.durationNormal,
    transitionTimingFunction: tokens.curveDecelerateMax,
  },
  operational: {
    backgroundColor: tokens.colorPaletteGreenBackground2,
  },
  partial: {
    backgroundColor: tokens.colorPaletteYellowBackground2,
  },
  scaffolded: {
    backgroundColor: tokens.colorPaletteBerryBackground2,
  },
  missing: {
    backgroundColor: tokens.colorPaletteRedBackground2,
  },
  scoreText: {
    fontVariantNumeric: 'tabular-nums',
  },
});

export function DomainChart({ scores }: DomainChartProps) {
  const styles = useStyles();

  return (
    <div className={styles.root}>
      {scores.map((item) => (
        <div key={item.domain} className={styles.row}>
          <Text size={200} weight="semibold" className={styles.label}>
            {item.domain}
          </Text>
          <div className={styles.barTrack}>
            <div
              className={mergeClasses(styles.barFill, styles[item.maturity])}
              style={{ width: `${Math.round(item.score * 100)}%` }}
            />
          </div>
          <Text size={200} className={styles.scoreText}>
            {Math.round(item.score * 100)}%
          </Text>
        </div>
      ))}
    </div>
  );
}
