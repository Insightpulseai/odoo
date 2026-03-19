'use client'

import {
  makeStyles,
  tokens,
  Text,
  Badge,
  Switch,
  Avatar,
  Divider,
} from '@fluentui/react-components'
import {
  WeatherSunny24Regular,
  WeatherMoon24Regular,
  Sparkle24Filled,
} from '@fluentui/react-icons'

const useStyles = makeStyles({
  header: {
    display: 'flex',
    alignItems: 'center',
    height: '56px',
    padding: '0 24px',
    borderBottom: '1px solid transparent',
    backgroundImage: 'linear-gradient(rgba(255,255,255,0.72), rgba(255,255,255,0.72))',
    backdropFilter: 'blur(20px) saturate(180%)',
    gap: '16px',
    flexShrink: 0,
    position: 'relative' as const,
    zIndex: 10,
  },
  headerBorder: {
    position: 'absolute' as const,
    bottom: 0,
    left: 0,
    right: 0,
    height: '1px',
    background: 'linear-gradient(90deg, #7B2FF2 0%, #2264D1 50%, transparent 100%)',
    opacity: 0.3,
  },
  titleWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  sparkleIcon: {
    color: '#7B2FF2',
    display: 'flex',
    alignItems: 'center',
  },
  title: {
    fontWeight: tokens.fontWeightSemibold,
    whiteSpace: 'nowrap' as const,
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  spacer: {
    flex: 1,
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  themeToggle: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
})

interface HeaderProps {
  isDark: boolean
  onThemeToggle: (dark: boolean) => void
}

export function Header({ isDark, onThemeToggle }: HeaderProps) {
  const styles = useStyles()

  return (
    <header
      className={styles.header}
      style={
        isDark
          ? {
              backgroundImage: 'linear-gradient(rgba(27,27,47,0.78), rgba(27,27,47,0.78))',
            }
          : undefined
      }
    >
      <div className={styles.titleWrap}>
        <span className={styles.sparkleIcon}>
          <Sparkle24Filled />
        </span>
        <Text className={styles.title} size={400}>
          IPAI Ops Console
        </Text>
      </div>
      <Badge
        appearance="filled"
        color="informative"
        size="small"
      >
        dev
      </Badge>
      <div className={styles.spacer} />
      <div className={styles.controls}>
        <div className={styles.themeToggle}>
          <WeatherSunny24Regular />
          <Switch
            checked={isDark}
            onChange={(_, data) => onThemeToggle(data.checked)}
            aria-label="Toggle dark mode"
          />
          <WeatherMoon24Regular />
        </div>
        <Divider vertical style={{ height: 24 }} />
        <Avatar
          name="IPAI Admin"
          size={28}
          color="brand"
          aria-label="User profile"
        />
      </div>
      <div className={styles.headerBorder} />
    </header>
  )
}
