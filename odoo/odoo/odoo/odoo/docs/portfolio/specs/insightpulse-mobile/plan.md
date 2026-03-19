# InsightPulse Mobile Plan

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    InsightPulse Mobile                       │
│                   (React Native + Expo)                      │
├─────────────────────────────────────────────────────────────┤
│  Navigation (React Navigation)                               │
│  ├── Dashboard Tab (Job Monitoring)                          │
│  ├── Approvals Tab (Workflow Actions)                        │
│  ├── KB Tab (Knowledge Search)                               │
│  └── Profile Tab (Settings)                                  │
├─────────────────────────────────────────────────────────────┤
│  State Management (Zustand + Persist)                        │
│  ├── User state                                              │
│  ├── Jobs cache                                              │
│  ├── Approvals queue                                         │
│  └── Offline mutations                                       │
├─────────────────────────────────────────────────────────────┤
│  Backend Integration                                          │
│  ├── Supabase Realtime (WebSocket)                           │
│  ├── Supabase Auth (JWT + SecureStore)                       │
│  └── WatermelonDB (Offline cache)                            │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supabase Backend                          │
│  (Shared with Control Room Web App)                          │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL + Realtime + Auth + Storage                      │
└─────────────────────────────────────────────────────────────┘
```

## Milestones

### Week 1: Foundation
- [x] Initialize Expo project with TypeScript
- [x] Configure Supabase client with SecureStore
- [x] Set up Zustand state management
- [x] Implement navigation structure
- [x] Create Dashboard screen (job monitoring)

### Week 2: Core Features
- [x] Create Approvals screen (one-tap workflow)
- [x] Create KB Search screen (semantic search)
- [x] Implement real-time subscriptions
- [ ] Add biometric authentication
- [ ] Configure push notifications

### Week 3: Offline & Polish
- [ ] Implement WatermelonDB for offline cache
- [ ] Add offline mutation queue
- [ ] Dark mode optimization
- [ ] Accessibility audit (VoiceOver)
- [ ] Performance profiling

### Week 4: Release
- [ ] Create app icons and splash screen
- [ ] Generate App Store screenshots
- [ ] Write App Store description
- [ ] EAS build for production
- [ ] TestFlight beta testing
- [ ] App Store submission

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | React Native + Expo | Fast iteration, EAS builds |
| Navigation | React Navigation 6 | Industry standard, typed |
| State | Zustand | Lightweight, persisted |
| Offline | WatermelonDB | SQLite-based, reactive |
| Auth | Supabase + SecureStore | Native keychain storage |
| Push | Expo Notifications | APNs + FCM abstraction |

## App Store Checklist

### iOS Requirements
- [ ] App icon (1024x1024 PNG)
- [ ] Screenshots (5 per device class)
- [ ] App Store description (< 4000 chars)
- [ ] Privacy policy URL
- [ ] Support URL
- [ ] Keywords (< 100 chars)

### Android Requirements
- [ ] App icon (512x512 PNG)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (2-8 per device)
- [ ] Full description (< 4000 chars)
- [ ] Short description (< 80 chars)
- [ ] Privacy policy URL

## Risks

| Risk | Mitigation |
|------|------------|
| App Store rejection | Follow HIG, thorough testing |
| Offline sync conflicts | Last-write-wins with user notification |
| Push notification issues | Graceful degradation, in-app alerts |
| Performance on older devices | Profile on iPhone X, optimize |
