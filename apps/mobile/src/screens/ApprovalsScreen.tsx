/**
 * Approvals Screen
 * One-tap approval workflows with swipe actions
 */

import React, { useCallback, useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
  Alert,
  useColorScheme,
} from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import * as LocalAuthentication from 'expo-local-authentication'
import { useRealtimeApprovals, useApprovalStats } from '../hooks/useRealtime'
import { useAppStore, selectPendingApprovals } from '../store/app'
import { supabase } from '../lib/supabase'
import { ApprovalRequest } from '../types/database'

const HIGH_VALUE_THRESHOLD = 1000 // Require biometric for amounts > $1000

export function ApprovalsScreen() {
  const colorScheme = useColorScheme()
  const isDark = colorScheme === 'dark'
  const theme = isDark ? darkTheme : lightTheme

  const { refetch } = useRealtimeApprovals()
  const { stats, refetch: refetchStats } = useApprovalStats()
  const pendingApprovals = useAppStore(selectPendingApprovals)
  const { user, isOnline, addToOfflineQueue } = useAppStore()

  const [refreshing, setRefreshing] = useState(false)
  const [processingId, setProcessingId] = useState<string | null>(null)

  const onRefresh = useCallback(async () => {
    setRefreshing(true)
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
    await Promise.all([refetch(), refetchStats()])
    setRefreshing(false)
  }, [refetch, refetchStats])

  const handleApprove = async (approval: ApprovalRequest) => {
    // Require biometric for high-value approvals
    if (approval.amount && approval.amount > HIGH_VALUE_THRESHOLD) {
      const hasHardware = await LocalAuthentication.hasHardwareAsync()
      const isEnrolled = await LocalAuthentication.isEnrolledAsync()

      if (hasHardware && isEnrolled) {
        const result = await LocalAuthentication.authenticateAsync({
          promptMessage: `Approve ${formatCurrency(approval.amount)}?`,
          fallbackLabel: 'Use passcode',
        })

        if (!result.success) {
          Alert.alert('Authentication Failed', 'Please try again')
          return
        }
      }
    }

    setProcessingId(approval.id)
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)

    if (!isOnline) {
      // Queue for offline sync
      addToOfflineQueue({
        id: `approve-${approval.id}-${Date.now()}`,
        type: 'approve',
        entity: 'approval',
        entityId: approval.id,
        payload: { status: 'approved', approved_by: user?.id },
        createdAt: new Date().toISOString(),
      })
      setProcessingId(null)
      Alert.alert('Queued', 'Approval will sync when online')
      return
    }

    const { error } = await supabase
      .from('approval_requests')
      .update({
        status: 'approved',
        approved_by: user?.id,
        updated_at: new Date().toISOString(),
      })
      .eq('id', approval.id)

    setProcessingId(null)

    if (error) {
      Alert.alert('Error', 'Failed to approve. Please try again.')
    } else {
      refetch()
    }
  }

  const handleReject = (approval: ApprovalRequest) => {
    Alert.prompt(
      'Reject Approval',
      'Please provide a reason for rejection:',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reject',
          style: 'destructive',
          onPress: async (reason) => {
            setProcessingId(approval.id)
            await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning)

            if (!isOnline) {
              addToOfflineQueue({
                id: `reject-${approval.id}-${Date.now()}`,
                type: 'reject',
                entity: 'approval',
                entityId: approval.id,
                payload: {
                  status: 'rejected',
                  rejected_by: user?.id,
                  rejection_reason: reason,
                },
                createdAt: new Date().toISOString(),
              })
              setProcessingId(null)
              Alert.alert('Queued', 'Rejection will sync when online')
              return
            }

            const { error } = await supabase
              .from('approval_requests')
              .update({
                status: 'rejected',
                rejected_by: user?.id,
                rejection_reason: reason,
                updated_at: new Date().toISOString(),
              })
              .eq('id', approval.id)

            setProcessingId(null)

            if (error) {
              Alert.alert('Error', 'Failed to reject. Please try again.')
            } else {
              refetch()
            }
          },
        },
      ],
      'plain-text'
    )
  }

  const renderApprovalItem = ({ item }: { item: ApprovalRequest }) => {
    const isProcessing = processingId === item.id
    const typeIcon = getTypeIcon(item.request_type)
    const typeColor = getTypeColor(item.request_type)

    return (
      <View style={[styles.approvalCard, { backgroundColor: theme.cardBg }]}>
        <View style={styles.approvalHeader}>
          <View style={[styles.typeBadge, { backgroundColor: typeColor + '20' }]}>
            <Ionicons name={typeIcon as any} size={14} color={typeColor} />
            <Text style={[styles.typeText, { color: typeColor }]}>
              {formatType(item.request_type)}
            </Text>
          </View>
          <Text style={[styles.createdAt, { color: theme.subtext }]}>
            {formatTime(item.created_at)}
          </Text>
        </View>

        <Text style={[styles.approvalName, { color: theme.text }]} numberOfLines={2}>
          {item.ref_name || `Request #${item.ref_id.slice(0, 8)}`}
        </Text>

        {item.amount && (
          <Text style={[styles.amount, { color: theme.text }]}>
            {formatCurrency(item.amount)}
          </Text>
        )}

        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={[styles.rejectButton, { backgroundColor: '#ef444420' }]}
            onPress={() => handleReject(item)}
            disabled={isProcessing}
          >
            <Ionicons name="close" size={20} color="#ef4444" />
            <Text style={[styles.buttonText, { color: '#ef4444' }]}>Reject</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.approveButton, { backgroundColor: '#22c55e' }]}
            onPress={() => handleApprove(item)}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <Text style={styles.buttonTextWhite}>Processing...</Text>
            ) : (
              <>
                <Ionicons name="checkmark" size={20} color="#ffffff" />
                <Text style={styles.buttonTextWhite}>Approve</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.bg }]}>
      {/* Stats Bar */}
      <View style={styles.statsBar}>
        <View style={[styles.statItem, { backgroundColor: theme.cardBg }]}>
          <Text style={[styles.statValue, { color: '#f59e0b' }]}>
            {stats?.pending || 0}
          </Text>
          <Text style={[styles.statLabel, { color: theme.subtext }]}>Pending</Text>
        </View>
        <View style={[styles.statItem, { backgroundColor: theme.cardBg }]}>
          <Text style={[styles.statValue, { color: '#22c55e' }]}>
            {stats?.approved_today || 0}
          </Text>
          <Text style={[styles.statLabel, { color: theme.subtext }]}>Approved</Text>
        </View>
        <View style={[styles.statItem, { backgroundColor: theme.cardBg }]}>
          <Text style={[styles.statValue, { color: '#ef4444' }]}>
            {stats?.rejected_today || 0}
          </Text>
          <Text style={[styles.statLabel, { color: theme.subtext }]}>Rejected</Text>
        </View>
      </View>

      {/* Pending Approvals */}
      <FlatList
        data={pendingApprovals}
        renderItem={renderApprovalItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.approvalList}
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
            <Ionicons name="checkmark-done-circle" size={64} color="#22c55e" />
            <Text style={[styles.emptyTitle, { color: theme.text }]}>All caught up!</Text>
            <Text style={[styles.emptyText, { color: theme.subtext }]}>
              No pending approvals
            </Text>
          </View>
        }
      />
    </View>
  )
}

// Helper functions
function getTypeIcon(type: string) {
  const icons: Record<string, string> = {
    expense_claim: 'receipt-outline',
    purchase_order: 'cart-outline',
    leave_request: 'calendar-outline',
    budget_request: 'wallet-outline',
  }
  return icons[type] || 'document-outline'
}

function getTypeColor(type: string) {
  const colors: Record<string, string> = {
    expense_claim: '#8b5cf6',
    purchase_order: '#3b82f6',
    leave_request: '#22c55e',
    budget_request: '#f59e0b',
  }
  return colors[type] || '#6b7280'
}

function formatType(type: string) {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

function formatTime(isoString: string) {
  const date = new Date(isoString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)

  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  return date.toLocaleDateString()
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
  },
  statsBar: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  statItem: {
    flex: 1,
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  approvalList: {
    paddingHorizontal: 16,
    paddingBottom: 100,
  },
  approvalCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  approvalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  typeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    gap: 4,
  },
  typeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  createdAt: {
    fontSize: 12,
  },
  approvalName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  amount: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 16,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  rejectButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 10,
    gap: 6,
  },
  approveButton: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 10,
    gap: 6,
  },
  buttonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  buttonTextWhite: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
    gap: 8,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginTop: 12,
  },
  emptyText: {
    fontSize: 14,
  },
})
