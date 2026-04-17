---
name: prisma2020-flow-diagram
domain: research
version: 1.0.0
license: MIT
language: R
description: PRISMA 2020-compliant flow diagrams via the PRISMA2020 R package (Haddaway et al., 2022). Interactive HTML + static PDF/PNG/SVG. Supports two-arm (new searches) and three-arm (Previous + Other methods) layouts.
triggers:
  - PRISMA
  - PRISMA 2020
  - flow diagram
  - flowchart systematic review
  - study selection diagram
  - PRISMA_flowdiagram
  - screening flowchart
  - records identified
  - records excluded
  - full-text assessed
sources:
  - https://github.com/prisma-flowdiagram/PRISMA2020
  - https://estech.shinyapps.io/prisma_flowdiagram/
citation: |
  Haddaway, N. R., Page, M. J., Pritchard, C. C., & McGuinness, L. A. (2022).
  PRISMA2020: An R package and Shiny app for producing PRISMA 2020-compliant flow diagrams.
  Campbell Systematic Reviews, 18, e1230. https://doi.org/10.1002/cl2.1230
---

# PRISMA 2020 Flow Diagram

## When to use

Invoke when the user asks for a PRISMA flow diagram, study-selection flowchart,
or screening flowchart for a systematic review / meta-analysis, or when the
companion skill `doing-meta-analysis-r` needs a reporting figure.

## Required R packages

```r
install.packages(c("PRISMA2020", "DiagrammeR", "DiagrammeRsvg", "rsvg"))
```

## Input contract (CSV)

Required columns (PRISMA 2020 two-arm layout):

```
previous_studies, previous_reports, register_results, database_results,
website_results, organisation_results, citation_results,
duplicates_removed, excluded_automation, excluded_other,
records_screened, records_excluded,
reports_sought_retrieval, reports_not_retrieved,
reports_assessed, reports_excluded_reason1, reports_excluded_reason2, reports_excluded_reason3,
new_studies, new_reports, total_studies, total_reports
```

Three-arm (Previous + New + Other methods) adds the `other_*` column family.

## Canonical pipeline

```r
library(PRISMA2020)
data <- read.csv("prisma_counts.csv")
plot <- PRISMA_flowdiagram(
  data,
  interactive = FALSE,
  previous    = TRUE,
  other       = FALSE,
  fontsize    = 12,
  font        = "Helvetica",
  title       = NA
)
PRISMA_save(plot, filename = "prisma_flow.pdf", filetype = "PDF")
```

## IPAI integration

- **Primary use case**: PrismaLab R&D systematic reviews, JBLMGH Neurology
  submissions — CAVE score PSE, toxoplasmosis, HIV-TB co-infection manuscripts.
- **Artifact storage**: register counts in `ops.artifacts` with `type='prisma_counts'`;
  upload PDF to Azure Blob `stipaidevlake/research/<study_id>/figures/prisma_flow.pdf`.
- **Companion skills**: `doing-meta-analysis-r` (pooling + diagnostics),
  `meta-analysis-pipeline` (orchestration).

## Safety

- Never fabricate counts. Require an explicit CSV from the user or from
  upstream search-results extraction.
- Row totals must reconcile (identified = screened + duplicates_removed).
  Flag mismatches — do not silently correct.
