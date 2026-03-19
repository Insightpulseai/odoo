# Agent Bricks: Feedback Intelligence

Agent Bricks module boundary for building and optimizing AI agent systems using Databricks data.

## Overview

This module provides the scaffolding for Agent Bricks-powered feedback intelligence agents that:
- Process user feedback data from the PPM system
- Build sentiment analysis and classification models
- Generate actionable insights for project management
- Integrate with the broader IPAI AI platform

## Structure

```
feedback_intel/
├── README.md           # This file
├── resources/          # DAB resource definitions
│   ├── agent_bricks_job.yml
│   └── eval_jobs.yml
└── src/
    ├── prompts/        # Prompt templates
    ├── evaluators/     # Agent evaluation logic
    └── pipelines/      # Data processing pipelines
```

## Agent Bricks Integration

Agent Bricks auto-builds and optimizes comprehensive agent systems. This module:

1. **Data Pipeline**: Feeds processed feedback data to Agent Bricks
2. **Prompt Management**: Version-controlled prompt templates
3. **Evaluation**: Automated eval jobs for agent quality
4. **Observability**: MLflow integration for tracking

## Usage

Deploy with the main bundle:
```bash
databricks bundle deploy --target dev
```

Run agent evaluation:
```bash
databricks bundle run --target dev agent_eval_job
```

## Related Docs

- [Agent Bricks Documentation](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/)
- [MLflow Agent Tracking](https://docs.databricks.com/aws/en/mlflow/)
