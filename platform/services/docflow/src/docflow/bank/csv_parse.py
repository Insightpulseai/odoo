import csv
from .schema import BankStatementExtraction, StatementLine


def parse_bank_csv(path: str, *, journal_id: int, currency: str = "PHP") -> BankStatementExtraction:
    # TODO: adapt column mapping per bank format
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amt = float(row["amount"])
            direction = "credit" if amt > 0 else "debit"
            lines.append(
                StatementLine(
                    date=row["date"],
                    amount=abs(amt),
                    direction=direction,
                    reference=row.get("reference"),
                    memo=row.get("memo"),
                    counterparty=row.get("counterparty"),
                )
            )
    # minimal header inference
    dates = sorted([l.date for l in lines]) if lines else ["1970-01-01"]
    return BankStatementExtraction(
        statement_name=f"CSV Statement {path}",
        currency=currency,
        date_from=dates[0],
        date_to=dates[-1],
        opening_balance=0.0,
        closing_balance=0.0,
        journal_id=journal_id,
        lines=lines,
        confidence=1.0,
    )
