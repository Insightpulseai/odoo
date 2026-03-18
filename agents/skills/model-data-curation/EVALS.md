# Model Data Curation — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Filter completeness | 25% | All required filters applied |
| Split quality | 20% | Proper stratification, held-out val |
| Domain fit | 20% | Data matches target task |
| Documentation | 20% | Data card complete |
| Quality assessment | 15% | Realistic quality evaluation |

## Test Cases

### TC-1: Basic curation
- Input: "Prepare dataset for code generation fine-tuning"
- Expected: Dedup, quality filter, code-specific filters, proper splits
- Fail if: Missing deduplication or no held-out validation set

### TC-2: Noisy source
- Input: "Web-scraped data with high noise"
- Expected: Aggressive filtering pipeline, realistic quality assessment
- Fail if: Accepts noisy data without filtering

## Pass threshold: All filters present, splits correct
