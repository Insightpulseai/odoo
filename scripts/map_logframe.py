#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogFrame Mapper for Month-End Closing Tasks
Maps tasks to Logical Framework structure (Goal → Outcome → IM1/IM2 → Outputs → Activities)

LogFrame Structure:
  Goal: 100% compliant and timely month-end closing and tax filing
  Outcome: Streamlined coordination between Finance, Payroll, Tax, Treasury
  IM1 (Month-End Closing): Accurate books and reconciliations
  IM2 (Tax Filing Compliance): On-time BIR filing
  Outputs: JEs finalized, BIR forms filed, reports reviewed
  Activities: Specific month-end closing tasks

Usage:
    python3 scripts/map_logframe.py --input data/notion_tasks_deduplicated.json --output data/notion_tasks_with_logframe.json

Author: Jake Tolentino
Date: 2025-11-26
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any


class LogFrameMapper:
    """Maps month-end closing tasks to Logical Framework structure."""

    LOGFRAME = {
        'goal': {
            'id': 'G1',
            'name': '100% compliant and timely month-end closing and tax filing',
            'indicator': 'Zero penalties, 100% on-time filing rate'
        },
        'outcome': {
            'id': 'O1',
            'name': 'Streamlined coordination between Finance, Payroll, Tax, Treasury',
            'indicator': 'Month-end closing completed within 5 business days'
        },
        'immediate_objectives': {
            'IM1': {
                'id': 'IM1',
                'name': 'Month-End Closing - Accurate books and reconciliations',
                'indicator': 'All reconciliations completed within 3 days of month-end',
                'activities': [
                    'Bank & Cash reconciliation',
                    'GL account reconciliation',
                    'AR/AP aging reviews',
                    'Inventory valuation',
                    'Accruals & provisions',
                    'Revenue recognition',
                    'Depreciation & amortization',
                    'Reclassifications (OOP/WIP)',
                    'Working capital reporting'
                ]
            },
            'IM2': {
                'id': 'IM2',
                'name': 'Tax Filing Compliance - On-time BIR filing',
                'indicator': '100% BIR forms filed before deadline',
                'activities': [
                    'VAT compilation and reporting',
                    'Withholding tax (2307) compilation',
                    'Tax provision calculation',
                    'BIR form preparation',
                    'Final pay processing',
                    'Payroll tax compliance'
                ]
            }
        },
        'outputs': {
            'O1.1': {
                'id': 'O1.1',
                'name': 'All journal entries finalized and posted',
                'indicator': 'Zero pending JEs after Day 5'
            },
            'O1.2': {
                'id': 'O1.2',
                'name': 'All BIR tax forms filed on time',
                'indicator': '100% forms filed before BIR deadline'
            },
            'O1.3': {
                'id': 'O1.3',
                'name': 'Management reports reviewed and approved',
                'indicator': 'CFO approval within 7 days of month-end'
            }
        }
    }

    def __init__(self):
        pass

    def map_task_to_im(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a task to appropriate Immediate Objective (IM1 or IM2).

        Args:
            task: Task dictionary with title, category, wbs_phase

        Returns:
            Task dictionary enhanced with LogFrame mappings
        """
        category = task.get('category', 'General')
        title_lower = task['title'].lower()

        # IM2 (Tax Filing) triggers
        if any(kw in title_lower for kw in ['vat', 'tax', 'withholding', 'bir', '2307', 'payroll', 'final pay']):
            im = 'IM2'
            output = 'O1.2'  # BIR tax forms
            activity = self._categorize_im2_activity(title_lower)

        # IM1 (Month-End Closing) for everything else
        else:
            im = 'IM1'
            output = 'O1.1'  # Journal entries finalized
            activity = self._categorize_im1_activity(title_lower, category)

        # Add LogFrame metadata
        task['logframe'] = {
            'goal': 'G1',
            'outcome': 'O1',
            'immediate_objective': im,
            'im_name': self.LOGFRAME['immediate_objectives'][im]['name'],
            'output': output,
            'output_name': self.LOGFRAME['outputs'][output]['name'],
            'activity': activity,
            'kpi_indicator': self.LOGFRAME['immediate_objectives'][im]['indicator']
        }

        return task

    def _categorize_im1_activity(self, title_lower: str, category: str) -> str:
        """Categorize IM1 (Month-End Closing) activity type."""
        if 'bank' in title_lower or 'cash' in title_lower:
            return 'Bank & Cash reconciliation'
        elif 'reconciliation' in title_lower or 'recon' in title_lower:
            return 'GL account reconciliation'
        elif 'ar' in title_lower or 'receivable' in title_lower or 'ap' in title_lower or 'payable' in title_lower:
            return 'AR/AP aging reviews'
        elif 'inventory' in title_lower:
            return 'Inventory valuation'
        elif 'accrue' in title_lower or 'accrual' in title_lower or 'provision' in title_lower:
            return 'Accruals & provisions'
        elif 'revenue' in title_lower or 'billable' in title_lower:
            return 'Revenue recognition'
        elif 'depreciation' in title_lower or 'amortization' in title_lower:
            return 'Depreciation & amortization'
        elif 'reclassification' in title_lower or 'oop' in title_lower or 'wip' in title_lower:
            return 'Reclassifications (OOP/WIP)'
        elif 'report' in title_lower or 'working capital' in title_lower:
            return 'Working capital reporting'
        else:
            return 'GL account reconciliation'  # Default

    def _categorize_im2_activity(self, title_lower: str) -> str:
        """Categorize IM2 (Tax Filing) activity type."""
        if 'vat' in title_lower:
            return 'VAT compilation and reporting'
        elif 'withholding' in title_lower or '2307' in title_lower:
            return 'Withholding tax (2307) compilation'
        elif 'tax provision' in title_lower or 'ppb provision' in title_lower:
            return 'Tax provision calculation'
        elif 'bir' in title_lower:
            return 'BIR form preparation'
        elif 'final pay' in title_lower:
            return 'Final pay processing'
        elif 'payroll' in title_lower:
            return 'Payroll tax compliance'
        else:
            return 'Tax provision calculation'  # Default

    def assign_employee(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign employee code based on task category and LogFrame activity.

        Employee Codes (from Gemini context):
        - CKVC: Finance Director (final approvals, strategic)
        - RIM: Senior Finance Manager (VAT, tax, complex accruals)
        - LAS: Finance Manager (revenue, billable, reconciliations)
        - BOM: Finance Supervisor (bank, payroll, routine tasks)
        - JPAL: VAT/reporting support
        - JPL: AP/billing support
        - JI: Expense/assets
        - JO, JM: General support
        - RMQB: AP/payments support
        """
        im = task['logframe']['immediate_objective']
        activity = task['logframe']['activity']
        category = task.get('category', 'General')

        # High-level strategic tasks → CKVC (Finance Director)
        if any(kw in task['title'].lower() for kw in ['final review', 'approval', 'cfo', 'director']):
            assigned_to = 'CKVC'
            role = 'Finance Director'

        # Tax & VAT tasks → RIM (Senior Finance Manager) or JPAL (support)
        elif im == 'IM2':
            if 'vat' in activity.lower():
                assigned_to = 'RIM'  # Primary VAT responsibility
                role = 'Senior Finance Manager'
            elif 'payroll' in activity.lower() or 'final pay' in activity.lower():
                assigned_to = 'BOM'  # Payroll supervisor
                role = 'Finance Supervisor'
            else:
                assigned_to = 'RIM'  # Default for tax tasks
                role = 'Senior Finance Manager'

        # Revenue & billable tasks → LAS (Finance Manager)
        elif category == 'Revenue Recognition' or 'revenue' in activity.lower() or 'billable' in activity.lower():
            assigned_to = 'LAS'
            role = 'Finance Manager'

        # Bank & Cash → BOM (Finance Supervisor)
        elif category == 'Bank & Cash' or 'bank' in activity.lower():
            assigned_to = 'BOM'
            role = 'Finance Supervisor'

        # Accruals & Provisions → RIM (complex) or LAS (routine)
        elif category == 'Accruals & Provisions':
            if any(kw in task['title'].lower() for kw in ['management fee', 'royalty', 'consulting']):
                assigned_to = 'RIM'  # Complex accruals
                role = 'Senior Finance Manager'
            else:
                assigned_to = 'LAS'  # Routine accruals
                role = 'Finance Manager'

        # Depreciation & Assets → JI (Expense/assets specialist)
        elif category == 'Depreciation & Assets':
            assigned_to = 'JI'
            role = 'Finance Assistant (Assets)'

        # AP/Billing → JPL or RMQB
        elif 'payable' in task['title'].lower() or 'ap' in task['title'].lower():
            assigned_to = 'RMQB'
            role = 'Finance Assistant (AP/Payments)'

        # Default → BOM (Finance Supervisor)
        else:
            assigned_to = 'BOM'
            role = 'Finance Supervisor'

        task['assigned_to'] = {
            'employee_code': assigned_to,
            'role': role
        }

        return task

    def map_all_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map all tasks to LogFrame and assign employees."""
        enhanced_tasks = []

        for task in tasks:
            # Map to LogFrame
            task = self.map_task_to_im(task)

            # Assign employee
            task = self.assign_employee(task)

            enhanced_tasks.append(task)

        return enhanced_tasks

    def generate_summary(self, tasks: List[Dict[str, Any]]) -> str:
        """Generate LogFrame mapping summary report."""
        # Count by IM
        im_counts = {}
        for task in tasks:
            im = task['logframe']['immediate_objective']
            im_counts[im] = im_counts.get(im, 0) + 1

        # Count by activity
        activity_counts = {}
        for task in tasks:
            activity = task['logframe']['activity']
            activity_counts[activity] = activity_counts.get(activity, 0) + 1

        # Count by employee
        employee_counts = {}
        for task in tasks:
            emp_code = task['assigned_to']['employee_code']
            employee_counts[emp_code] = employee_counts.get(emp_code, 0) + 1

        report = f"""
LogFrame Mapping Summary
========================

Logical Framework Structure:
  Goal (G1): {self.LOGFRAME['goal']['name']}
  Outcome (O1): {self.LOGFRAME['outcome']['name']}

  Immediate Objective 1 (IM1): {self.LOGFRAME['immediate_objectives']['IM1']['name']}
    Indicator: {self.LOGFRAME['immediate_objectives']['IM1']['indicator']}

  Immediate Objective 2 (IM2): {self.LOGFRAME['immediate_objectives']['IM2']['name']}
    Indicator: {self.LOGFRAME['immediate_objectives']['IM2']['indicator']}

Task Distribution:
  Total tasks: {len(tasks)}
  IM1 (Month-End Closing): {im_counts.get('IM1', 0)} tasks
  IM2 (Tax Filing Compliance): {im_counts.get('IM2', 0)} tasks

Tasks by Activity:
{chr(10).join(f'  - {activity}: {count} tasks' for activity, count in sorted(activity_counts.items(), key=lambda x: x[1], reverse=True))}

Tasks by Employee Assignment:
{chr(10).join(f'  - {emp_code}: {count} tasks' for emp_code, count in sorted(employee_counts.items(), key=lambda x: x[1], reverse=True))}

Sample Task Mapping (first 5):
{chr(10).join(f'  {i+1}. [{t["assigned_to"]["employee_code"]}] {t["logframe"]["immediate_objective"]} → {t["logframe"]["activity"]}: {t["title"][:60]}...' for i, t in enumerate(tasks[:5]))}
"""
        return report


def main():
    """Main entry point for LogFrame mapper."""
    parser = argparse.ArgumentParser(description='Map tasks to LogFrame structure')
    parser.add_argument('--input', type=Path, required=True, help='Input JSON file with deduplicated tasks')
    parser.add_argument('--output', type=Path, required=True, help='Output JSON file with LogFrame mappings')
    parser.add_argument('--summary', action='store_true', help='Print summary report')

    args = parser.parse_args()

    # Load deduplicated tasks
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize mapper
    mapper = LogFrameMapper()

    # Map all tasks
    enhanced_tasks = mapper.map_all_tasks(data['tasks'])

    # Update data structure
    output_data = {
        **data,
        'tasks': enhanced_tasks,
        'logframe_structure': mapper.LOGFRAME
    }

    # Save output
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f'LogFrame mapping complete: {len(enhanced_tasks)} tasks mapped')
    print(f'Output saved to: {args.output}')

    # Print summary if requested
    if args.summary:
        print(mapper.generate_summary(enhanced_tasks))

    return 0


if __name__ == '__main__':
    exit(main())
