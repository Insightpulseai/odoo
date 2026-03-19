# Training Readiness Judge — Examples

## Example 1: Promoting a Well-Evaluated Checkpoint

```
Checkpoint: SmolLM2-1.7B-SFT-v2
Target level: internal

Data quality:      PASS
  - Data card: present, 100K instruction pairs from curated sources
  - Dedup: applied (12% removed)
  - Filtering: quality + toxicity + domain (documented)
  - Splits: 90K train / 5K val / 5K test (val strictly held out)

Eval completeness: PASS
  - MMLU: 48.3 (base: 45.2, +3.1)
  - HellaSwag: 62.1 (base: 60.5, +1.6)
  - Instruction following (GPT-4 judge): 4.2/5.0 (base: 2.1/5.0)
  - Safety (GPT-4 judge): 4.7/5.0
  - All required benchmarks present

Training health:   PASS
  - Loss: converged from 2.8 to 1.4, stable last 20% of training
  - No divergence events
  - Gradient norm: stable 0.5-1.2 throughout
  - LR schedule: cosine with warmup, executed correctly

Reproducibility:   PASS
  - Config: full TrainingArguments saved to config.json
  - Seed: 42
  - Data version: dataset-v2-hash-abc123
  - Software: transformers 4.46.0, torch 2.5.0, trl 0.12.0
  - Hardware: 4x A100 80GB

Decision: PROMOTE to internal
Justification: All four gates pass. Meaningful improvement over base model on
instruction following (+2.1 points) with no regression on general benchmarks.
Training was healthy and fully reproducible.
```

## Example 2: Rejecting an Under-Evaluated Checkpoint

```
Checkpoint: SmolLM2-1.7B-DPO-v1
Target level: internal

Data quality:      FAIL
  - Data card: MISSING
  - Dedup: unknown
  - Filtering: unknown
  - Splits: training data described as "15K preference pairs" with no further detail

Eval completeness: INCOMPLETE
  - MMLU: not run
  - HellaSwag: not run
  - Win rate vs SFT: 58% (on 50 examples — too small a sample)
  - General benchmarks: not run

Training health:   PASS
  - Loss: converged normally
  - No divergence
  - Gradient norms: stable

Reproducibility:   FAIL
  - Config: partial (missing beta value, lr)
  - Seed: not documented
  - Data version: not documented
  - Software: "latest" (no specific versions)

Decision: REJECT
Justification: Missing data card (hard reject on data quality gate). Config
incomplete and no seed documented (hard reject on reproducibility). Even if
those were fixed, eval coverage is insufficient — only 50 examples for win
rate, no general benchmarks.

Gaps:
- Create data card with provenance, filtering evidence, and licensing
- Run MMLU and HellaSwag benchmarks
- Increase win rate sample to 200+ examples
- Document full config including beta, lr, and all hyperparameters
- Record seed and data version hash
- Pin software versions (no "latest")
```
