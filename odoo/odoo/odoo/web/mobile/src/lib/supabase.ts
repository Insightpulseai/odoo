/**
 * Supabase Client for InsightPulse Mobile
 * Shared configuration with Control Room web app
 */

import { createClient } from '@supabase/supabase-js'
import * as SecureStore from 'expo-secure-store'
import { Database } from '../types/database'

const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://spdtwktxdalcfigzeqrz.supabase.co'
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || ''

// Custom storage adapter using Expo SecureStore
const ExpoSecureStoreAdapter = {
  getItem: async (key: string) => {
    return await SecureStore.getItemAsync(key)
  },
  setItem: async (key: string, value: string) => {
    await SecureStore.setItemAsync(key, value)
  },
  removeItem: async (key: string) => {
    await SecureStore.deleteItemAsync(key)
  },
}

// Create typed Supabase client
export const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: ExpoSecureStoreAdapter,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
})

// Real-time subscription helpers
export function subscribeToJobs(callback: (payload: any) => void) {
  return supabase
    .channel('control_room_jobs')
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table: 'control_room_jobs' },
      callback
    )
    .subscribe()
}

export function subscribeToApprovals(callback: (payload: any) => void) {
  return supabase
    .channel('approval_requests')
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table: 'approval_requests' },
      callback
    )
    .subscribe()
}

export function subscribeToNotifications(userId: string, callback: (payload: any) => void) {
  return supabase
    .channel(`notifications:${userId}`)
    .on(
      'postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'notifications', filter: `user_id=eq.${userId}` },
      callback
    )
    .subscribe()
}

// Auth helpers
export async function signInWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  return { data, error }
}

export async function signOut() {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

export async function getCurrentSession() {
  const { data: { session } } = await supabase.auth.getSession()
  return session
}
