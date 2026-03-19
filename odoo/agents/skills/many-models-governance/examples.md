# many-models-governance — Examples

## Example 1: Multi-Domain Model Portfolio

**Input**: We have 12 ML models across sales, marketing, and operations domains. Some overlap in features. Monthly compute cost is $8,400. No formal inventory exists.

**Output**:

Inventory:
| Model | Domain | Owner | Last Retrained | Monthly Cost | Status |
|-------|--------|-------|----------------|--------------|--------|
| lead_scorer_v3 | sales | data-team | 2026-02-15 | $450 | active |
| churn_predictor_v2 | sales | data-team | 2026-01-20 | $600 | stale (>45 days) |
| campaign_response_v1 | marketing | analytics | 2026-03-01 | $350 | active |
| ... | ... | ... | ... | ... | ... |

Splitting strategy: Model-per-domain is justified (sales, marketing, operations have distinct feature spaces). Within sales, consolidate lead_scorer and opportunity_ranker (shared features, marginal accuracy difference of 0.3%).

Routing: Domain classifier based on request source system (CRM -> sales models, MAP -> marketing models, ERP -> operations models). Fallback to general-purpose model if domain model unavailable.

Cost governance: Tag all compute with domain label. Alert at $500/model/month. Quarterly review of cost-per-prediction.

Retirement: churn_predictor_v2 flagged for retraining or retirement (45+ days stale). Two legacy models identified for decommission (superseded by v2/v3 versions).

---

## Example 2: Multi-Tenant Model Strategy

**Input**: SaaS platform with 50 tenants. Currently one shared model. Top 5 tenants want personalized predictions. Data isolation is contractually required for 3 tenants.

**Output**:

Splitting strategy:
- 3 tenants with contractual isolation: model-per-tenant (mandatory)
- 2 additional high-value tenants: model-per-tenant (justified by 8% accuracy improvement in testing)
- Remaining 45 tenants: shared model with tenant feature encoding

Routing: Tenant ID lookup table maps to model endpoint. Shared model is default fallback.

Cost governance:
- Per-tenant models: $200/month each (training + serving)
- Shared model: $800/month total
- Total: $1,800/month vs. $800/month baseline
- Justification: isolation contracts require it; accuracy gains for top tenants deliver measurable revenue impact

Retirement: Per-tenant models retire if tenant churns or data volume drops below minimum threshold (1,000 training samples).
