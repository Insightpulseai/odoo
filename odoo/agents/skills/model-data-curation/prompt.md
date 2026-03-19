# Model Data Curation — Prompt

You are curating training data. Dataset quality is the single highest-leverage factor in model training outcomes.

## Process

### 1. Define Requirements
- What task/domain is the model being trained for?
- What format is needed (text, instruction pairs, preference pairs)?
- What quality thresholds apply?
- What size budget exists?

### 2. Source Selection
- Identify candidate data sources
- Evaluate each for: quality, domain fit, licensing, size
- Prefer curated sources over raw web scrapes

### 3. Filtering Pipeline
Apply in order:
1. **Deduplication**: exact and near-duplicate removal
2. **Language detection**: remove off-language content
3. **Quality filtering**: perplexity, length, formatting
4. **Toxicity filtering**: remove harmful content
5. **Domain filtering**: retain only domain-relevant content

### 4. Split Design
- Train: 80-90%
- Validation: 5-10% (strictly held out, never used for training decisions during run)
- Test: 5-10% (only used for final evaluation)
- Stratify by important attributes (domain, difficulty, format)

### 5. Quality Report
Document:
- Source statistics
- Filter pass rates
- Final dataset size and composition
- Data card with provenance and licensing

## Output
```
Dataset: [name]
Sources: [list with sizes]
Filters applied: [list with pass rates]
Final size: [train/val/test counts]
Quality score: [overall assessment]
Data card: [location]
```
