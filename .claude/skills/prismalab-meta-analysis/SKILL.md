---
name: prismalab-meta-analysis
description: Perform meta-analyses using Azure Databricks for computation and Power BI for visualization. Supports fixed/random effects, subgroup analysis, and publication bias assessment.
---

# PrismaLab Meta-Analysis Skill

## When to Use
- User needs to compute pooled effect sizes
- User asks about heterogeneity assessment (I-squared, Q-statistic)
- User needs forest plots, funnel plots, or sensitivity analyses
- User asks about publication bias (Egger's test, trim-and-fill)

## Azure Services Used
- **Databricks** (`dbw-ipai-dev`): Python computation (statsmodels, scipy, meta-analysis libraries)
- **Power BI**: Publication-ready visualizations
- **Azure AI Foundry**: Interpretation and narrative synthesis

## Computation Approach

### Effect Size Calculation
```python
# Run in Databricks notebook
import numpy as np
from scipy import stats

def compute_effect_size(study_data, metric="SMD"):
    """
    Compute standardized mean difference (Cohen's d) or odds ratio.

    study_data: list of dicts with keys:
      SMD: n1, mean1, sd1, n2, mean2, sd2
      OR:  events1, total1, events2, total2
    """
    if metric == "SMD":
        d = (study_data["mean1"] - study_data["mean2"]) / pooled_sd
        se = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    elif metric == "OR":
        OR = (a * d) / (b * c)
        se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    return {"effect": d_or_OR, "se": se, "ci_lower": ..., "ci_upper": ...}
```

### Pooled Effect (Random Effects)
```python
def random_effects_meta(effects, variances):
    """DerSimonian-Laird random effects model."""
    weights_fixed = 1.0 / variances
    Q = np.sum(weights_fixed * (effects - weighted_mean_fixed)**2)
    tau2 = max(0, (Q - (k - 1)) / (sum_w - sum_w2 / sum_w))
    weights_random = 1.0 / (variances + tau2)
    pooled = np.sum(weights_random * effects) / np.sum(weights_random)
    se_pooled = np.sqrt(1.0 / np.sum(weights_random))
    I2 = max(0, (Q - (k - 1)) / Q * 100)
    return {"pooled_effect": pooled, "se": se_pooled, "I2": I2, "tau2": tau2, "Q": Q}
```

### Heterogeneity Interpretation
| I-squared | Interpretation |
|-----------|---------------|
| 0-25% | Low heterogeneity |
| 25-50% | Moderate heterogeneity |
| 50-75% | Substantial heterogeneity |
| 75-100% | Considerable heterogeneity |

## Visualization (Power BI or HTML/SVG)

### Forest Plot
Generate SVG forest plot with:
- Study labels with year
- Effect size point + CI whiskers
- Weight proportional to square size
- Diamond for pooled estimate
- Vertical line at null effect

### Funnel Plot
Generate for publication bias assessment:
- X-axis: effect size
- Y-axis: standard error (inverted)
- Pseudo-95% CI lines
- Egger's regression line if significant

## Subgroup and Sensitivity Analyses
- **Subgroup**: stratify by study characteristics (design, population, intervention type)
- **Leave-one-out**: recalculate excluding each study
- **Cumulative**: add studies chronologically
- **Influence**: Cook's distance equivalent for meta-analysis

## Quality Standards
- Report per PRISMA 2020 synthesis methods
- Use GRADE framework for certainty of evidence
- Report prediction intervals alongside confidence intervals
- Always assess publication bias for >=10 studies
- Declare statistical software and version
