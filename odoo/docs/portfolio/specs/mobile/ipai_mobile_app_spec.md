# IPAI Mobile App - Flutter + Odoo 19 CE Integration

**Version**: 1.0.0
**Target Platforms**: Android (Google Play) + iOS (App Store)
**Stack**: Flutter + Fastlane + Supabase + Odoo JSON-RPC

---

## Overview

CI-first mobile app for Odoo 19 CE with:

- ✅ **Flutter** for cross-platform (Android + iOS)
- ✅ **Fastlane** for automated build + deploy (no UI)
- ✅ **Supabase Flutter** for push/auth/offline sync
- ✅ **Odoo JSON-RPC** client for ERP integration
- ✅ **GitHub Actions** for CI/CD

---

## Architecture

```
mobile/odoo_client/
├── lib/
│   ├── main.dart                    # App entry
│   ├── src/
│   │   ├── odoo/
│   │   │   ├── odoo_client.dart     # JSON-RPC client
│   │   │   ├── models/              # Freezed models
│   │   │   └── services/            # Business logic
│   │   ├── supabase/
│   │   │   ├── supabase_client.dart # Supabase integration
│   │   │   └── offline_queue.dart   # Offline sync
│   │   └── ui/
│   │       ├── screens/             # App screens
│   │       └── widgets/             # Reusable widgets
├── android/
│   └── fastlane/
│       └── Fastfile                 # Android CI lanes
├── ios/
│   └── fastlane/
│       └── Fastfile                 # iOS CI lanes
├── tool/
│   └── odoo_login_smoke.dart        # Auth smoke test
└── .github/workflows/
    └── mobile-release.yml           # CI/CD workflow
```

---

## Dependencies

### Core

```yaml
dependencies:
  flutter:
    sdk: flutter

  # Odoo JSON-RPC
  http: ^1.1.0
  dio: ^5.4.0
  flutter_secure_storage: ^9.0.0

  # Supabase
  supabase_flutter: ^2.0.0

  # State management
  riverpod: ^2.4.0
  flutter_riverpod: ^2.4.0

  # Models
  json_annotation: ^4.8.1
  freezed_annotation: ^2.4.1

  # UI
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0

dev_dependencies:
  build_runner: ^2.4.7
  json_serializable: ^6.7.1
  freezed: ^2.4.6
  flutter_test:
    sdk: flutter
```

---

## Odoo JSON-RPC Client

### Authentication

```dart
class OdooClient {
  Future<OdooSession> login({
    required String db,
    required String username,
    required String password,
  }) async {
    final res = await _dio.post('/web/session/authenticate', data: {
      'jsonrpc': '2.0',
      'method': 'call',
      'params': {'db': db, 'login': username, 'password': password},
    });

    // Extract session_id cookie
    final sessionId = _extractSessionId(res.headers['set-cookie']);
    _dio.options.headers['Cookie'] = 'session_id=$sessionId';

    return OdooSession(uid: result['uid'], sessionId: sessionId);
  }
}
```

### Model Operations

```dart
Future<List<dynamic>> search({
  required String model,
  List<dynamic> domain = const [],
  List<String> fields = const [],
  int limit = 80,
}) async {
  return await callKw(
    model: model,
    method: 'search_read',
    kwargs: {
      'domain': domain,
      'fields': fields,
      'limit': limit,
    },
  );
}
```

---

## Supabase Integration

### Initialization

```dart
await Supabase.initialize(
  url: env['SUPABASE_URL']!,
  anonKey: env['SUPABASE_ANON_KEY']!,
);
```

### Offline Queue

```dart
class OfflineQueue {
  Future<void> enqueue(OdooOperation op) async {
    await supabase.from('offline_queue').insert({
      'operation': op.toJson(),
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  Future<void> sync() async {
    final pending = await supabase
      .from('offline_queue')
      .select()
      .order('created_at');

    for (final item in pending) {
      await _executeOperation(item['operation']);
      await supabase.from('offline_queue').delete().eq('id', item['id']);
    }
  }
}
```

---

## Fastlane Configuration

### Android (Google Play)

**`android/fastlane/Fastfile`**:

```ruby
default_platform(:android)

platform :android do
  desc "Build AAB"
  lane :build do
    sh("cd .. && flutter build appbundle --release")
  end

  desc "Upload to Google Play (internal track)"
  lane :play_internal do
    build
    supply(
      aab: "../build/app/outputs/bundle/release/app-release.aab",
      track: "internal",
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end

  desc "Promote internal to production"
  lane :promote_production do
    supply(
      track: "internal",
      track_promote_to: "production",
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end
end
```

### iOS (App Store Connect)

**`ios/fastlane/Fastfile`**:

```ruby
default_platform(:ios)

platform :ios do
  desc "Build IPA"
  lane :build do
    sh("cd .. && flutter build ipa --release --export-options-plist=ios/ExportOptions.plist")
  end

  desc "Upload IPA to App Store Connect"
  lane :appstore do
    build
    upload_to_app_store(
      ipa: "../build/ios/ipa/*.ipa",
      skip_metadata: true,
      skip_screenshots: true
    )
  end
end
```

---

## CI/CD Workflow

### GitHub Actions

**`.github/workflows/mobile-release.yml`**:

```yaml
name: mobile-release

on:
  workflow_dispatch:
  push:
    tags:
      - "mobile-v*"

jobs:
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: "stable"

      - name: Install dependencies
        working-directory: mobile/odoo_client
        run: flutter pub get

      - name: Run tests
        working-directory: mobile/odoo_client
        run: flutter test

      - name: Install Ruby deps
        working-directory: mobile/odoo_client/android
        run: bundle install

      - name: Build+Upload Internal
        working-directory: mobile/odoo_client/android
        env:
          SUPPLY_JSON_KEY_DATA: ${{ secrets.GOOGLE_PLAY_JSON_KEY }}
        run: bundle exec fastlane android play_internal

  ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: "stable"

      - name: Install dependencies
        working-directory: mobile/odoo_client
        run: flutter pub get

      - name: Run tests
        working-directory: mobile/odoo_client
        run: flutter test

      - name: Install Ruby deps
        working-directory: mobile/odoo_client/ios
        run: bundle install

      - name: Build+Upload
        working-directory: mobile/odoo_client/ios
        env:
          APP_STORE_CONNECT_API_KEY: ${{ secrets.APP_STORE_CONNECT_API_KEY }}
        run: bundle exec fastlane ios appstore
```

---

## Environment Configuration

**`.env.example`**:

```bash
ODOO_BASE_URL=https://erp.insightpulseai.com
ODOO_DB=odoo
SUPABASE_URL=https://YOURPROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR_ANON_KEY
```

---

## Smoke Tests

### Odoo Auth Test

**`tool/odoo_login_smoke.dart`**:

```dart
import 'dart:io';
import '../lib/src/odoo/odoo_client.dart';

Future<void> main() async {
  final baseUrl = Platform.environment['ODOO_BASE_URL']!;
  final db = Platform.environment['ODOO_DB']!;
  final user = Platform.environment['ODOO_USER']!;
  final pass = Platform.environment['ODOO_PASS']!;

  final c = OdooClient(baseUrl: baseUrl);
  final s = await c.login(db: db, username: user, password: pass);
  stdout.writeln('OK uid=${s.uid} session=${s.sessionId.substring(0, 6)}…');
}
```

**Run**:

```bash
export ODOO_BASE_URL="https://erp.insightpulseai.com"
export ODOO_DB="odoo"
export ODOO_USER="YOUR_USER"
export ODOO_PASS="YOUR_PASS"
dart run tool/odoo_login_smoke.dart
```

---

## Store Requirements

### Android (Google Play)

#### Target API Level

- **Requirement**: Apps must target API level 34 (Android 14) or higher
- **CI Guard**: Fail builds if `targetSdkVersion < 34`

**`android/app/build.gradle`**:

```gradle
android {
    compileSdkVersion 34

    defaultConfig {
        targetSdkVersion 34
        minSdkVersion 21
    }
}
```

#### Play App Signing

- Google manages release signing keys
- Upload signing key is separate from release key
- CI uploads AAB, Google signs and distributes

#### Credentials

- **Option 1**: Service account JSON key (stored in GitHub Secrets)
- **Option 2**: Workload Identity Federation (recommended for GitHub Actions)

### iOS (App Store)

#### Signing

- **Automatic signing** in Xcode (for local dev)
- **Manual signing** in CI via `fastlane match`

**`ios/ExportOptions.plist`**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>method</key><string>app-store</string>
  <key>uploadBitcode</key><false/>
  <key>compileBitcode</key><false/>
  <key>signingStyle</key><string>automatic</string>
</dict>
</plist>
```

#### App Store Connect API Key

- Generate API key in App Store Connect
- Store in GitHub Secrets as `APP_STORE_CONNECT_API_KEY`
- Fastlane uses key for automated uploads

---

## Brand & Trademark

### App Identity

- **App Name**: "IPAI Mobile" (not "Odoo")
- **Bundle ID**: `com.insightpulseai.odoo_client`
- **Description**: "Mobile client for Odoo ERP by InsightPulse AI"

### Legal

- ✅ Don't use "Odoo" trademark in app name
- ✅ Describe as "Odoo client" or "Odoo-compatible"
- ✅ Use your own branding (IPAI/TBWA)

---

## Integration with IPAI Custom Modules

### Allowed Mobile-Related Modules

Add to `spec/ipai_custom_modules_allowlist.yaml`:

```yaml
allowlist:
  platform_glue:
    - ipai_mobile_api_bridge # Mobile-specific API endpoints
    - ipai_push_notifications # FCM/APNs integration
```

### Mobile API Bridge

**Purpose**: Expose mobile-optimized endpoints

- Lightweight JSON responses (no HTML)
- Batch operations for offline sync
- Push notification registration

**Implementation**: Thin Odoo controller, no business logic

```python
class MobileAPIController(http.Controller):
    @http.route('/api/mobile/sync', type='json', auth='user')
    def sync(self, last_sync_timestamp):
        # Return delta since last sync
        return {
            'invoices': self._get_updated_invoices(last_sync_timestamp),
            'expenses': self._get_updated_expenses(last_sync_timestamp),
        }
```

---

## Deployment Checklist

### One-Time Setup

#### Android

- [ ] Create Google Play Console account
- [ ] Create app listing
- [ ] Generate upload keystore
- [ ] Create service account for CI
- [ ] Enable Play App Signing
- [ ] Add service account JSON to GitHub Secrets

#### iOS

- [ ] Create Apple Developer account
- [ ] Create App Store Connect app
- [ ] Generate App Store Connect API key
- [ ] Set up `fastlane match` for code signing
- [ ] Add API key to GitHub Secrets

### Per-Release

#### Android

```bash
# Tag release
git tag mobile-v1.0.0
git push origin mobile-v1.0.0

# CI builds and uploads to internal track
# Manually promote to production in Play Console
```

#### iOS

```bash
# Tag release
git tag mobile-v1.0.0
git push origin mobile-v1.0.0

# CI builds and uploads to App Store Connect
# Manually submit for review in App Store Connect
```

---

## Risks & Mitigations

### Risk: Store Policy Changes

- **Mitigation**: CI guard for target API level
- **Action**: Monitor Google/Apple developer news

### Risk: Signing Key Loss

- **Mitigation**: Use Play App Signing (Android), `fastlane match` (iOS)
- **Action**: Backup keys to secure vault

### Risk: Offline Sync Conflicts

- **Mitigation**: Last-write-wins with conflict queue
- **Action**: User review for conflicts

### Risk: API Breaking Changes

- **Mitigation**: Version mobile API endpoints
- **Action**: Graceful degradation for old clients

---

## Next Steps

1. **Scaffold Flutter app** (`flutter create`)
2. **Implement Odoo JSON-RPC client**
3. **Add Supabase integration**
4. **Configure Fastlane lanes**
5. **Set up GitHub Actions**
6. **One-time store setup**
7. **First release to internal track**
8. **User acceptance testing**
9. **Promote to production**

---

## References

- [Flutter Documentation](https://docs.flutter.dev/)
- [Fastlane Documentation](https://docs.fastlane.tools/)
- [Supabase Flutter](https://pub.dev/pkgs/supabase_flutter)
- [Google Play Console](https://play.google.com/console)
- [App Store Connect](https://appstoreconnect.apple.com/)
