'use client'

import {
  makeStyles,
  tokens,
  Card,
  Text,
  Button,
} from '@fluentui/react-components'
import {
  Rocket24Regular,
  ClipboardTask24Regular,
  ArrowSync24Regular,
  DocumentSearch24Regular,
} from '@fluentui/react-icons'

const useStyles = makeStyles({
  card: {
    padding: '20px',
    width: '100%',
  },
  title: {
    marginBottom: '16px',
    fontWeight: tokens.fontWeightSemibold,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
    gap: '12px',
  },
  action: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    padding: '16px 12px',
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    cursor: 'pointer',
    transition: 'all 150ms ease',
    ':hover': {
      backgroundColor: tokens.colorNeutralBackground1Hover,
      border: `1px solid ${tokens.colorBrandStroke1}`,
    },
  },
  actionIcon: {
    color: tokens.colorBrandForeground1,
  },
  actionLabel: {
    textAlign: 'center',
    color: tokens.colorNeutralForeground1,
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
  },
})

const actions = [
  { key: 'deploy', label: 'Deploy Service', icon: <Rocket24Regular /> },
  { key: 'eval', label: 'Run Eval', icon: <ClipboardTask24Regular /> },
  { key: 'refresh', label: 'Refresh KBs', icon: <ArrowSync24Regular /> },
  { key: 'logs', label: 'View Logs', icon: <DocumentSearch24Regular /> },
]

export function QuickActions() {
  const styles = useStyles()

  return (
    <Card className={styles.card}>
      <Text className={styles.title} size={400}>
        Quick Actions
      </Text>
      <div className={styles.grid}>
        {actions.map((action) => (
          <button
            key={action.key}
            className={styles.action}
            onClick={() => {
              /* placeholder */
            }}
            aria-label={action.label}
          >
            <span className={styles.actionIcon}>{action.icon}</span>
            <span className={styles.actionLabel}>{action.label}</span>
          </button>
        ))}
      </div>
    </Card>
  )
}
