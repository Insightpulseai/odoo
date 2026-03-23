# Concur Feature Parity Map — InsightPulse iOS Wrapper

> Maps SAP Concur mobile app capabilities to InsightPulse wrapper equivalents.
> Concur is the enterprise benchmark; this doc tracks feature coverage.

---

## Feature Matrix

| # | Concur Feature | InsightPulse Equivalent | Layer | Status |
|---|---------------|------------------------|-------|--------|
| **Expense Management** |
| 1 | Create expense report | Odoo Expense via hosted web | WKWebView | Hosted |
| 2 | Submit expense report | Odoo Expense submit action | WKWebView | Hosted |
| 3 | Expense categories | Odoo expense categories | WKWebView | Hosted |
| 4 | Payment method tracking | Odoo journal/payment fields | WKWebView | Hosted |
| 5 | Corporate card matching | Odoo bank statement reconciliation | WKWebView | Planned |
| **Receipt Capture & OCR** |
| 6 | Camera receipt capture | Native camera → OCR bridge | Native | **To Build** |
| 7 | AI receipt data extraction | Azure Document Intelligence (`ocr.insightpulseai.com`) | Native+API | **To Build** |
| 8 | Auto-categorization from receipt | AI suggestion from OCR result | Native+API | **To Build** |
| 9 | Hotel bill itemization (GenAI) | Azure Document Intelligence custom model | API | Planned |
| 10 | Multilingual receipt support | Azure Document Intelligence (90+ languages) | API | Available |
| 11 | Offline receipt queue | Local capture queue, sync on connectivity | Native | **To Build** |
| **Mileage & Distance** |
| 12 | GPS mileage tracking | CoreLocation distance tracking | Native | **To Build** |
| 13 | Point-to-point calculation | MapKit route distance | Native | **To Build** |
| 14 | Auto reimbursement rate | Odoo expense policy rules | WKWebView | Hosted |
| **Approval Workflows** |
| 15 | Manager approval inbox | Odoo approval routes via push deep link | WKWebView+Push | Hosted |
| 16 | Approve/reject from notification | Push → deep link → Odoo action | Native+WKWebView | Implemented |
| 17 | Approval delegation | Odoo delegation rules | WKWebView | Hosted |
| **Travel Integration** |
| 18 | Travel booking | Not in scope (no Concur Travel equivalent) | — | N/A |
| 19 | Itinerary management | Not in scope V1 | — | N/A |
| 20 | Real-time travel alerts | Not in scope V1 | — | N/A |
| **Dashboard & Reporting** |
| 21 | Spending summary dashboard | Hosted Odoo dashboard + native tab | WKWebView | Hosted |
| 22 | Category breakdown charts | Hosted Odoo analytics | WKWebView | Hosted |
| 23 | Budget vs actual tracking | Odoo budget module | WKWebView | Hosted |
| 24 | Export CSV/PDF | Odoo report export | WKWebView | Hosted |
| **Platform Capabilities** |
| 25 | Push notifications | APNs registration + deep link routing | Native | Implemented |
| 26 | Biometric authentication | Face ID / Touch ID gate | Native | Implemented |
| 27 | Offline mode | Receipt queue + cached session | Native | **To Build** |
| 28 | Deep linking | Universal Links → WKWebView route | Native | Implemented |
| 29 | Share extension | iOS Share Sheet → Odoo intake | Native | **To Build** |
| 30 | Secure session persistence | Keychain-backed session tokens | Native | **To Build** |

---

## Priority Build Items (Native Bridges)

### P0 — Receipt Capture → OCR Pipeline

The highest-value native feature gap. Concur's ExpenseIt is their primary differentiator.

**Flow:**
```
Camera Capture → Local Image → Upload to ocr.insightpulseai.com
→ Azure Document Intelligence extracts fields
→ Return: amount, date, vendor, category, currency, line items
→ Pre-fill Odoo expense form → Navigate to hosted expense route
```

**Files to create:**
- `Sources/CameraCaptureBridge.swift` — Native camera UI with crop/flash
- `Sources/OCRService.swift` — Upload to Document Intelligence, parse response
- `Sources/ReceiptQueueManager.swift` — Offline queue with retry

### P1 — Mileage Tracking

**Flow:**
```
Start Trip → CoreLocation tracking → Distance accumulated
→ Stop Trip → Calculate reimbursement at policy rate
→ Create Odoo expense entry with distance metadata
```

**Files to create:**
- `Sources/MileageTracker.swift` — CoreLocation distance tracking
- `Sources/MileageExpenseBridge.swift` — Create expense from trip data

### P2 — Share Extension

**Flow:**
```
iOS Share Sheet (Photos, Files, Safari) → App Extension
→ Validate file type → Route to receipt capture or document intake
→ Open app at correct Odoo hosted route
```

**Files to create:**
- `ShareExtension/ShareViewController.swift` — Share extension entry point
- `ShareExtension/Info.plist` — Extension configuration

### P3 — Secure Session / Keychain

**Flow:**
```
Login → Store session token in Keychain
→ App resume → Retrieve from Keychain → Inject into WKWebView
→ Token expired → Show re-auth flow
```

**Files to create:**
- `Sources/KeychainService.swift` — Keychain CRUD wrapper
- `Sources/SessionManager.swift` — Token lifecycle + WKWebView injection

---

## What We Intentionally Skip (vs Concur)

| Concur Feature | Why Skip |
|---------------|----------|
| Travel booking | No travel module in Odoo CE scope |
| TripIt Pro integration | No travel itinerary requirement |
| Visa/vaccination requirements | Out of scope for expense wrapper |
| Corporate card feed integration | Requires bank API contracts (future phase) |
| Multi-entity expense routing | Single-entity V1 |

---

## Concur vs InsightPulse Architecture Comparison

| Aspect | SAP Concur | InsightPulse |
|--------|-----------|-------------|
| Architecture | Full native app | Wrapper-first (WKWebView + native bridges) |
| Backend | Concur cloud | Odoo CE 19 on Azure |
| OCR Engine | Concur ExpenseIt (proprietary) | Azure Document Intelligence |
| AI | Concur GenAI (SAP BTP) | Azure OpenAI |
| Identity | Concur SSO | Keycloak → Entra ID |
| Offline | Full offline with sync | Receipt queue only (V1) |
| Design System | SAP Fiori | Fluent System Icons + Liquid Glass |

---

*Created: 2026-03-22*
*Spec bundle: `spec/odoo-ios-mobile/`*
