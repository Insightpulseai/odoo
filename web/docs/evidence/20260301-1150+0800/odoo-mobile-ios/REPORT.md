# odoo-mobile-ios — Phase 3 Evidence

**Stamp**: 2026-03-01T11:50+0800
**Branch**: feat/ipai-module-audit-odoo18
**Scope**: `apps/odoo-mobile-ios/`
**Swift**: 6.2.3 (arm64-apple-macosx26.0)

---

## STATUS=COMPLETE

**30 / 30 tests passed** — 4 suites, 0 failures.

---

## [CONTEXT]

- **repo**: /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
- **branch**: feat/ipai-module-audit-odoo18
- **cwd**: apps/odoo-mobile-ios
- **goal**: Implement OfflineQueue CoreData store + 4 tests; add GitHub Actions Swift CI workflow
- **stamp**: 2026-03-01T11:50+0800

---

## [EVIDENCE]

### Build

```
command: swift build (macOS arm64)
result:  PASS — Build complete (1.15s)
```

### Test Run

```
command: swift test -Xswiftc -F<CLT/Frameworks> -Xlinker -rpath <CLT/Frameworks>
result:  PASS — 30 tests in 4 suites passed after 0.094 seconds.
saved_to: logs/swift_test_full.log
```

| Suite | Tests | Result | Duration |
|-------|-------|--------|----------|
| DeepLinkRouter | 14 | ✅ All passed | 0.001s |
| TokenStore | 5 | ✅ All passed | 0.094s |
| OdooClient | 7 | ✅ All passed | 0.055s |
| **OfflineQueue** | **4** | ✅ **All passed** | **0.030s** |

#### OfflineQueue — 4 new tests

| Test | Result |
|------|--------|
| pendingCount is zero for an empty queue | ✅ passed |
| enqueue increases pendingCount by one per call | ✅ passed |
| sync removes items when server returns HTTP 200 | ✅ passed |
| sync retains items when server returns HTTP 500 | ✅ passed |

---

## [CHANGES]

| File | Change |
|------|--------|
| `Sources/Features/Offline/OfflineQueue.swift` | Full CoreData implementation: programmatic `NSManagedObjectModel` (no `.xcdatamodeld` file, SPM-compatible), `makeInMemory()` factory, `enqueue()`, `sync()`, `pendingCount` |
| `Tests/OdooClientMocks.swift` | Added `OfflineQueueMockProtocol` + `queueSyncSession()` — dedicated mock with separate static state to prevent inter-suite races |
| `Tests/OfflineQueueTests.swift` | New — 4 Swift Testing tests for OfflineQueue |
| `.github/workflows/odoo-mobile-ios-swift-tests.yml` | New — CI workflow: Job 1 `swift test` (macOS CLT, blocking), Job 2 `xcodebuild test` iOS Simulator (continue-on-error until Xcode 16.4 pinned) |

---

## [NOTES]

### Programmatic CoreData model (SPM constraint)

`NSPersistentContainer(name: "OdooMobile")` looks for a compiled `.momd` bundle
resource — not available in Swift Package Manager. Fix: build `NSManagedObjectModel`
programmatically via `NSEntityDescription` + `NSAttributeDescription`, then pass to
`NSPersistentContainer(name:managedObjectModel:)`.

Entity: `QueuedAction` with 5 attributes (`id_`, `model_`, `method_`, `payload_`,
`queuedAt_`). All attributes are stored as primitive types (`String`, `BinaryData`,
`Date`) — no `@NSManaged` subclass required.

### Inter-suite mock race (root cause + fix)

`OdooClientTests` and `OfflineQueueTests` are separate `@Suite` instances and run in
**parallel** by Swift Testing. `.serialized` only prevents intra-suite parallelism.

When both suites used `MockURLProtocol` (single shared class with static state), the
`OfflineQueueTests` "sync retains on HTTP 500" test read the HTTP-200 handler set by
the concurrent OdooClient test — causing `pendingCount == 0` instead of `1`.

Fix: `OfflineQueueMockProtocol` is a separate `URLProtocol` subclass with its own
static `statusCode` / `responseBodyData`. Both suites serialize internally; they no
longer share any static state.

### In-memory CoreData for tests

```swift
// /dev/null → in-memory only; no SQLite file written
cont.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
```

Used by `OfflineQueue.makeInMemory()` — each test creates a fresh instance.

### CI workflow structure

- **Job 1** (`macos-swift-clt`): deterministic gate — `swift build && swift test`,
  no Xcode, no Apple ID. Blocks merge on failure.
- **Job 2** (`ios-simulator`): `xcodebuild test -destination "platform=iOS Simulator,…"`,
  `continue-on-error: true` until Xcode 16.4 is pinned in CI. Uploads `.xcresult` bundle.

---

## [NEXT - DETERMINISTIC]

1. `xcodes install "16.4"` — **[MANUAL_REQUIRED]** Apple ID credentials needed; enables local Simulator test runs
2. Pin `DEVELOPER_DIR=/Applications/Xcode_16.x.app/Contents/Developer` in CI workflow and flip `continue-on-error: false` once Simulator test is green
3. Wire `OdooClient.call` → live `odoo_dev` JSON-RPC (requires local Odoo 18 dev instance)
4. Add `BiometricGate` tests (LAContext requires device/simulator, not testable on macOS CLT)
