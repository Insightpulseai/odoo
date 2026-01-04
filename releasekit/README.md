# ReleaseKit - Mobile App Store Deployment

Automated deployment pipeline for iOS App Store and Google Play Store.

## Quick Start

```bash
# Install fastlane
cd releasekit/fastlane
bundle install

# Set up credentials (see below)
export APPLE_ID="your@email.com"
export ASC_KEY_ID="XXXXXXXXXX"
# ... (see full list below)

# Run audit
./scripts/audit_android.sh
./scripts/audit_ios.sh

# Build and deploy
./scripts/build_android.sh
bundle exec fastlane android internal

./scripts/build_ios.sh
bundle exec fastlane ios beta
```

## Directory Structure

```
releasekit/
├── fastlane/
│   ├── Appfile      # App identifiers and team IDs
│   ├── Fastfile     # Deployment lanes
│   └── Gemfile      # Ruby dependencies
├── scripts/
│   ├── audit_android.sh  # Play Store compliance check
│   ├── audit_ios.sh      # App Store compliance check
│   ├── build_android.sh  # Build Android AAB
│   └── build_ios.sh      # Build iOS app
└── store/
    ├── android/
    │   └── README.md     # Play Store listing template
    └── ios/
        └── README.md     # App Store listing template
```

## Environment Variables

### iOS (App Store Connect)

```bash
# Apple ID
export APPLE_ID="developer@company.com"
export APPLE_TEAM_ID="XXXXXXXXXX"
export ITC_TEAM_ID="XXXXXXXXXX"

# App Store Connect API Key (recommended)
export ASC_KEY_ID="XXXXXXXXXX"
export ASC_ISSUER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export ASC_PRIVATE_KEY_P8="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"

# App Config
export IOS_BUNDLE_ID="com.company.app"
export IOS_WORKSPACE="apps/flutter_app/ios/Runner.xcworkspace"
export IOS_SCHEME="Runner"
```

### Android (Google Play)

```bash
# Service Account JSON (single line)
export SUPPLY_JSON_KEY_DATA='{"type": "service_account", ...}'

# App Config
export ANDROID_PACKAGE_NAME="com.company.app"
export ANDROID_AAB_PATH="apps/flutter_app/build/app/outputs/bundle/release/app-release.aab"
```

## Fastlane Lanes

### Android

| Lane | Command | Description |
|------|---------|-------------|
| validate | `fastlane android validate` | Build check |
| internal | `fastlane android internal` | Upload to internal track |
| alpha | `fastlane android alpha` | Upload to alpha track |
| production | `fastlane android production` | Submit to production (10% rollout) |
| metadata | `fastlane android metadata` | Update store listing only |

### iOS

| Lane | Command | Description |
|------|---------|-------------|
| validate | `fastlane ios validate` | Build check |
| beta | `fastlane ios beta` | Upload to TestFlight |
| release | `fastlane ios release` | Submit for App Store review |
| metadata | `fastlane ios metadata` | Update store listing only |
| download_metadata | `fastlane ios download_metadata` | Fetch current metadata |

### Shared

| Lane | Command | Description |
|------|---------|-------------|
| bump_version | `fastlane bump_version type:minor` | Increment version |

## Store Requirements

### Google Play (Android)

- **Target SDK**: API 35+ (required Aug 2025)
- **Signing**: AAB signed with upload key
- **Privacy Policy**: Required
- **Data Safety**: Form must be completed

### App Store (iOS)

- **Deployment Target**: iOS 15+
- **App Review Guidelines**: Must comply
- **Privacy Nutrition Labels**: Required
- **TestFlight**: Beta testing before release

## GitHub Actions Integration

Add these secrets to your repository:

```
# iOS
APPLE_ID
APPLE_TEAM_ID
ASC_KEY_ID
ASC_ISSUER_ID
ASC_PRIVATE_KEY_P8
IOS_BUNDLE_ID

# Android
SUPPLY_JSON_KEY_DATA
ANDROID_PACKAGE_NAME
```

See `.github/workflows/release-*.yml` for CI/CD examples.

## Troubleshooting

### Android

**"targetSdk too low"**: Update `android/app/build.gradle`:
```gradle
android {
    defaultConfig {
        targetSdkVersion 35
    }
}
```

**"AAB not found"**: Run build script first:
```bash
./scripts/build_android.sh
```

### iOS

**"Signing failed"**: Ensure App Store Connect API key is configured.

**"Missing usage descriptions"**: Add to `Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to...</string>
```

## License

MIT - InsightPulse AI
