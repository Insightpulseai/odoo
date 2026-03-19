# Benchmark: Hugging Face Smol Training Playbook

> Source: HuggingFaceTB org, Smol Training Playbook Space
>
> Role: Benchmark doctrine for training small/open models well
>
> This is a benchmark anchor, NOT a runtime framework. Actual skill contracts are pinned to HF's concrete docs for Transformers, Accelerate, and TRL.

---

## Canonical Fit

```
Smol Training Playbook = benchmark doctrine for training small/open models well
Transformers           = core training workflow surface
Accelerate             = distributed training surface
TRL                    = post-training / alignment surface
Your repo              = bounded skills + eval gates + promotion rules
```

---

## Training Workflow Stages

### 1. Data Curation

- Corpus selection and quality filtering
- Deduplication and cleaning
- Domain/task fit assessment
- Train/validation/test split design
- **Surface**: HuggingFaceTB datasets, Datasets library

### 2. Pretraining / Continued Pretraining

- Full pretraining: training from scratch on large corpus
- Continued pretraining: extending a pretrained model on new domain data
- Architecture and training arguments selection
- Checkpoint and loss tracking
- **Surface**: Transformers Trainer

### 3. Fine-Tuning

- Domain adaptation on task-specific data
- Instruction tuning for chat/assistant behavior
- Supervised downstream task tuning
- Requires far less compute/data/time than pretraining
- **Surface**: Transformers Trainer, fine-tuning guide

### 4. Distributed Training

- Multi-GPU / multi-node strategy
- Parallelism: data, tensor, pipeline, model
- Memory optimization: gradient checkpointing, mixed precision, CPU offloading
- Speed/cost tradeoff decisions
- **Surface**: Accelerate

### 5. Post-Training / Alignment

#### Supervised Fine-Tuning (SFT)
- Chat/instruction data formatting
- Truncation, packing, max sequence decisions
- Base aligned checkpoint creation
- **Surface**: TRL SFTTrainer

#### Preference Optimization
- DPO: preference dataset (chosen/rejected pairs)
- GRPO: online RL from generated data
- Post-SFT refinement
- **Surface**: TRL DPO Trainer, GRPO Trainer

### 6. Training Eval / Readiness

- Checkpoint quality assessment
- Data quality verification
- Eval completeness check
- Infrastructure reproducibility
- Promotion gate: experiment → shared → internal → production

---

## Key Principles from HuggingFaceTB

1. **Dataset quality is the highest-leverage factor** — curate before you train
2. **Small models trained well outperform large models trained poorly** — the "smol" thesis
3. **Training is a pipeline, not a single step** — data → pretrain → fine-tune → align → eval → promote
4. **Reproducibility is non-negotiable** — configs, seeds, data versions must be tracked
5. **Evaluation drives promotion** — no checkpoint advances without eval evidence

---

## Important Rule

The Smol Training Playbook Space is the **benchmark anchor**. The actual skill contracts are pinned to Hugging Face's concrete docs:
- Transformers: https://huggingface.co/docs/transformers/
- Accelerate: https://huggingface.co/docs/transformers/accelerate
- TRL: https://huggingface.co/docs/trl/

This keeps doctrine grounded in maintained, versioned documentation.

---

## Sources

- [HuggingFaceTB org](https://huggingface.co/HuggingFaceTB)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
- [Transformers Trainer](https://huggingface.co/docs/transformers/trainer)
- [Fine-tuning guide](https://huggingface.co/docs/transformers/training)
- [Accelerate](https://huggingface.co/docs/transformers/accelerate)
- [TRL SFTTrainer](https://huggingface.co/docs/trl/sft_trainer)
- [TRL DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer)
