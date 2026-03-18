# Marketplace

Global readiness standards and per-offer status tracking.

## Structure

```
marketplace/
├── README.md                                    # This file
├── docs/
│   └── MARKETPLACE_READINESS_CHECKLIST.md       # Global readiness standard
└── offers/
    └── odooops-control-plane/
        └── READINESS.md                         # Per-offer status
```

## Usage

- **Global standard**: `docs/MARKETPLACE_READINESS_CHECKLIST.md` defines the 10-section checklist (A–J) applied to every offer.
- **Per-offer tracking**: Each offer under `offers/<offer-slug>/READINESS.md` captures current readiness level and blockers.
- **Readiness levels**: 0 (Scaffolded) → 1 (Alpha) → 2 (Beta) → 3 (GA-Ready) → 4 (Listed)
