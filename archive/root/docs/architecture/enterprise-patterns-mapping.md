# Next Enterprise to OdooOps Mapping

This reference maps the enterprise-grade patterns from the [next-enterprise](https://github.com/Blazity/next-enterprise) boilerplate to the improvements required for the OdooOps "Engineering System Success" pillar.

## Core Infrastructure & Quality

| Feature                  | IPAI Mapping / Action                                       | WAF Pillar Alignment                               |
| :----------------------- | :---------------------------------------------------------- | :------------------------------------------------- |
| **Vitest**               | Transition from Jest to Vitest in `odooops-console`.        | **Performance Efficiency** (Faster feedback loops) |
| **Playwright**           | Integrate Playwright for E2E testing of console dashboards. | **Reliability** (Shift-left testing)               |
| **T3 Env**               | Implement `env.ts` for type-safe environment variables.     | **Operational Excellence** (Configuration safety)  |
| **OpenTelemetry**        | Integrate distributed tracing for OdooOps API calls.        | **Observability** (Refined Architecture)           |
| **Conventional Commits** | Enforce via husky/commitlint in the Odoo repo.              | **Operational Excellence** (Clearer changelogs)    |

## Developer Productivity (Golden Paths)

| Feature             | IPAI Mapping / Action                                  | WAF Pillar Alignment                                  |
| :------------------ | :----------------------------------------------------- | :---------------------------------------------------- |
| **Storybook**       | Implement component library for Odoo UI/UX components. | **Productivity** (Component isolation)                |
| **Bundle Analyzer** | Add to Next.js config to monitor console weight.       | **Performance Efficiency** (Golden Path optimization) |
| **Lighthouse CI**   | Add to GitHub Actions to prevent UX regression.        | **Operational Excellence** (Quality gates)            |
| **Renovate BOT**    | Automate pinning of Odoo/Supabase dependencies.        | **Resiliency** (Automated security updates)           |

## Implementation Roadmap

1.  **Testing Upgrade**: Replace `jest` setup with `vitest` to match modern ESM standards.
2.  **Environment Safety**: Scaffold `t3-oss/env-nextjs` into the console and docs app.
3.  **Governance Enforcement**: Add `commitlint` to the CI gate to enforce standard messaging.
