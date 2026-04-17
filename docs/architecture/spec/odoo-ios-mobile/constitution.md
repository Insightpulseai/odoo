# Constitution — Odoo iOS Wrapper App

## 1. Purpose

This spec governs the design, implementation, and operation of the Odoo iOS app as a wrapper/container for the governed Odoo web/PWA experience on iPhone.

The app exists to improve mobile usability, iOS integration, and controlled access to approved Odoo workflows without creating a second ERP client.

## 2. Scope Doctrine

The iOS app is a shell over Odoo web/PWA, not a parallel mobile product.

It may:
- host approved Odoo web/PWA routes inside an iOS container
- provide native bridges for iOS capabilities that materially improve the hosted experience
- enforce route/domain controls for hosted content
- provide native push, deep link, upload, share, biometric, and telemetry support
- improve stability and operational readiness of Odoo on iPhone

It must not:
- become a second transactional source of truth
- duplicate Odoo business workflows natively in V1 unless explicitly approved as an exception
- bypass Odoo ACLs, approval chains, or finance controls
- embed business logic that belongs in Odoo
- store plaintext secrets or unrestricted ERP data on-device
- silently mutate Odoo state outside governed server-side flows

## 3. Source-of-Truth Doctrine

System authorities are fixed:

- Odoo = transactional system of record and workflow authority
- Azure Boards = goals and portfolio system of record
- Spec Kit bundle = specification system of record
- GitHub = code and pull request system of record
- SSOT machine-readable files = contract truth
- runtime evidence docs = live-state authority

The iOS app is a governed mobile delivery surface over those authorities.

## 4. Architecture Doctrine

The canonical V1 architecture is:

iOS Shell (WKWebView) → Odoo Web/PWA → Odoo Backend

Native code is limited to bridge capabilities such as:
- APNs push notifications
- deep-link routing
- camera and file picker handoff
- share extension handoff
- biometric session resume/lock
- secure token/session storage
- telemetry/crash instrumentation
- limited download/open helpers where policy-approved

No workflow may be reimplemented natively in V1 unless this spec explicitly identifies it as an approved exception.

## 5. Security Doctrine

The wrapper must implement:

- enterprise authentication/session handling aligned to approved identity architecture
- secure cookie/token/session storage
- domain allowlisting and route controls for hosted content
- prevention of unintended navigation to untrusted origins
- least-privilege access enforcement through Odoo/server-side authorization
- auditability of mobile-originated business actions
- safe file upload/download handling
- session invalidation and revoked-user handling

Financially or legally significant actions must remain governed by Odoo-side approval and authorization controls.

## 6. UX Doctrine

The UX priority is not to redesign Odoo wholesale in V1, but to make the hosted Odoo experience usable and reliable on iPhone.

The wrapper must prioritize:
- fast launch and resume
- stable login/session behavior
- safe hosted navigation
- usable deep links into approved routes
- reliable camera/share/file upload handoff
- readable mobile viewport behavior
- deterministic loading/error/offline states
- accessibility and predictable iOS behavior

## 7. Delivery Doctrine

All work must be:
- repo-first
- testable in CI
- evidence-backed
- deterministic in artifact naming and paths
- deployable without manual business-logic edits in production
- constrained to wrapper-first scope unless later phases explicitly expand the product

## 8. Integration Doctrine

The wrapper integrates with Odoo primarily through hosted web/PWA routes and narrow native-to-web bridge contracts.

Allowed integration surfaces:
- approved Odoo web/PWA routes
- JS/native bridge events for uploads, notifications, deep links, and session helpers
- APNs notification routing into governed Odoo routes
- signed or governed upload flows already supported by Odoo/web stack

Disallowed V1 patterns:
- replacing core Odoo workflows with native business forms by default
- direct mobile-to-database access
- client-trusted authorization or business state
- broad new mobile-only domain APIs unless a wrapper limitation explicitly requires them

## 9. Wrapper-First Doctrine

Wrapper-first is the governing delivery rule.

This means:
- Odoo web/PWA remains the primary workflow UX surface
- native code exists only to improve iOS usability and platform integration
- any native replacement of a hosted workflow must be treated as a future exception, separately justified and explicitly approved in spec

## 9A. Asset Doctrine

The wrapper must use a controlled visual-asset stack for icons, avatars, and illustrations.

### Approved Primary Asset Sources
- Icons: Fluent System Icons
- Avatars: DiceBear
- Illustrations: unDraw

### Approved Secondary Asset Source
- Storyset may be used for onboarding, help, or marketing-style illustration surfaces where richer expressive artwork is needed.

### Usage Rules
- One primary icon family must be used consistently across the product UI
- Avatars must be deterministic and seed-based for placeholder or generated identities
- Illustrations must be used sparingly and only where they improve comprehension, such as:
  - empty states
  - onboarding
  - blocked states
  - help/support surfaces
- Core ERP, finance, approval, OCR, cash advance, and liquidation routes must prioritize icons, statuses, and structured data over decorative artwork
- Any deviation from the approved primary asset sources must be explicitly approved in spec

## 9B. Liquid Glass Doctrine (iOS 26+)

The wrapper must adopt Apple's Liquid Glass design language when compiled with the iOS 26 SDK.

### Adoption Rules
- The tab bar must use the new SwiftUI `Tab` API with `.tabBarMinimizeBehavior(.onScrollDown)` for content-first scrolling
- Native overlay components (floating buttons, banners, lock screens) must use `.glassEffect(.regular)` or `.glassEffect(.regular.interactive())`
- The `.clear` glass variant is permitted only over media-rich content (camera preview, document viewer)
- Liquid Glass must be applied exclusively to the navigation/control layer, never to content views
- All glass-enabled components must fall back gracefully on iOS 16-25 using the app's navy/green palette tokens

### Compatibility
- iOS 26+: Full Liquid Glass via SwiftUI `glassEffect()` modifier
- iOS 16-25: Solid navy backgrounds, white card surfaces, standard UIKit blur effects
- The `UIDesignRequiresCompatability` plist key must NOT be set — the app must adopt Liquid Glass, not opt out

### Implementation
- `LiquidGlassTabView.swift`: SwiftUI root view with 5-tab glass bar
- `GlassEffectComponents.swift`: Reusable glass button, card, banner, and lock screen components
- `SceneDelegate.swift`: Routes to SwiftUI host on iOS 26+, UIKit fallback on earlier

## 10. Acceptance Doctrine

A wrapper feature is not complete unless it has:
- spec coverage
- route/bridge contract definition
- RBAC and denial-path definition
- telemetry and audit mapping
- failure-mode handling
- test coverage
- runtime verification evidence
