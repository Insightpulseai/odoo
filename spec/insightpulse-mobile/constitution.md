# InsightPulse Mobile App Constitution

## Non-Negotiables

### 1. Mobile-First UX
- **Thumb-friendly navigation**: Bottom tab bar, reachable with one hand
- **Card-based UI**: Large touch targets, swipeable actions
- **Instant feedback**: Haptic responses, loading states, optimistic updates
- **Offline-first**: App must work without internet connection

### 2. Real-Time Sync
- **Supabase Realtime**: WebSocket subscriptions for instant updates
- **Conflict resolution**: Last-write-wins with user notification
- **Sync indicators**: Clear visual feedback on sync status
- **Queue management**: Offline actions queued and replayed on reconnect

### 3. Security
- **Biometric auth**: Face ID / Touch ID required for production
- **JWT tokens**: Secure storage in iOS Keychain / Android Keystore
- **Row-Level Security**: Same RLS policies as web app
- **Data at rest**: Encrypted local database (WatermelonDB + SQLCipher)

### 4. Performance
- **Cold start**: < 2 seconds on iPhone 12+
- **Time to interactive**: < 3 seconds
- **Memory usage**: < 200MB average
- **Battery drain**: < 5% per hour of active use

### 5. Accessibility
- **VoiceOver support**: All interactive elements labeled
- **Dynamic Type**: Support iOS text size settings
- **Color contrast**: WCAG AA compliant (4.5:1 minimum)
- **Reduce motion**: Respect system accessibility settings

### 6. Platform Guidelines
- **iOS HIG**: Follow Apple Human Interface Guidelines
- **Material 3**: Follow Material Design (if Android)
- **No custom patterns**: Use native navigation, gestures, controls

## Source of Truth

| Domain | Source | Notes |
|--------|--------|-------|
| API | Control Room API | Same endpoints as web |
| Auth | Supabase Auth | JWT + biometric |
| Data | Supabase + WatermelonDB | Realtime + offline cache |
| Design | Figma | Mobile-specific designs |
| State | Zustand | Shared state management |

## Quality Gates

1. **Code review**: All PRs reviewed before merge
2. **Unit tests**: 80%+ coverage on business logic
3. **E2E tests**: Critical flows tested with Detox
4. **Performance**: Lighthouse mobile score 90+
5. **Accessibility**: Accessibility audit before release
6. **Crash-free**: < 0.1% crash rate in production
