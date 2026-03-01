# odoo-mobile-ios — Phase 2 Evidence

**Stamp**: 2026-03-01T10:50+0800
**Branch**: feat/ipai-module-audit-odoo19
**Scope**: `apps/odoo-mobile-ios/`
**Swift**: 6.2.3 (arm64-apple-macosx26.0)

---

## STATUS=COMPLETE

**26 / 26 tests passed** — 3 suites, 0 failures.

---

## [CONTEXT]

- **repo**: /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
- **branch**: feat/ipai-module-audit-odoo19
- **cwd**: apps/odoo-mobile-ios
- **goal**: Implement PKCE in SSOAuthSession, OdooClient tests + uploadDocument multipart, run 26-test suite
- **stamp**: 2026-03-01T10:50+0800

---

## [EVIDENCE]

### Build

```
command: swift build (macOS arm64)
result:  PASS — Build complete (1.17s)
```

### Test Run

```
command: swift test -Xswiftc -F<CLT/Frameworks> -Xlinker -rpath <CLT/Frameworks>
result:  PASS — 26 tests in 3 suites passed after 0.158 seconds.
saved_to: logs/swift_test_full.log
```

| Suite | Tests | Result | Duration |
|-------|-------|--------|----------|
| DeepLinkRouter | 14 | ✅ All passed | 0.007s |
| TokenStore | 5 | ✅ All passed | 0.157s |
| OdooClient | 7 | ✅ All passed | 0.123s |

#### OdooClient — 7 new tests

| Test | Result |
|------|--------|
| call POSTs to /web/dataset/call_kw with JSON content-type | ✅ passed |
| call body encodes jsonrpc:2.0, model, and method | ✅ passed |
| call decodes typed result from JSON-RPC envelope | ✅ passed |
| call throws URLError on HTTP 500 | ✅ passed |
| uploadDocument POSTs multipart to /web/binary/upload_attachment | ✅ passed |
| uploadDocument body contains filename, model, and file bytes | ✅ passed |
| uploadDocument throws URLError on HTTP 403 | ✅ passed |

---

## [CHANGES]

| File | Change |
|------|--------|
| `Sources/Features/Auth/SSOAuthSession.swift` | PKCE implemented (already in prior session; `struct` form confirmed) |
| `Sources/Shared/OdooClient.swift` | `uploadDocument()` multipart POST to `/web/binary/upload_attachment` fully implemented; returns `ir.attachment` ID |
| `Tests/OdooClientMocks.swift` | New — `MockURLProtocol` URLProtocol interceptor; drains `httpBodyStream` (URLSession converts `httpBody`→stream); request capture as primitive types so test file needs no `import Foundation` |
| `Tests/OdooClientTests.swift` | New — 7 Swift Testing tests for `OdooClient.call()` (request shape, payload encoding, result decoding, error handling) and `uploadDocument()` (endpoint, multipart body, auth failure) |

---

## [NOTES]

### Why OdooClient tests use mocks

`odoo_dev` database is not accessible from macOS (production runs `list_db=False`,
no local database available). Mock `URLProtocol` intercepts `URLSession` at the
transport level — tests verify request construction and response parsing without
any live network dependency.

### httpBodyStream vs httpBody

`URLSession` converts `URLRequest.httpBody` to `httpBodyStream` internally before
passing the request to `URLProtocol.startLoading()`. `request.httpBody` is always
`nil` in `startLoading()`. Fix: drain `httpBodyStream` manually with a 4096-byte
read loop.

### _Testing_Foundation cross-import overlay (CLT constraint)

Same constraint as Phase 1: no file may have both `import Foundation` and
`import Testing`. Split:
- `OdooClientMocks.swift` — `import Foundation` only; provides `MockURLProtocol`,
  capture properties (primitive types), and Data/response helpers.
- `OdooClientTests.swift` — `import Testing` only; accesses captured data via
  `MockURLProtocol.capturedPath` (`String?`) etc., never names Foundation types.

---

## [NEXT - DETERMINISTIC]

1. `xcodes install "16.4"` requires Apple ID — provide credentials to enable Simulator tests
2. Wire `OdooClient.call` → live `odoo_dev` JSON-RPC (requires local Odoo dev instance)
3. Complete `OfflineQueue` CoreData store (marked TODO in source)
4. Add `BiometricGate` tests (LAContext requires device/simulator, not testable on macOS CLT)
5. Run `xcodebuild test -destination "platform=iOS Simulator,name=iPhone 16"` in CI
