"""
agents/workflows/payment_reconcile_workflow.py

Pulser Account Reconciliation Workflow  (SC-PH-27)
D365 benchmark: Account Reconciliation Agent
Scope: Bank statement lines ↔ account.move.line matching
       Intercompany: Dataverse ↔ TBWA\SMP WHT clearing

HandoffWorkflow chosen because:
- Can span multiple sessions (bank data arrives daily)
- Durable checkpointing via FileCheckpointStorage
- Multiple specialist agents hand off to each other based on match status

Human-in-the-loop: Required before clearing any unmatched item older than 30 days

Usage:
    workflow = build_reconcile_workflow("dataverse_pasig", "2026-04")
    # Resumes from checkpoint when new bank data arrives
"""
import os
from typing import Annotated

from agent_framework import Agent, FileCheckpointStorage, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework.workflows import HandoffBuilder
from azure.identity import ManagedIdentityCredential, ChainedTokenCredential
from pydantic import Field

credential = ChainedTokenCredential(
    ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]),
)

client = FoundryChatClient(
    project_endpoint=os.environ["IPAI_FOUNDRY_ENDPOINT"],
    model="claude-sonnet-4-6",
    credential=credential,
)

# ---------------------------------------------------------------------------
# Read-only tools
# ---------------------------------------------------------------------------
@tool
def get_bank_statement_lines(company_id: str, period: str) -> str:
    """Fetch unreconciled bank statement lines for the period."""
    ...

@tool
def get_open_ar_lines(company_id: str, partner_id: str = None) -> str:
    """Fetch open AR lines (outstanding customer invoices)."""
    ...

@tool
def get_open_ap_lines(company_id: str, partner_id: str = None) -> str:
    """Fetch open AP lines (outstanding vendor bills)."""
    ...

@tool
def get_intercompany_transactions(
    source_company: str, target_company: str, period: str
) -> str:
    """
    Get intercompany transactions between two Odoo companies.
    Primary use: Dataverse ↔ TBWA\SMP WHT clearing (Invoice No. 0001, ₱1,734.69).
    """
    ...

@tool
def match_bank_line_to_move(
    bank_line_id: Annotated[int, Field(description="account.bank.statement.line ID")],
    move_line_id: Annotated[int, Field(description="account.move.line ID to match")],
) -> str:
    """
    Propose a match between a bank line and a move line.
    Does NOT post — returns match confidence score and amount delta for review.
    """
    ...

# ---------------------------------------------------------------------------
# Write tools — REQUIRE approval
# ---------------------------------------------------------------------------
@tool(approval_mode="always_require")
def reconcile_bank_line(
    bank_line_id: Annotated[int, Field(description="account.bank.statement.line ID")],
    move_line_id: Annotated[int, Field(description="account.move.line ID")],
    writeoff_amount: Annotated[float, Field(description="Writeoff amount if delta exists")] = 0.0,
    writeoff_account: Annotated[str, Field(description="Account code for writeoff")] = None,
) -> str:
    """
    Mark a bank line as reconciled against an account.move.line.
    Requires human approval if writeoff_amount > 0.
    """
    ...

@tool(approval_mode="always_require")
def clear_intercompany_transaction(
    source_company: Annotated[str, Field(description="Source company xmlid")],
    target_company: Annotated[str, Field(description="Target company xmlid")],
    invoice_id: Annotated[int, Field(description="Odoo invoice ID")],
    wht_amount: Annotated[float, Field(description="WHT amount to clear")],
) -> str:
    """
    Clear an intercompany WHT transaction.
    Example: TBWA\SMP Form 2307 ₱1,734.69 clearing for Invoice No. 0001.
    Always requires approval — intercompany postings affect two companies simultaneously.
    """
    ...

# ---------------------------------------------------------------------------
# Specialist agents
# ---------------------------------------------------------------------------
SYSTEM_BASE = """
You are Pulser, IPAI's reconciliation specialist agent.
Never post or clear without explicit approval.
Always show: amounts, dates, Odoo record IDs, and confidence score before requesting approval.
"""

bank_matcher_agent = Agent(
    client=client,
    name="BankMatcher",
    instructions=SYSTEM_BASE + """
    Match bank statement lines to account.move.line entries.
    For each bank line:
    1. Find the best matching move line (amount ± 1%, same period)
    2. Show the match proposal with confidence score
    3. Hand off to BankClearer for high-confidence matches (≥95%)
    4. Hand off to ExceptionHandler for low-confidence matches or unmatched lines
    """,
    tools=[get_bank_statement_lines, get_open_ar_lines, get_open_ap_lines, match_bank_line_to_move],
)

bank_clearer_agent = Agent(
    client=client,
    name="BankClearer",
    instructions=SYSTEM_BASE + """
    You receive high-confidence match proposals from BankMatcher.
    For each proposal:
    - Summarize: bank line date, amount, partner, proposed move line, delta
    - Request approval via reconcile_bank_line tool
    - If approved: confirm reconciliation
    - If delta > 0: propose writeoff account and amount, get approval
    """,
    tools=[reconcile_bank_line],
)

intercompany_agent = Agent(
    client=client,
    name="IntercompanyClearer",
    instructions=SYSTEM_BASE + """
    Handle intercompany transaction clearing between Odoo companies.
    Primary scenario: Dataverse IT Consultancy (Pasig) ↔ TBWA\SMP
    - Invoice No. 0001: ₱86,734.69 invoice, ₱1,734.69 WHT (Form 2307)
    - Confirm Form 2307 has been received before clearing
    - Present full clearing detail before requesting approval
    """,
    tools=[get_intercompany_transactions, clear_intercompany_transaction],
)

exception_handler_agent = Agent(
    client=client,
    name="ReconciliationExceptionHandler",
    instructions=SYSTEM_BASE + """
    Handle low-confidence matches and unmatched lines.
    For each unmatched item:
    - Flag if older than 30 days (escalate to Finance Director)
    - Suggest: is this a duplicate payment? Missing invoice? Bank error?
    - Do NOT clear — surface for human decision
    Produce an exceptions report at the end.
    """,
    tools=[get_bank_statement_lines, get_open_ar_lines, get_open_ap_lines],
)

# ---------------------------------------------------------------------------
# Workflow — HandoffBuilder (durable, multi-session)
# ---------------------------------------------------------------------------
checkpoint_storage = FileCheckpointStorage(
    storage_path=os.environ.get("PULSER_CHECKPOINT_PATH", "/var/lib/pulser/checkpoints")
)

def build_reconcile_workflow(company_id: str, period: str):
    """
    Build the payment reconciliation workflow.

    Flow:
        BankMatcher → BankClearer (high confidence)
        BankMatcher → ExceptionHandler (low confidence / unmatched)
        IntercompanyClearer (runs in parallel or as separate handoff)

    The workflow is durable — if new bank data arrives, resume from checkpoint.
    """
    workflow = (
        HandoffBuilder(
            name=f"reconcile_{company_id}_{period}",
            participants=[
                bank_matcher_agent,
                bank_clearer_agent,
                intercompany_agent,
                exception_handler_agent,
            ],
            checkpoint_storage=checkpoint_storage,
        )
        .with_start_agent(bank_matcher_agent)
        .build()
    )
    return workflow
