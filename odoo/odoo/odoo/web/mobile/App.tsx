/**
 * InsightPulse Mobile App
 * Enterprise companion to Control Room
 */

import React, { useEffect } from 'react'
import { StatusBar, useColorScheme } from 'react-native'
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { Ionicons } from '@expo/vector-icons'
import * as Notifications from 'expo-notifications'
import { useAppStore } from './src/store/app'
import { getCurrentUser, subscribeToNotifications } from './src/lib/supabase'

// Screens
import { DashboardScreen } from './src/screens/DashboardScreen'
import { ApprovalsScreen } from './src/screens/ApprovalsScreen'
import { KBSearchScreen } from './src/screens/KBSearchScreen'

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
})

const Tab = createBottomTabNavigator()

// Custom themes
const CustomDarkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: '#0f172a',
    card: '#1e293b',
    text: '#f8fafc',
    border: '#334155',
    primary: '#3b82f6',
  },
}

const CustomLightTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: '#f8fafc',
    card: '#ffffff',
    text: '#0f172a',
    border: '#e2e8f0',
    primary: '#3b82f6',
  },
}

export default function App() {
  const colorScheme = useColorScheme()
  const { setUser, user, setIsOnline } = useAppStore()

  // Initialize auth and notifications
  useEffect(() => {
    async function init() {
      // Get current user
      const currentUser = await getCurrentUser()
      if (currentUser) {
        // In production, fetch full employee record
        setUser({
          id: currentUser.id,
          user_id: currentUser.id,
          employee_number: 'EMP-001',
          first_name: currentUser.user_metadata?.first_name || 'User',
          last_name: currentUser.user_metadata?.last_name || '',
          email: currentUser.email || '',
          status: 'active',
          is_manager: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      }

      // Request notification permissions
      const { status } = await Notifications.requestPermissionsAsync()
      if (status === 'granted') {
        const token = await Notifications.getExpoPushTokenAsync()
        console.log('Push token:', token.data)
        // Register token with backend
      }
    }

    init()
  }, [])

  // Subscribe to real-time notifications
  useEffect(() => {
    if (!user) return

    const subscription = subscribeToNotifications(user.id, (payload) => {
      const notification = payload.new
      // Show local notification
      Notifications.scheduleNotificationAsync({
        content: {
          title: notification.title,
          body: notification.body,
          data: notification.data,
        },
        trigger: null, // Immediate
      })
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [user?.id])

  // Handle notification tap
  useEffect(() => {
    const subscription = Notifications.addNotificationResponseReceivedListener((response) => {
      const data = response.notification.request.content.data
      // Navigate based on notification type
      console.log('Notification tapped:', data)
    })

    return () => subscription.remove()
  }, [])

  return (
    <NavigationContainer theme={colorScheme === 'dark' ? CustomDarkTheme : CustomLightTheme}>
      <StatusBar barStyle={colorScheme === 'dark' ? 'light-content' : 'dark-content'} />

      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName: string

            switch (route.name) {
              case 'Dashboard':
                iconName = focused ? 'grid' : 'grid-outline'
                break
              case 'Approvals':
                iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline'
                break
              case 'KB':
                iconName = focused ? 'library' : 'library-outline'
                break
              case 'Profile':
                iconName = focused ? 'person' : 'person-outline'
                break
              default:
                iconName = 'help-circle-outline'
            }

            return <Ionicons name={iconName as any} size={size} color={color} />
          },
          tabBarActiveTintColor: '#3b82f6',
          tabBarInactiveTintColor: colorScheme === 'dark' ? '#94a3b8' : '#64748b',
          tabBarStyle: {
            backgroundColor: colorScheme === 'dark' ? '#1e293b' : '#ffffff',
            borderTopColor: colorScheme === 'dark' ? '#334155' : '#e2e8f0',
            paddingTop: 8,
            paddingBottom: 8,
            height: 80,
          },
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: '500',
          },
          headerStyle: {
            backgroundColor: colorScheme === 'dark' ? '#0f172a' : '#f8fafc',
          },
          headerTitleStyle: {
            fontWeight: '600',
          },
          headerTintColor: colorScheme === 'dark' ? '#f8fafc' : '#0f172a',
        })}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{
            title: 'Dashboard',
            headerTitle: 'InsightPulse',
          }}
        />
        <Tab.Screen
          name="Approvals"
          component={ApprovalsScreen}
          options={{
            title: 'Approvals',
            tabBarBadge: undefined, // Dynamic based on pending count
          }}
        />
        <Tab.Screen
          name="KB"
          component={KBSearchScreen}
          options={{
            title: 'Knowledge',
            headerTitle: 'Knowledge Base',
          }}
        />
        <Tab.Screen
          name="Profile"
          component={ProfilePlaceholder}
          options={{
            title: 'Profile',
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  )
}

// Placeholder for Profile screen
function ProfilePlaceholder() {
  const { user } = useAppStore()
  const colorScheme = useColorScheme()
  const theme = colorScheme === 'dark' ? darkTheme : lightTheme

  return (
    <View style={[styles.profileContainer, { backgroundColor: theme.bg }]}>
      <View style={[styles.avatar, { backgroundColor: '#3b82f6' }]}>
        <Ionicons name="person" size={48} color="#ffffff" />
      </View>
      <Text style={[styles.userName, { color: theme.text }]}>
        {user?.first_name} {user?.last_name}
      </Text>
      <Text style={[styles.userEmail, { color: theme.subtext }]}>
        {user?.email}
      </Text>
    </View>
  )
}

import { View, Text, StyleSheet } from 'react-native'

const darkTheme = {
  bg: '#0f172a',
  text: '#f8fafc',
  subtext: '#94a3b8',
}

const lightTheme = {
  bg: '#f8fafc',
  text: '#0f172a',
  subtext: '#64748b',
}

const styles = StyleSheet.create({
  profileContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  avatar: {
    width: 96,
    height: 96,
    borderRadius: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  userName: {
    fontSize: 24,
    fontWeight: '600',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 16,
  },
})
