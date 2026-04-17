---
name: doing-meta-analysis-r
domain: research
version: 1.0.0
license: CC0-1.0
language: R
description: R-native meta-analysis via Harrer et al. (2021) — effect sizes, pooling, forest/funnel plots, heterogeneity, subgroup, meta-regression, publication bias (Egger, trim-and-fill, PET-PEESE, p-curve), NMA, Bayesian MA, SEM-MA, RoB plots, power analysis.
triggers:
  - meta-analysis
  - forest plot
  - heterogeneity
  - I-squared
  - tau-squared
  - Egger
  - trim and fill
  - meta-regression
  - network meta-analysis
  - Harrer
  - dmetar
  - metafor
  - systematic review pooling
  - effect size pooling
sources:
  - https://github.com/MathiasHarrer/Doing-Meta-Analysis-in-R
  - https://bookdown.org/MathiasHarrer/Doing_Meta_Analysis_in_R/
citation: |
  Harrer, M., Cuijpers, P., Furukawa, T.A., & Ebert, D.D. (2021).
  Doing Meta-Analysis with R: A Hands-On Guide.
  Chapman & Hall/CRC Press. ISBN 978-0-367-61007-4.
---

# Doing Meta-Analysis in R

Canonical reference: Harrer et al. (2021) *Doing Meta-Analysis with R: A Hands-On Guide*.

## When to use

Invoke when the user asks for any of: effect-size pooling, forest/funnel plots,
heterogeneity diagnostics, subgroup / meta-regression, publication-bias
assessment (Egger, trim-and-fill, PET-PEESE, p-curve), network meta-analysis,
Bayesian meta-analysis, SEM-MA, RoB plots, or power analysis.

## Required R packages

```r
install.packages(c("meta", "metafor", "netmeta", "brms"))
# dmetar is a companion package — bundled with the Harrer book
remotes::install_github("MathiasHarrer/dmetar")
```

## Canonical pipeline

1. **Import** — `esc` / `metafor::escalc()` to compute effect sizes (SMD, OR, HR, RR).
2. **Pool** — `meta::metagen()` (generic IV), `metabin()`, `metacont()`, `metacor()`.
   Default: REML random-effects; report τ², I², prediction interval.
3. **Visualize** — `meta::forest()`, `funnel()`; save to PDF/PNG at 300 DPI.
4. **Diagnose** — subgroup via `update.meta(subgroup=)`, meta-regression via `metafor::rma()`.
5. **Publication bias** — `metabias()` (Egger), `trimfill()`, PET-PEESE (`metafor`),
   p-curve (`dmetar::pcurve()`).
6. **NMA (optional)** — `netmeta::netmeta()`, SUCRA via `netrank()`.
7. **Bayesian (optional)** — `brms::brm(bf(yi | se(sei) ~ 1 + (1|study)))`.
8. **Report** — PRISMA 2020 flow diagram via companion skill `prisma2020-flow-diagram`.

## IPAI integration

- **Primary use case**: PrismaLab R&D systematic reviews (BIR entity -00002),
  JBLMGH Neurology manuscripts (CAVE score PSE, toxoplasmosis, HIV-TB co-infection).
- **Artifact storage**: write final RData + figures to Azure Blob Storage
  (`stipaidevlake/research/<study_id>/`) and register metadata in `ops.artifacts`.
- **Companion skills**: `meta-analysis-pipeline` (orchestration), `prisma2020-flow-diagram` (reporting).

## Safety

- Never invent effect sizes — require a study-level CSV with fields:
  `study_id, n1, n2, mean1, mean2, sd1, sd2` (continuous) or
  `study_id, events1, n1, events2, n2` (binary).
- Flag I² > 75% in output and recommend subgroup / meta-regression.
- Never suppress studies from pooling without an explicit, logged reason.
