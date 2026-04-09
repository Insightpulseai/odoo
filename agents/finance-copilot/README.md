# Finance Copilot Agent

First Foundry agent proving the AI plane split: **Databricks = data**, **Foundry = agents**.

Queries Databricks gold marts (`gold.project_profitability`, `gold.portfolio_financial_health`) via SQL Statement API and answers finance questions using Azure OpenAI function calling.

## Run locally

```bash
cp .env.example .env
# Fill in DATABRICKS_TOKEN and AZURE_OPENAI_API_KEY

pip install -e ".[dev]"
python agent.py
```

## Run via DevUI

```bash
pip install agent-framework-devui
agent-devui serve --config devui_config.yaml
# Open http://localhost:8765
```

## Run tests

```bash
pytest tests/ -v
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DATABRICKS_HOST` | Databricks workspace URL |
| `DATABRICKS_HTTP_PATH` | SQL warehouse HTTP path |
| `DATABRICKS_TOKEN` | Databricks PAT or AAD token |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name (default: `gpt-4o`) |

## Architecture

```
User -> FinanceCopilotAgent -> Azure OpenAI (function calling)
                                    |
                            tool dispatch
                                    |
                          Databricks SQL API -> gold marts
```
