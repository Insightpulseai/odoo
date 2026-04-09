# Odoo Browser Tooling Strategy

> Defines the three-layer browser testing and debugging stack for the Odoo platform.
> Companion to `docs/architecture/ODOO_MODULE_DOCTRINE.md` (Browser Automation and Debugging Doctrine).

---

## Layer 1: Odoo-Native Correctness Tests

**Authority**: Server-side and form-level correctness.

| Test class | When to use |
| --- | --- |
| `TransactionCase` | ORM logic, computed fields, constraints, defaults |
| `Form` (odoo.tests.common) | Onchange, form save/load, field visibility |
| `HttpCase` | Controller routes, RPC, full request lifecycle |
| Tours (`odoo.tour`) | End-to-end UI flows exercised through the Odoo tour runner |

**Scope**: Every bug fix and feature that touches a model, view, or controller must have at least one Odoo-native test. This layer is the correctness authority and runs on every PR.

---

## Layer 2: Playwright Browser Regression Tests

**Authority**: Browser-level rendering, navigation, and client stability.

### Preferred First Smoke Targets

1. Login page load and successful authentication
2. Apps menu renders and all installed app tiles are clickable
3. Settings page opens, a toggle is changed, and Save completes without error

### What Playwright Owns

- Page load and navigation smoke (menu, breadcrumb, back)
- Settings open/save round-trip
- Client action stability (no JS crash on navigation)
- Cross-browser verification (Chromium, Firefox, WebKit)
- Screenshot and trace capture for failure evidence

### What Playwright Does Not Own

- Business logic correctness (use Odoo-native tests)
- ORM/access rule enforcement (use TransactionCase)
- Data seeding or fixture management (use Odoo test fixtures)

---

## Layer 3: Chrome DevTools MCP Debugging

**Authority**: Interactive investigation of browser-side failures.

### When to Use

- A Playwright test fails and the root cause is unclear from traces alone
- Network waterfall inspection is needed (slow RPC, failed asset load)
- JS console errors need structured capture
- DOM state inspection during a specific failure condition
- Performance profiling of a browser-heavy view

### What DevTools MCP Does Not Own

- Automated regression coverage (use Playwright)
- CI gating (DevTools MCP is never a CI step)
- Correctness proof (use Odoo-native tests)

---

## Tool Selection Rules

| Situation | Tool |
| --- | --- |
| Model/form/controller logic changed | Odoo-native test (TransactionCase, Form, HttpCase) |
| Browser crash or rendering regression reported | Playwright regression test |
| Settings page or menu navigation broke | Playwright smoke + Odoo-native Form test |
| JS error in console, cause unknown | Chrome DevTools MCP investigation |
| Cross-browser rendering issue | Playwright multi-browser run |
| Performance regression in browser | Chrome DevTools MCP profiling |
| New feature with UI surface | Odoo-native test first, then Playwright smoke if navigation-critical |

---

## CI Expectations

| Layer | PR gate | Nightly | On-demand |
| --- | --- | --- | --- |
| Odoo-native tests | Yes (required) | Yes | Yes |
| Playwright smoke (login, apps, settings) | Yes (required) | Yes | Yes |
| Playwright broader regression suite | No | Yes | Yes |
| Chrome DevTools MCP | No | No | Yes (investigation only) |

### CI Pipeline Integration

- Odoo-native tests run inside the devcontainer against a disposable `test_<module>` database.
- Playwright smoke tests run in a headless browser against a running Odoo instance (devcontainer or CI service).
- Playwright traces and screenshots are uploaded as CI artifacts on failure.
- Chrome DevTools MCP is never part of CI. It is used by developers during local investigation.

---

## Definition of Done for Browser Regressions

A browser regression is resolved when all of the following are true:

1. **Root cause identified** — documented in the issue/PR with evidence (trace, screenshot, console log)
2. **Odoo-native test added** — TransactionCase or Form test proving the server-side fix is correct
3. **Playwright regression test added** — reproduces the original browser failure and now passes
4. **CI green** — both Odoo-native and Playwright smoke gates pass
5. **Evidence captured** — screenshots/traces saved to `docs/evidence/<date>/<scope>/`

If the regression was found via Chrome DevTools MCP, the investigation findings (console errors, network failures, DOM state) must be attached to the issue before the fix PR is opened.

---

*Last updated: 2026-04-05*
