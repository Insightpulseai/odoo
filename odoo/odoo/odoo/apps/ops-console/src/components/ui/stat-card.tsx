'use client';

import {
  Card,
  CardHeader,
  Text,
  Badge,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  ArrowTrendingRegular,
  ArrowTrendingDownRegular,
  SubtractRegular,
} from '@fluentui/react-icons';
import type { BadgeProps } from '@fluentui/react-components';

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  intent?: 'success' | 'warning' | 'error' | 'info';
}

const intentColorMap: Record<string, BadgeProps['color']> = {
  success: 'success',
  warning: 'warning',
  error: 'danger',
  info: 'informative',
};

const useStyles = makeStyles({
  card: {
    minWidth: '200px',
    padding: tokens.spacingVerticalL,
  },
  valueContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    marginTop: tokens.spacingVerticalS,
  },
  value: {
    fontSize: tokens.fontSizeHero800,
    fontWeight: tokens.fontWeightBold,
    lineHeight: tokens.lineHeightHero800,
    color: tokens.colorNeutralForeground1,
  },
  subtitle: {
    marginTop: tokens.spacingVerticalXS,
    color: tokens.colorNeutralForeground3,
  },
  trendIcon: {
    fontSize: '20px',
  },
  trendUp: {
    color: tokens.colorPaletteGreenForeground1,
  },
  trendDown: {
    color: tokens.colorPaletteRedForeground1,
  },
  trendNeutral: {
    color: tokens.colorNeutralForeground3,
  },
  header: {
    paddingBottom: '0',
  },
});

export function StatCard({ title, value, subtitle, trend, intent }: StatCardProps) {
  const styles = useStyles();

  const TrendIcon = trend === 'up'
    ? ArrowTrendingRegular
    : trend === 'down'
      ? ArrowTrendingDownRegular
      : SubtractRegular;

  const trendStyle = trend === 'up'
    ? styles.trendUp
    : trend === 'down'
      ? styles.trendDown
      : styles.trendNeutral;

  return (
    <Card className={styles.card}>
      <CardHeader
        className={styles.header}
        header={
          <Text weight="semibold" size={300}>
            {title}
          </Text>
        }
        action={
          intent ? (
            <Badge appearance="filled" color={intentColorMap[intent]}>
              {intent}
            </Badge>
          ) : undefined
        }
      />
      <div className={styles.valueContainer}>
        <Text className={styles.value}>{value}</Text>
        {trend && (
          <TrendIcon className={`${styles.trendIcon} ${trendStyle}`} />
        )}
      </div>
      {subtitle && (
        <Text className={styles.subtitle} size={200}>
          {subtitle}
        </Text>
      )}
    </Card>
  );
}
