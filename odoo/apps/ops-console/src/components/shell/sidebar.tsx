'use client'

import { useCallback } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import {
  makeStyles,
  tokens,
  Button,
  Tooltip,
  mergeClasses,
} from '@fluentui/react-components'
import {
  Home24Regular,
  Home24Filled,
  Trophy24Regular,
  Trophy24Filled,
  Bot24Regular,
  Bot24Filled,
  Server24Regular,
  Server24Filled,
  Clock24Regular,
  Clock24Filled,
  PlugConnected24Regular,
  PlugConnected24Filled,
  Book24Regular,
  Book24Filled,
  Rocket24Regular,
  Rocket24Filled,
  Settings24Regular,
  Settings24Filled,
  Navigation24Regular,
  Sparkle20Regular,
} from '@fluentui/react-icons'
import type { NavItem } from '@/lib/types'

const navItems: NavItem[] = [
  { key: 'overview', label: 'Overview', href: '/', icon: Home24Regular, iconFilled: Home24Filled },
  { key: 'leaderboard', label: 'Leaderboard', href: '/leaderboard', icon: Trophy24Regular, iconFilled: Trophy24Filled },
  { key: 'agents', label: 'Agents', href: '/agents', icon: Bot24Regular, iconFilled: Bot24Filled },
  { key: 'services', label: 'Services', href: '/services', icon: Server24Regular, iconFilled: Server24Filled },
  { key: 'jobs', label: 'Jobs & Cron', href: '/jobs', icon: Clock24Regular, iconFilled: Clock24Filled },
  { key: 'orchestration', label: 'Orchestration', href: '/orchestration', icon: PlugConnected24Regular, iconFilled: PlugConnected24Filled },
  { key: 'knowledge', label: 'Knowledge Bases', href: '/knowledge', icon: Book24Regular, iconFilled: Book24Filled },
  { key: 'deployments', label: 'Deployments', href: '/deployments', icon: Rocket24Regular, iconFilled: Rocket24Filled },
]

const bottomItems: NavItem[] = [
  { key: 'settings', label: 'Settings', href: '/settings', icon: Settings24Regular, iconFilled: Settings24Filled },
]

const useStyles = makeStyles({
  sidebar: {
    display: 'flex',
    flexDirection: 'column',
    backgroundImage: 'linear-gradient(rgba(255,255,255,0.72), rgba(255,255,255,0.72))',
    backdropFilter: 'blur(20px) saturate(180%)',
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
    height: '100vh',
    transition: 'width 200ms ease',
    overflow: 'hidden',
    flexShrink: 0,
  },
  expanded: {
    width: '240px',
  },
  collapsed: {
    width: '48px',
  },
  toggleWrap: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '8px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    gap: '8px',
  },
  brandIcon: {
    color: '#7B2FF2',
    display: 'flex',
    alignItems: 'center',
    flexShrink: 0,
  },
  navBody: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    padding: '8px',
    gap: '2px',
    overflowY: 'auto',
    overflowX: 'hidden',
  },
  navBottom: {
    padding: '8px',
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    width: '100%',
    justifyContent: 'flex-start',
    minWidth: 0,
    padding: '8px 12px',
    borderRadius: '8px',
    color: tokens.colorNeutralForeground2,
    textDecoration: 'none',
    cursor: 'pointer',
    transitionProperty: 'background, color',
    transitionDuration: '150ms',
    fontSize: tokens.fontSizeBase300,
    ':hover': {
      backgroundColor: tokens.colorNeutralBackground3Hover,
      color: tokens.colorNeutralForeground1,
    },
  },
  navItemActive: {
    background: 'linear-gradient(135deg, rgba(123,47,242,0.12), rgba(34,100,209,0.12))',
    color: '#7B2FF2',
    ':hover': {
      background: 'linear-gradient(135deg, rgba(123,47,242,0.18), rgba(34,100,209,0.18))',
      color: '#7B2FF2',
    },
  },
  navItemCollapsed: {
    justifyContent: 'center',
    padding: '8px',
  },
  navLabel: {
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightRegular,
  },
  spacer: {
    flex: 1,
  },
})

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const styles = useStyles()
  const pathname = usePathname()

  const isActive = useCallback(
    (item: NavItem) => {
      if (item.href === '/') return pathname === '/'
      return pathname.startsWith(item.href)
    },
    [pathname]
  )

  const renderNavItem = useCallback(
    (item: NavItem) => {
      const active = isActive(item)
      const Icon = active ? item.iconFilled : item.icon

      const link = (
        <Link
          key={item.key}
          href={item.href}
          className={mergeClasses(
            styles.navItem,
            active && styles.navItemActive,
            collapsed && styles.navItemCollapsed
          )}
        >
          <Icon />
          {!collapsed && <span className={styles.navLabel}>{item.label}</span>}
        </Link>
      )

      if (collapsed) {
        return (
          <Tooltip key={item.key} content={item.label} relationship="label" positioning="after">
            {link}
          </Tooltip>
        )
      }

      return link
    },
    [isActive, collapsed, styles]
  )

  return (
    <nav className={mergeClasses(styles.sidebar, collapsed ? styles.collapsed : styles.expanded)}>
      <div className={styles.toggleWrap}>
        {!collapsed && (
          <span className={styles.brandIcon}>
            <Sparkle20Regular />
          </span>
        )}
        <Button
          appearance="subtle"
          icon={<Navigation24Regular />}
          onClick={onToggle}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        />
      </div>
      <div className={styles.navBody}>
        {navItems.map(renderNavItem)}
      </div>
      <div className={styles.navBottom}>
        {bottomItems.map(renderNavItem)}
      </div>
    </nav>
  )
}
