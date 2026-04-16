# Tax Guru Fine-Tuning — BIR Specialist

Fine-tunes `gpt-4o-mini` on Philippine BIR tax compliance data for the Tax Guru Pulser agent.

## Training data

`training_data.jsonl` — 10 examples covering:

| Topic | BIR forms/regs |
|---|---|
| EWT on professional fees (individual) | RR 11-2018 §2.57.2(A)(1), Form 2307 |
| EWT on commercial rental | RR 11-2018 §2.57.2(E), Form 2307 |
| BIR Form 2307 setup in Odoo | RR 2-1998, ipai_bir_2307 module |
| EWT on consulting (corporate) | RR 11-2018 §2.57.2(A)(6), ATC WC010 |
| 1601-EQ vs 1601-FQ distinction | NIRC §57-58, quarterly returns |
| Non-VAT freelancer withholding | RR 11-2018, Percentage Tax §116 |
| BIR Form 2316 employee cert | RR 11-2018 §2.79, NIRC §79 |
| VAT threshold + Odoo config | NIRC §106-108, TRAIN/CREATE MORE |
| Construction subcontractor EWT | RR 11-2018 §2.57.2(G), ATC WC010 |
| Monthly/quarterly/annual filing calendar | RMC 4-2023, all major BIR forms |

## How to run

```bash
# Prerequisites
pip install openai azure-identity
az login

# Full pipeline: upload + create fine-tune job
python scripts/finetune/run_finetune_tax_guru.py

# Check job status
python scripts/finetune/run_finetune_tax_guru.py --status <job-id>

# Deploy the fine-tuned model
python scripts/finetune/run_finetune_tax_guru.py --deploy <fine-tuned-model-id>
```

## Expanding training data

Add more examples to `training_data.jsonl` in OpenAI chat format:

```json
{"messages":[
  {"role":"system","content":"You are Tax Guru..."},
  {"role":"user","content":"<question>"},
  {"role":"assistant","content":"<grounded answer with BIR citation + Odoo mapping>"}
]}
```

Minimum recommended: 50-100 examples for meaningful fine-tuning improvement.
Current: 10 examples (starter set — validates pipeline; expand before production use).

## Target quality

After fine-tuning, Tax Guru should:
- Cite specific BIR RR/RMC numbers without prompting
- Know all ATC codes for common transaction types
- Map every tax scenario to Odoo `account.tax` + `account.move` fields
- Compute withholding amounts correctly with PHP formatting
- Distinguish individual vs corporate payee rates automatically

## Doctrine

- Fine-tuning runs on `ipai-copilot-resource` (Foundry), NOT Azure ML
- Auth: `DefaultAzureCredential` (Managed Identity first)
- Base model: `gpt-4o-mini` (cheapest fine-tunable model with sufficient capability)
- Deployment: Standard SKU, capacity 10
- Per `feedback_stick_to_gpt41`: gpt-4.1 remains the primary Pulser engine; fine-tuned gpt-4o-mini is a **specialist supplement**, not a replacement
