# Model Data Curation — Examples

## Example 1: Instruction-Tuning Dataset

```
Task: Fine-tune for Odoo assistant
Sources: Odoo documentation (200K pages), community forum Q&A (50K pairs)
Filters:
  - Dedup: 12% removed
  - Language: 3% non-English removed
  - Quality: 8% low-quality removed (too short, formatting issues)
  - Domain: 5% off-topic removed
Final size: 180K train / 10K val / 10K test
Quality: High — curated from official docs
```

## Example 2: Pretraining Corpus

```
Task: Continue pretraining for finance domain
Sources: Financial news (10M articles), SEC filings (2M), financial textbooks (500K pages)
Filters:
  - Dedup: 25% removed (news repeats)
  - Quality: 15% removed (boilerplate, ads)
  - Domain: 2% off-topic removed
Final size: 8M train / 400K val / 200K test
Quality: Medium-high — web sources require aggressive filtering
```
