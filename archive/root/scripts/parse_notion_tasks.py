#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion Task Parser for Month-End Closing Tasks
Parses 73 HTML exports from Notion Kanban board and extracts structured task data.

Usage:
    python3 scripts/parse_notion_tasks.py --input /Users/tbwa/Downloads/notion-kanban/Untitled/New\ data\ source/ --output data/notion_tasks_parsed.json

Author: Jake Tolentino
Date: 2025-11-26
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from html.parser import HTMLParser
from bs4 import BeautifulSoup


class NotionTaskParser:
    """Parser for Notion HTML export files."""

    def __init__(self, input_dir: Path):
        self.input_dir = input_dir
        self.tasks = []
        self.duplicates = []

    def parse_html_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a single Notion HTML file and extract task data.

        Args:
            file_path: Path to HTML file

        Returns:
            Dictionary with task metadata and content
        """
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title from <title> tag
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else file_path.stem

        # Extract main content from article or body
        article = soup.find("article") or soup.find("body")

        # Get task description (first paragraph or div after title)
        description = ""
        if article:
            # Look for main content paragraphs
            paragraphs = article.find_all("p", limit=3)
            if paragraphs:
                description = "\n".join(
                    [
                        p.get_text(strip=True)
                        for p in paragraphs
                        if p.get_text(strip=True)
                    ]
                )

        # Extract Notion page ID from filename
        notion_id = file_path.stem.split(" ")[-1] if " " in file_path.stem else ""

        # Categorize task based on keywords
        category = self._categorize_task(title)
        wbs_phase = self._map_to_wbs_phase(title)

        return {
            "title": title,
            "description": description or title,  # Fallback to title if no description
            "notion_id": notion_id,
            "file_name": file_path.name,
            "category": category,
            "wbs_phase": wbs_phase,
            "priority": self._infer_priority(title),
            "estimated_days": self._estimate_duration(title),
        }

    def _categorize_task(self, title: str) -> str:
        """Categorize task based on keywords in title."""
        title_lower = title.lower()

        if any(
            kw in title_lower for kw in ["vat", "tax", "withholding", "bir", "2307"]
        ):
            return "Tax & Compliance"
        elif any(kw in title_lower for kw in ["accrue", "accrual", "provision"]):
            return "Accruals & Provisions"
        elif any(
            kw in title_lower for kw in ["depreciation", "amortization", "fixed asset"]
        ):
            return "Depreciation & Assets"
        elif any(
            kw in title_lower for kw in ["revenue", "billable", "oopc", "retainer"]
        ):
            return "Revenue Recognition"
        elif any(kw in title_lower for kw in ["bank", "reconciliation", "recon"]):
            return "Bank & Cash"
        elif any(kw in title_lower for kw in ["payroll", "final pay", "sl conversion"]):
            return "Payroll"
        elif any(kw in title_lower for kw in ["reclassification", "oop", "wip"]):
            return "Reclassifications"
        elif any(
            kw in title_lower
            for kw in ["report", "aging", "working capital", "summary"]
        ):
            return "Reporting"
        elif any(
            kw in title_lower
            for kw in ["revaluation", "foreign currency", "intercompany"]
        ):
            return "Adjustments"
        else:
            return "General"

    def _map_to_wbs_phase(self, title: str) -> str:
        """Map task to WBS phase based on typical month-end workflow."""
        category = self._categorize_task(title)

        # Phase 1: Initial & Compliance (Days 1-5)
        if category in ["Bank & Cash", "Tax & Compliance", "Payroll"]:
            return "Phase 1: Initial & Compliance"

        # Phase 2: Revenue & Core Accruals (Days 3-7)
        elif category in ["Revenue Recognition", "Accruals & Provisions"]:
            return "Phase 2: Revenue & Core Accruals"

        # Phase 3: WIP/Final Accruals (Days 5-10)
        elif category in ["Reclassifications"]:
            return "Phase 3: WIP/Final Accruals"

        # Phase 4: Final Adjustments & Close (Days 8-12)
        elif category in ["Depreciation & Assets", "Adjustments", "Reporting"]:
            return "Phase 4: Final Adjustments & Close"

        else:
            return "Phase 2: Revenue & Core Accruals"  # Default

    def _infer_priority(self, title: str) -> str:
        """Infer task priority based on keywords."""
        title_lower = title.lower()

        if any(
            kw in title_lower for kw in ["bank", "payroll", "tax", "bir", "critical"]
        ):
            return "1"  # High priority
        elif any(kw in title_lower for kw in ["report", "review", "summary"]):
            return "2"  # Medium-high
        else:
            return "3"  # Normal

    def _estimate_duration(self, title: str) -> int:
        """Estimate task duration in days based on complexity keywords."""
        title_lower = title.lower()

        if any(kw in title_lower for kw in ["compile", "review", "prepare"]):
            return 2
        elif any(kw in title_lower for kw in ["calculate", "record", "perform"]):
            return 1
        elif any(kw in title_lower for kw in ["generate", "create", "process"]):
            return 3
        else:
            return 1  # Default 1 day

    def parse_all_tasks(self) -> List[Dict[str, Any]]:
        """Parse all HTML files in input directory."""
        html_files = sorted(self.input_dir.glob("*.html"))
        print(f"Found {len(html_files)} HTML files to parse...")

        for html_file in html_files:
            try:
                task_data = self.parse_html_file(html_file)
                self.tasks.append(task_data)
            except Exception as e:
                print(f"Error parsing {html_file.name}: {e}")

        print(f"Successfully parsed {len(self.tasks)} tasks")
        return self.tasks

    def detect_duplicates(self, existing_tasks: List[str]) -> List[Dict[str, Any]]:
        """
        Detect duplicate tasks by comparing titles.

        Args:
            existing_tasks: List of existing task titles from seed data

        Returns:
            List of tasks that are NOT duplicates
        """
        unique_tasks = []

        for task in self.tasks:
            # Normalize title for comparison
            normalized_title = re.sub(r"[^\w\s]", "", task["title"].lower())

            # Check if similar title exists
            is_duplicate = False
            for existing in existing_tasks:
                normalized_existing = re.sub(r"[^\w\s]", "", existing.lower())

                # Simple similarity check (>80% character overlap)
                if (
                    self._calculate_similarity(normalized_title, normalized_existing)
                    > 0.8
                ):
                    is_duplicate = True
                    self.duplicates.append(
                        {
                            "notion_task": task["title"],
                            "existing_task": existing,
                            "similarity": self._calculate_similarity(
                                normalized_title, normalized_existing
                            ),
                        }
                    )
                    break

            if not is_duplicate:
                unique_tasks.append(task)

        print(
            f"Found {len(unique_tasks)} unique tasks (filtered out {len(self.duplicates)} duplicates)"
        )
        return unique_tasks

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple character-based similarity ratio."""
        if not str1 or not str2:
            return 0.0

        # Simple set-based Jaccard similarity
        set1 = set(str1.split())
        set2 = set(str2.split())

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def export_to_json(self, output_path: Path, include_duplicates: bool = True):
        """Export parsed tasks to JSON file."""
        output_data = {
            "total_parsed": len(self.tasks),
            "unique_tasks": len(
                [
                    t
                    for t in self.tasks
                    if t not in [d["notion_task"] for d in self.duplicates]
                ]
            ),
            "duplicate_count": len(self.duplicates),
            "tasks": self.tasks,
        }

        if include_duplicates:
            output_data["duplicates"] = self.duplicates

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Exported task data to {output_path}")

    def generate_summary_report(self) -> str:
        """Generate human-readable summary report."""
        category_counts = {}
        wbs_counts = {}

        for task in self.tasks:
            category_counts[task["category"]] = (
                category_counts.get(task["category"], 0) + 1
            )
            wbs_counts[task["wbs_phase"]] = wbs_counts.get(task["wbs_phase"], 0) + 1

        report = f"""
Notion Task Parsing Summary
===========================
Total tasks parsed: {len(self.tasks)}
Duplicate tasks found: {len(self.duplicates)}
Unique tasks: {len(self.tasks) - len(self.duplicates)}

Tasks by Category:
{chr(10).join(f'  - {cat}: {count}' for cat, count in sorted(category_counts.items()))}

Tasks by WBS Phase:
{chr(10).join(f'  - {phase}: {count}' for phase, count in sorted(wbs_counts.items()))}

Top 10 Tasks by Priority:
{chr(10).join(f'  {i+1}. [{t["priority"]}] {t["title"][:80]}' for i, t in enumerate(sorted(self.tasks, key=lambda x: x['priority'])[:10]))}
"""
        return report


def main():
    """Main entry point for Notion task parser."""
    parser = argparse.ArgumentParser(description="Parse Notion HTML task exports")
    parser.add_argument(
        "--input", type=Path, required=True, help="Input directory with HTML files"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/notion_tasks_parsed.json"),
        help="Output JSON file",
    )
    parser.add_argument("--summary", action="store_true", help="Print summary report")

    args = parser.parse_args()

    # Initialize parser
    notion_parser = NotionTaskParser(args.input)

    # Parse all tasks
    tasks = notion_parser.parse_all_tasks()

    # Export to JSON
    notion_parser.export_to_json(args.output)

    # Print summary if requested
    if args.summary:
        print(notion_parser.generate_summary_report())

    return 0


if __name__ == "__main__":
    exit(main())
