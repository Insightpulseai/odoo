# InsightPulse Mobile App - Product Requirements

## Overview

InsightPulse Mobile is the iOS/Android companion to Control Room, providing enterprise workforce management on-the-go. Benchmarked against Notion's mobile app (4.7★, 10M+ downloads).

## Target Metrics

| Metric | Target | Benchmark (Notion) |
|--------|--------|-------------------|
| App Store Rating | 4.5+ ★ | 4.7 ★ |
| Downloads (Year 1) | 5K-10K | 10M+ |
| Crash Rate | < 0.05% | < 0.1% |
| Cold Start | < 2s | ~3s |
| Retention (D30) | 70%+ | ~60% |

## Core Features

### 1. Job Monitoring Dashboard
**Priority: P0**

Real-time visibility into ETL jobs, pipelines, and system health.

```typescript
interface JobDashboard {
  stats: {
    running: number
    succeeded: number
    failed: number
    queued: number
  }
  recentJobs: Job[]
  alerts: Alert[]
}
```

**Acceptance Criteria:**
- [ ] Live job counts update via Supabase Realtime
- [ ] Pull-to-refresh for manual sync
- [ ] Tap job card to view details
- [ ] Filter by status, date range
- [ ] Push notification on job failure

### 2. Approval Workflows
**Priority: P0**

One-tap expense and request approvals with full audit trail.

```typescript
interface Approval {
  id: string
  type: 'expense' | 'leave' | 'purchase_order'
  requestor: Employee
  amount?: number
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}
```

**Acceptance Criteria:**
- [ ] Push notification for new approvals
- [ ] Swipe-to-approve/reject
- [ ] Biometric confirmation for high-value approvals
- [ ] Offline queue with sync indicator
- [ ] Approval history with search

### 3. Knowledge Base Search
**Priority: P1**

Semantic search across KB artifacts with persona-based ranking.

**Acceptance Criteria:**
- [ ] Voice search input
- [ ] Semantic search results (pgvector)
- [ ] Persona-filtered recommendations
- [ ] Offline cached favorites
- [ ] Share artifact via iOS Share Sheet

### 4. Task Management
**Priority: P1**

Synced task list from Odoo with offline completion.

**Acceptance Criteria:**
- [ ] Task list with due dates
- [ ] Checkbox completion (optimistic UI)
- [ ] Photo attachment from camera
- [ ] Location tagging (field work)
- [ ] Offline support with sync

### 5. Expense Submission
**Priority: P1**

Camera-to-OCR expense submission flow.

```typescript
interface ExpenseSubmission {
  receipt: File
  ocr: {
    vendor: string
    amount: number
    date: string
    confidence: number
  }
  category: ExpenseCategory
  notes: string
}
```

**Acceptance Criteria:**
- [ ] Camera capture or photo library
- [ ] AWS Textract OCR processing
- [ ] Auto-fill form from OCR
- [ ] Category selection
- [ ] Submit for approval

## Technical Requirements

### Stack
- **Framework**: React Native + Expo (EAS)
- **Language**: TypeScript
- **Backend**: Supabase (same as Control Room)
- **Offline**: WatermelonDB (SQLite-based)
- **State**: Zustand
- **Navigation**: React Navigation 6
- **Push**: Expo Notifications (APNs/FCM)

### API Integration
```typescript
// Shared API client with Control Room
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

// Real-time subscriptions
supabase
  .channel('jobs')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'control_room_jobs' }, handler)
  .subscribe()
```

### Offline Strategy
1. **Read**: Serve from WatermelonDB cache
2. **Write**: Queue mutations locally
3. **Sync**: Replay queue on reconnect
4. **Conflict**: Last-write-wins with toast notification

## Screen Hierarchy

```
Tab Bar
├─ Dashboard (Home)
│   ├─ Job Stats Cards
│   ├─ Recent Jobs List
│   └─ Quick Actions FAB
├─ Approvals
│   ├─ Pending Tab
│   └─ History Tab
├─ KB Search
│   ├─ Search Bar
│   ├─ Results List
│   └─ Artifact Detail Modal
├─ Tasks
│   ├─ Task List
│   └─ Task Detail
└─ Profile
    ├─ Settings
    ├─ Notifications
    └─ Logout
```

## Non-Functional Requirements

### Performance
- Cold start: < 2 seconds
- Time to interactive: < 3 seconds
- Frame rate: 60fps animations
- Bundle size: < 50MB (without assets)

### Security
- Biometric auth (Face ID / Touch ID)
- Keychain storage for tokens
- Certificate pinning (optional)
- No sensitive data in logs

### Accessibility
- VoiceOver labels on all controls
- Dynamic Type support
- Color contrast 4.5:1+
- Reduce motion respect

## App Store Requirements

### iOS (App Store Connect)
- App icon: 1024x1024 PNG
- Screenshots: 5 per device class
- Description: 1000 chars max
- Keywords: 30 chars
- Privacy policy URL
- Support URL

### Android (Google Play)
- App icon: 512x512 PNG
- Feature graphic: 1024x500
- Screenshots: 2-8 per device
- Description: 4000 chars max
- Privacy policy URL

## Success Criteria

1. **Week 21**: App builds successfully on iOS + Android
2. **Week 22**: App Store submission approved
3. **Week 23**: 100+ internal users onboarded
4. **Month 3**: 4.5+ star rating maintained
5. **Month 6**: 70%+ D30 retention

## Dependencies

- Control Room API (complete)
- Supabase schemas (complete)
- AWS Textract (expense OCR)
- Apple Developer Account ($99/year)
- Google Play Developer Account ($25 one-time)
