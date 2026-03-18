'use client'

import {
  makeStyles,
  tokens,
  Card,
  Text,
  Badge,
} from '@fluentui/react-components'

const useStyles = makeStyles({
  card: {
    padding: '20px',
    flex: '1 1 300px',
    minWidth: '280px',
  },
  title: {
    marginBottom: '16px',
    fontWeight: tokens.fontWeightSemibold,
  },
  item: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '10px 0',
    borderBottom: `1px solid ${tokens.colorNeutralStroke3}`,
  },
  itemLast: {
    borderBottom: 'none',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: tokens.colorBrandBackground,
    marginTop: '6px',
    flexShrink: 0,
  },
  itemContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  time: {
    color: tokens.colorNeutralForeground4,
  },
})

interface ActivityItem {
  id: string
  text: string
  time: string
  type: 'deploy' | 'eval' | 'kb' | 'system'
}

const activities: ActivityItem[] = [
  { id: '1', text: 'Copilot eval completed: 41.7% overall', time: '2 hours ago', type: 'eval' },
  { id: '2', text: 'odoo19-docs KB refreshed (7,224 chunks)', time: '4 hours ago', type: 'kb' },
  { id: '3', text: 'Foundry healthcheck passed', time: '6 hours ago', type: 'system' },
  { id: '4', text: 'Service matrix synced (7 services)', time: '8 hours ago', type: 'system' },
  { id: '5', text: 'DNS consistency check passed', time: '12 hours ago', type: 'system' },
]

const typeColors: Record<ActivityItem['type'], 'informative' | 'success' | 'warning' | 'important'> = {
  deploy: 'success',
  eval: 'informative',
  kb: 'warning',
  system: 'important',
}

export function ActivityFeed() {
  const styles = useStyles()

  return (
    <Card className={styles.card}>
      <Text className={styles.title} size={400}>
        Recent Activity
      </Text>
      {activities.map((activity, i) => (
        <div
          key={activity.id}
          className={`${styles.item} ${i === activities.length - 1 ? styles.itemLast : ''}`}
        >
          <div className={styles.dot} />
          <div className={styles.itemContent}>
            <Text size={300}>{activity.text}</Text>
            <Text className={styles.time} size={200}>
              {activity.time}
            </Text>
          </div>
          <Badge appearance="tint" color={typeColors[activity.type]} size="small">
            {activity.type}
          </Badge>
        </div>
      ))}
    </Card>
  )
}
