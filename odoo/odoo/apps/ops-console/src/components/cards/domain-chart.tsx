'use client'

import {
  makeStyles,
  tokens,
  Card,
  Text,
} from '@fluentui/react-components'
import { copilotEvalData, domainLabel, formatScore } from '@/lib/data'

const useStyles = makeStyles({
  card: {
    padding: '20px',
    flex: '1 1 400px',
  },
  title: {
    marginBottom: '16px',
    fontWeight: tokens.fontWeightSemibold,
  },
  barRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '10px',
  },
  label: {
    width: '160px',
    flexShrink: 0,
    textAlign: 'right',
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  barTrack: {
    flex: 1,
    height: '20px',
    backgroundColor: tokens.colorNeutralBackground4,
    borderRadius: tokens.borderRadiusSmall,
    overflow: 'hidden',
    position: 'relative' as const,
  },
  barFill: {
    height: '100%',
    borderRadius: tokens.borderRadiusSmall,
    transition: 'width 600ms ease',
  },
  score: {
    width: '40px',
    textAlign: 'right',
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
})

function getBarColor(score: number): string {
  if (score >= 0.7) return tokens.colorPaletteGreenBackground3
  if (score >= 0.5) return tokens.colorPaletteYellowBackground3
  if (score >= 0.3) return tokens.colorPaletteDarkOrangeBackground3
  return tokens.colorPaletteRedBackground3
}

export function DomainChart() {
  const styles = useStyles()
  const sorted = Object.entries(copilotEvalData.domain_scores).sort(
    ([, a], [, b]) => b - a
  )

  return (
    <Card className={styles.card}>
      <Text className={styles.title} size={400}>
        Domain Maturity
      </Text>
      {sorted.map(([domain, score]) => (
        <div key={domain} className={styles.barRow}>
          <Text className={styles.label}>{domainLabel(domain)}</Text>
          <div className={styles.barTrack}>
            <div
              className={styles.barFill}
              style={{
                width: `${Math.round(score * 100)}%`,
                backgroundColor: getBarColor(score),
              }}
            />
          </div>
          <Text className={styles.score}>{formatScore(score)}</Text>
        </div>
      ))}
    </Card>
  )
}
