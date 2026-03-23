#!/usr/bin/env python3
"""
generate_2026_month_end_calendar.py

Generates a full 2026 schedule for the TBWA Month-End Close Tasks.
Based on the phases from tasks_month_end.csv and applying business day offsets
relative to the end of each month in 2026.
"""

import csv
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import List

TASKS_CSV = Path("../../supabase/data/seed/finance_ppm/tbwa_smp/tasks_month_end.csv")
HOLIDAYS_CSV = Path("ph_holidays_2026.csv")

OUT_CALENDAR_CSV = Path("month_end_calendar_2026.csv")
OUT_EVENTS_JSON = Path("month_end_events_2026.json")

# Approximate offsets (business days) relative to the end of the month
# Negative = N business days before month end
# Positive = N business days after month end
PHASE_OFFSETS = {
    "Phase I": -5,   # ~24th of the month
    "Phase II": -3,
    "Phase III": -1,
    "Phase IV": 1,   # First business day of new month
    "Phase V": 3,    # Third business day of new month
}

@dataclass
class Holiday:
    day: date
    name: str

def load_holidays(path: Path) -> List[Holiday]:
    holidays = []
    if not path.exists():
        return holidays
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            y, m, d = map(int, row["date"].split("-"))
            holidays.append(Holiday(date(y, m, d), row.get("name", "")))
    return holidays

def is_business_day(d: date, holidays: List[Holiday]) -> bool:
    if d.weekday() >= 5:  # 5=Sat, 6=Sun
        return False
    return all(h.day != d for h in holidays)

def get_business_day(reference_date: date, offset: int, holidays: List[Holiday]) -> date:
    cur = reference_date
    if offset < 0:
        remaining = abs(offset)
        while remaining > 0:
            if is_business_day(cur, holidays):
                remaining -= 1
            if remaining > 0:
                cur -= timedelta(days=1)
    elif offset > 0:
        remaining = offset
        # Always move into the next month first
        cur += timedelta(days=1)
        while remaining > 0:
            if is_business_day(cur, holidays):
                remaining -= 1
                if remaining == 0:
                    break
            cur += timedelta(days=1)
    else:
        while not is_business_day(cur, holidays):
            cur -= timedelta(days=1)
    return cur

def get_last_day_of_month(year: int, month: int) -> date:
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)

def build_month_end_calendar(holidays: List[Holiday]):
    tasks_template = []
    # Load task template
    with TASKS_CSV.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse phase from description (e.g. "Phase I: Initial & Compliance")
            desc_lines = row["description"].split("\n")
            phase_str = desc_lines[0].split(":")[0].strip()
            tasks_template.append({
                "id": row["id"],
                "name": row["name"],
                "phase": phase_str,
                "description": row["description"]
            })

    generated_tasks = []
    for month in range(1, 13):
        last_day = get_last_day_of_month(2026, month)
        period_label = f"{date(2026, month, 1).strftime('%b %Y')}"

        for t in tasks_template:
            offset = PHASE_OFFSETS.get(t["phase"], 0)
            planned_date = get_business_day(last_day, offset, holidays)
            
            generated_tasks.append({
                "period": period_label,
                "task_id": t["id"],
                "phase": t["phase"],
                "name": t["name"],
                "planned_date": planned_date.isoformat(),
                "description": t["description"]
            })
            
    return generated_tasks

def main():
    holidays = load_holidays(HOLIDAYS_CSV)
    tasks = build_month_end_calendar(holidays)

    # Write CSV
    with OUT_CALENDAR_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "task_id", "phase", "name", "planned_date", "description"])
        writer.writeheader()
        writer.writerows(tasks)

    # Write JSON
    events = []
    for t in tasks:
        events.append({
            "date": t["planned_date"],
            "value": 1,
            "label": f"{t['period']} Close - {t['name']}",
            "status": "open",
            "phase": t["phase"]
        })
        
    with OUT_EVENTS_JSON.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    print(f"Generated {len(tasks)} month-end tasks across 12 months for 2026.")

if __name__ == "__main__":
    main()
