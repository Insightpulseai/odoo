/**
 * Dashboard Screen
 * Real-time job monitoring with stats cards
 */

import React, { useCallback } from 'react'
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
  useColorScheme,
} from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import { useRealtimeJobs, useJobStats } from '../hooks/useRealtime'
import { useAppStore, selectRecentJobs } from '../store/app'
import { Job } from '../types/database'

export function DashboardScreen() {
  const colorScheme = useColorScheme()
  const isDark = colorScheme === 'dark'
  const theme = isDark ? darkTheme : lightTheme

  const { refetch } = useRealtimeJobs()
  const { stats, refetch: refetchStats } = useJobStats()
  const jobs = useAppStore(selectRecentJobs)
  const { isOnline, lastSyncAt } = useAppStore()

  const [refreshing, setRefreshing] = React.useState(false)

  const onRefresh = useCallback(async () => {
    setRefreshing(true)
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
    await Promise.all([refetch(), refetchStats()])
    setRefreshing(false)
  }, [refetch, refetchStats])

  const renderStatsCard = (title: string, value: number | string, icon: string, color: string) => (
    <View style={[styles.statsCard, { backgroundColor: theme.cardBg }]}>
      <Ionicons name={icon as any} size={24} color={color} />
      <Text style={[styles.statsValue, { color: theme.text }]}>{value}</Text>
      <Text style={[styles.statsLabel, { color: theme.subtext }]}>{title}</Text>
    </View>
  )

  const renderJobItem = ({ item }: { item: Job }) => {
    const statusColor = getStatusColor(item.status)
    const statusIcon = getStatusIcon(item.status)

    return (
      <TouchableOpacity
        style={[styles.jobCard, { backgroundColor: theme.cardBg }]}
        onPress={() => {
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
          // Navigate to job detail
        }}
        activeOpacity={0.7}
      >
        <View style={styles.jobHeader}>
          <View style={[styles.statusBadge, { backgroundColor: statusColor + '20' }]}>
            <Ionicons name={statusIcon as any} size={14} color={statusColor} />
            <Text style={[styles.statusText, { color: statusColor }]}>
              {item.status.toUpperCase()}
            </Text>
          </View>
          <Text style={[styles.jobType, { color: theme.subtext }]}>
            {item.job_type}
          </Text>
        </View>

        <Text style={[styles.jobName, { color: theme.text }]} numberOfLines={1}>
          {item.name}
        </Text>

        <View style={styles.jobFooter}>
          <Text style={[styles.jobTime, { color: theme.subtext }]}>
            {formatTime(item.created_at)}
          </Text>
          {item.duration_ms && (
            <Text style={[styles.jobDuration, { color: theme.subtext }]}>
              {formatDuration(item.duration_ms)}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.bg }]}>
      {/* Sync Status */}
      <View style={[styles.syncBar, { backgroundColor: isOnline ? '#22c55e20' : '#ef444420' }]}>
        <Ionicons
          name={isOnline ? 'cloud-done' : 'cloud-offline'}
          size={14}
          color={isOnline ? '#22c55e' : '#ef4444'}
        />
        <Text style={[styles.syncText, { color: isOnline ? '#22c55e' : '#ef4444' }]}>
          {isOnline ? 'Connected' : 'Offline'} • Last sync: {formatTime(lastSyncAt || new Date().toISOString())}
        </Text>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        {renderStatsCard('Running', stats?.running || 0, 'play-circle', '#3b82f6')}
        {renderStatsCard('Succeeded', stats?.succeeded || 0, 'checkmark-circle', '#22c55e')}
        {renderStatsCard('Failed', stats?.failed || 0, 'close-circle', '#ef4444')}
        {renderStatsCard('Queued', stats?.queued || 0, 'time', '#f59e0b')}
      </View>

      {/* Success Rate */}
      {stats && (
        <View style={[styles.successRateCard, { backgroundColor: theme.cardBg }]}>
          <Text style={[styles.successRateLabel, { color: theme.subtext }]}>
            Today's Success Rate
          </Text>
          <Text style={[styles.successRateValue, { color: '#22c55e' }]}>
            {stats.success_rate.toFixed(1)}%
          </Text>
        </View>
      )}

      {/* Recent Jobs */}
      <Text style={[styles.sectionTitle, { color: theme.text }]}>Recent Jobs</Text>

      <FlatList
        data={jobs}
        renderItem={renderJobItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.jobList}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.text}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="folder-open-outline" size={48} color={theme.subtext} />
            <Text style={[styles.emptyText, { color: theme.subtext }]}>No jobs yet</Text>
          </View>
        }
      />
    </View>
  )
}

// Helper functions
function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    pending: '#f59e0b',
    running: '#3b82f6',
    success: '#22c55e',
    failed: '#ef4444',
    cancelled: '#6b7280',
  }
  return colors[status] || '#6b7280'
}

function getStatusIcon(status: string) {
  const icons: Record<string, string> = {
    pending: 'time-outline',
    running: 'sync',
    success: 'checkmark-circle-outline',
    failed: 'close-circle-outline',
    cancelled: 'ban-outline',
  }
  return icons[status] || 'help-circle-outline'
}

function formatTime(isoString: string) {
  const date = new Date(isoString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return date.toLocaleDateString()
}

function formatDuration(ms: number) {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

// Themes
const darkTheme = {
  bg: '#0f172a',
  cardBg: '#1e293b',
  text: '#f8fafc',
  subtext: '#94a3b8',
}

const lightTheme = {
  bg: '#f8fafc',
  cardBg: '#ffffff',
  text: '#0f172a',
  subtext: '#64748b',
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 8,
  },
  syncBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 8,
    gap: 6,
  },
  syncText: {
    fontSize: 12,
    fontWeight: '500',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 12,
    gap: 8,
  },
  statsCard: {
    flex: 1,
    minWidth: '45%',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    gap: 8,
  },
  statsValue: {
    fontSize: 28,
    fontWeight: '700',
  },
  statsLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  successRateCard: {
    marginHorizontal: 16,
    marginTop: 12,
    padding: 16,
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  successRateLabel: {
    fontSize: 14,
    fontWeight: '500',
  },
  successRateValue: {
    fontSize: 24,
    fontWeight: '700',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginHorizontal: 16,
    marginTop: 20,
    marginBottom: 12,
  },
  jobList: {
    paddingHorizontal: 16,
    paddingBottom: 100,
  },
  jobCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  jobHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    gap: 4,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
  },
  jobType: {
    fontSize: 12,
    textTransform: 'uppercase',
  },
  jobName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  jobFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  jobTime: {
    fontSize: 12,
  },
  jobDuration: {
    fontSize: 12,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 48,
    gap: 12,
  },
  emptyText: {
    fontSize: 16,
  },
})
