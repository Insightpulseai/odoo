from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class StatementLine(BaseModel):
    date: str  # YYYY-MM-DD
    amount: float
    direction: Literal["debit", "credit"]
    reference: Optional[str] = None
    memo: Optional[str] = None
    counterparty: Optional[str] = None


class BankStatementExtraction(BaseModel):
    statement_name: str
    currency: str = "PHP"
    date_from: str
    date_to: str
    opening_balance: float = 0.0
    closing_balance: float = 0.0
    journal_id: int = Field(..., description="Target Odoo bank journal id")
    lines: List[StatementLine]
    confidence: float = 0.0
