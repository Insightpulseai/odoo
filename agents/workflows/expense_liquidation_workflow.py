"""
agents/workflows/expense_liquidation_workflow.py

Pulser Time and Expense / Cash Advance Liquidation Workflow  (SC-PH-07/08/09)
D365 benchmark: Time and Expense Agent
Scope:
  SC-PH-07: Expense readiness check (missing timesheet/expense capture)
  SC-PH-08: Cash advance control (advance vs liquidation balance)
  SC-PH-09: Cash advance liquidation (expense submission and posting)

Sequential workflow — one agent per control point, human approval at posting.
"""
import os
from typing import Annotated

from agent_framework import Agent, FileCheckpointStorage, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework.workflows import SequentialBuilder
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
# Read-only tools (SC-PH-07: Expense Readiness)
# ---------------------------------------------------------------------------
@tool
def get_missing_timesheets(company_id: str, week_ending: str) -> str:
    """
    List employees with zero timesheet hours for the given week.
    Source: hr.timesheet where employee_id not in (SELECT employee_id FROM 
    account_analytic_line WHERE date BETWEEN week_start AND week_ending)
    """
    ...

@tool
def get_unsubmitted_expenses(company_id: str, employee_id: int = None) -> str:
    """
    List expense reports in draft state older than 3 days.
    Source: hr.expense.sheet where state='draft' and date < NOW() - INTERVAL 3 days
    """
    ...

@tool
def get_cash_advance_balance(
    company_id: str,
    employee_id: Annotated[int, Field(description="hr.employee ID")]
) -> str:
    """
    Get outstanding cash advance balance for an employee.
    Returns: total advance issued, total liquidated, outstanding balance.
    Source: account.move filtered by cash advance journal + employee analytic tag.
    """
    ...

@tool
def get_overdue_liquidations(company_id: str, days_overdue: int = 30) -> str:
    """
    List cash advances not liquidated within the policy period (default 30 days).
    Returns: employee, advance date, amount, days outstanding.
    """
    ...

@tool
def get_expense_readiness_summary(company_id: str, period: str) -> str:
    """
    Comprehensive expense readiness report for the period:
    - % of timesheets submitted vs expected
    - Unsubmitted expense reports with amounts
    - Cash advance outstanding balances
    - Days to expense report deadline
    """
    ...

# ---------------------------------------------------------------------------
# Write tools — REQUIRE approval (SC-PH-09: Liquidation posting)
# ---------------------------------------------------------------------------
@tool(approval_mode="always_require")
def post_expense_report(
    expense_sheet_id: Annotated[int, Field(description="hr.expense.sheet ID to post")],
    analytic_account_id: Annotated[int, Field(description="Analytic account for cost allocation")],
) -> str:
    """
    Post an approved expense report to the Odoo journal.
    Requires Finance Supervisor (BOM) approval.
    This debits the expense account and credits the employee payable/advance account.
    """
    ...

@tool(approval_mode="always_require")
def liquidate_cash_advance(
    employee_id: Annotated[int, Field(description="hr.employee ID")],
    advance_move_id: Annotated[int, Field(description="Original cash advance account.move ID")],
    expense_sheet_id: Annotated[int, Field(description="Liquidating expense report ID")],
    liquidation_amount: Annotated[float, Field(description="Amount being liquidated in PHP")],
    remaining_advance: Annotated[float, Field(description="Remaining advance to return (0 if fully liquidated)")],
) -> str:
    """
    Liquidate a cash advance against a submitted expense report.
    If remaining_advance > 0: employee must return cash to treasury.
    If liquidation_amount > advance: excess becomes a reimbursable claim.
    Requires Finance Supervisor (BOM) approval.
    """
    ...

@tool(approval_mode="always_require")
def flag_overdue_advance(
    employee_id: Annotated[int, Field(description="hr.employee ID")],
    advance_move_id: Annotated[int, Field(description="account.move ID for the advance")],
    days_overdue: Annotated[int, Field(description="Days past liquidation deadline")],
    action: Annotated[str, Field(description="'withhold_salary' | 'send_notice' | 'escalate_to_ckvc'")] = "send_notice",
) -> str:
    """
    Flag an overdue cash advance and initiate the policy action.
    Requires Finance Director (CKVC) approval for salary withholding actions.
    """
    ...

# ---------------------------------------------------------------------------
# Specialist agents — one per SC control point
# ---------------------------------------------------------------------------
SYSTEM_BASE = """
You are Pulser, IPAI's expense and cash advance control agent.
You serve TBWA\SMP Finance team (BOM=Finance Supervisor, CKVC=Finance Director).
Never post expenses or liquidations without explicit approval.
Always cite: employee name/code, amount in PHP, expense report ID, advance date.
"""

sc_ph_07_agent = Agent(
    client=client,
    name="ExpenseReadinessChecker",
    instructions=SYSTEM_BASE + """
    SC-PH-07: Expense Readiness Control
    Check:
    1. All team members have submitted timesheets for the week
    2. No unsubmitted expense reports older than 3 days
    3. Cash advance balances are within policy limits
    Produce: Expense Readiness Report with traffic-light status (Green/Amber/Red)
    - Green: all submitted, no outstanding advances
    - Amber: 1-3 missing timesheets OR advances 15-30 days outstanding
    - Red: >3 missing OR advances >30 days outstanding
    """,
    tools=[get_missing_timesheets, get_unsubmitted_expenses, get_cash_advance_balance, get_expense_readiness_summary],
)

sc_ph_08_agent = Agent(
    client=client,
    name="CashAdvanceController",
    instructions=SYSTEM_BASE + """
    SC-PH-08: Cash Advance Control
    For each outstanding advance:
    1. Calculate days outstanding
    2. Flag if >30 days without liquidation
    3. Check if expense report has been submitted as liquidation
    4. If overdue: propose action (send_notice → escalate_to_ckvc → withhold_salary)
    Escalation requires CKVC approval. Notices can be sent without approval.
    """,
    tools=[get_cash_advance_balance, get_overdue_liquidations, flag_overdue_advance],
)

sc_ph_09_agent = Agent(
    client=client,
    name="LiquidationProcessor",
    instructions=SYSTEM_BASE + """
    SC-PH-09: Cash Advance Liquidation
    For each expense report submitted as liquidation:
    1. Match to the original cash advance (amount, employee, date)
    2. Compute: advance amount, liquidation amount, balance (return or reimburse)
    3. Present full detail before requesting approval:
       - Employee: [code] [name]
       - Advance date: [date], Amount: ₱[amount]
       - Expense report ID: [id], Description: [desc]
       - Liquidation amount: ₱[amount]
       - Balance: ₱[return] to return / ₱[reimburse] to reimburse
    4. After approval: post expense + liquidate advance
    """,
    tools=[post_expense_report, liquidate_cash_advance, get_cash_advance_balance],
)

# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------
checkpoint_storage = FileCheckpointStorage(
    storage_path=os.environ.get("PULSER_CHECKPOINT_PATH", "/var/lib/pulser/checkpoints")
)

def build_expense_workflow(company_id: str, period: str):
    """
    Build the expense and cash advance liquidation workflow.

    Flow: ExpenseReadinessChecker → CashAdvanceController → LiquidationProcessor

    Human-in-the-loop: LiquidationProcessor requires BOM/CKVC approval for all
    posting operations. CashAdvanceController requires CKVC for salary withholding.

    Args:
        company_id: "tbwa_smp" | "dataverse_pasig" | "prismalab" | "w9studio"
        period: "2026-04"
    """
    workflow = (
        SequentialBuilder(
            participants=[
                sc_ph_07_agent,
                sc_ph_08_agent,
                sc_ph_09_agent,
            ],
            checkpoint_storage=checkpoint_storage,
        )
        .with_request_info(agents=["CashAdvanceController", "LiquidationProcessor"])
        .build()
    )
    return workflow
