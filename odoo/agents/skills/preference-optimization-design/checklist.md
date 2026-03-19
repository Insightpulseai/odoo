# Preference Optimization Design — Checklist

- [ ] Method selected: DPO vs GRPO with justification
- [ ] SFT baseline checkpoint identified
- [ ] Preference data prepared in correct format
- [ ] Data quality verified (chosen/rejected labels accurate)
- [ ] Beta parameter set with justification
- [ ] Learning rate set (very low for DPO, typically 1e-7 to 5e-6)
- [ ] Loss type selected (sigmoid, hinge)
- [ ] Max length and max prompt length configured
- [ ] Reward hacking detection plan defined
- [ ] Win rate evaluation planned (vs SFT baseline)
- [ ] General benchmark regression check planned
- [ ] Response diversity monitoring configured
