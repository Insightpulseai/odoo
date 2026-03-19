'use client'

import {
  makeStyles,
  tokens,
  Card,
  CardHeader,
  Text,
  Badge,
  mergeClasses,
} from '@fluentui/react-components'
import type { BadgeProps } from '@fluentui/react-components'

const useStyles = makeStyles({
  card: {
    flex: '1 1 220px',
    minWidth: '200px',
    padding: '24px',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
    border: 'none',
    transition: 'box-shadow 200ms ease, transform 200ms ease',
    ':hover': {
      boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
      transform: 'translateY(-1px)',
    },
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '12px',
  },
  value: {
    fontSize: '32px',
    fontWeight: tokens.fontWeightBold,
    lineHeight: '1.1',
    color: tokens.colorNeutralForeground1,
  },
  valueGradient: {
    fontSize: '32px',
    fontWeight: tokens.fontWeightBold,
    lineHeight: '1.1',
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  label: {
    color: tokens.colorNeutralForeground3,
    marginTop: '8px',
  },
  trend: {
    marginTop: '8px',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
})

interface StatCardProps {
  title: string
  value: string | number
  label?: string
  badge?: {
    text: string
    color: BadgeProps['color']
  }
  icon?: React.ReactNode
  accent?: boolean
}

export function StatCard({ title, value, label, badge, icon, accent }: StatCardProps) {
  const styles = useStyles()

  return (
    <Card className={styles.card}>
      <div className={styles.header}>
        <Text size={300} weight="semibold" style={{ color: tokens.colorNeutralForeground3 }}>
          {title}
        </Text>
        {badge && (
          <Badge appearance="filled" color={badge.color} size="small">
            {badge.text}
          </Badge>
        )}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {icon}
        <Text className={accent ? styles.valueGradient : styles.value}>{value}</Text>
      </div>
      {label && (
        <Text className={styles.label} size={200}>
          {label}
        </Text>
      )}
    </Card>
  )
}
