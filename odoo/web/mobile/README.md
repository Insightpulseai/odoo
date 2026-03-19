# InsightPulse Mobile

iOS/Android companion app for Control Room - enterprise workforce management on-the-go.

## Features

- **Real-time Dashboard** - Monitor ETL jobs, pipelines, and system health
- **One-tap Approvals** - Approve expenses and requests with biometric auth
- **KB Search** - Semantic search across knowledge base artifacts
- **Offline Support** - Work without internet, sync when connected
- **Push Notifications** - Instant alerts for approvals and job failures

## Tech Stack

- **React Native** + Expo (EAS)
- **TypeScript**
- **Supabase** (shared backend with Control Room)
- **Zustand** (state management)
- **WatermelonDB** (offline-first sync)

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android
```

## Build & Deploy

```bash
# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android

# Submit to App Store
eas submit --platform ios

# Submit to Google Play
eas submit --platform android
```

## Environment Variables

Create a `.env` file:

```
EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## App Store Checklist

### iOS (App Store Connect)
- [ ] App icon (1024x1024)
- [ ] Screenshots (5 per device)
- [ ] Description
- [ ] Privacy policy URL
- [ ] Support URL

### Android (Google Play)
- [ ] App icon (512x512)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (2-8)
- [ ] Description
- [ ] Privacy policy URL

## Architecture

```
src/
├── lib/           # Supabase client, utilities
├── types/         # TypeScript definitions
├── store/         # Zustand state management
├── hooks/         # Custom React hooks
├── screens/       # Screen components
├── components/    # Reusable UI components
└── assets/        # Images, fonts
```

## Related

- [Control Room Web](../control-room/) - Web dashboard
- [Supabase Migrations](../../supabase/migrations/) - Shared schema
- [Spec Bundle](../../spec/insightpulse-mobile/) - Product requirements
