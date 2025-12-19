# -*- coding: utf-8 -*-
"""Date utilities for business day calculations."""
from datetime import date, timedelta


def is_weekend(d: date) -> bool:
    """Check if date is a weekend (Saturday=5, Sunday=6)."""
    return d.weekday() >= 5


def subtract_business_days(d: date, business_days: int) -> date:
    """
    Subtract N business days (Mon-Fri) from date d.

    Args:
        d: The anchor date
        business_days: Number of business days to subtract

    Returns:
        Date that is business_days before d (skipping weekends)
    """
    if business_days <= 0:
        return d
    cur = d
    remaining = business_days
    while remaining > 0:
        cur = cur - timedelta(days=1)
        if not is_weekend(cur):
            remaining -= 1
    return cur


def add_business_days(d: date, business_days: int) -> date:
    """
    Add N business days (Mon-Fri) to date d.

    Args:
        d: The anchor date
        business_days: Number of business days to add

    Returns:
        Date that is business_days after d (skipping weekends)
    """
    if business_days <= 0:
        return d
    cur = d
    remaining = business_days
    while remaining > 0:
        cur = cur + timedelta(days=1)
        if not is_weekend(cur):
            remaining -= 1
    return cur
