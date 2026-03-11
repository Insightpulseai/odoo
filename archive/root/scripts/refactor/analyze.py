#!/usr/bin/env python3
"""
Refactor Analysis Engine
Analyzes Python code for refactoring opportunities using multiple analyzers.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
except ImportError:
    print("Error: radon not installed. Run: pip install radon", file=sys.stderr)
    sys.exit(1)


class RefactorAnalyzer:
    """Main refactor analysis orchestrator"""

    def __init__(self, config_path: str = ".refactor/config.yaml"):
        self.config = self._load_config(config_path)
        self.findings = []

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_file = Path(path)
        if not config_file.exists():
            # Default config
            return {
                "analyzers": {
                    "complexity": {"enabled": True, "threshold": 10},
                    "duplication": {"enabled": True, "min_lines": 15},
                },
                "scoring": {"complexity": 0.5, "duplication": 0.5},
                "priority": {"critical": 90, "high": 70, "medium": 40, "low": 0},
            }

        with open(config_file) as f:
            return yaml.safe_load(f)

    def analyze_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Analyze a single Python file"""
        file_path = Path(filepath)

        if not file_path.exists():
            return []

        # Skip excluded patterns
        if self._should_exclude(str(file_path)):
            return []

        findings = []

        try:
            with open(file_path) as f:
                code = f.read()

            # Run complexity analyzer
            if self.config["analyzers"]["complexity"]["enabled"]:
                findings.extend(self._analyze_complexity(str(file_path), code))

            # Additional analyzers would go here (duplication, types, etc.)

        except Exception as e:
            print(f"Error analyzing {filepath}: {e}", file=sys.stderr)

        return findings

    def _should_exclude(self, filepath: str) -> bool:
        """Check if file should be excluded from analysis"""
        exclude_patterns = self.config["analyzers"]["complexity"].get(
            "exclude_patterns", []
        )
        for pattern in exclude_patterns:
            if pattern.replace("*", "") in filepath:
                return True
        return False

    def _analyze_complexity(self, filepath: str, code: str) -> List[Dict[str, Any]]:
        """Analyze code complexity using McCabe complexity"""
        findings = []
        threshold = self.config["analyzers"]["complexity"]["threshold"]

        try:
            # Get complexity for each function
            complexities = cc_visit(code)

            for complexity in complexities:
                if complexity.complexity > threshold:
                    score = min(100, (complexity.complexity / threshold) * 50 + 50)
                    priority = self._calculate_priority(score)

                    findings.append(
                        {
                            "type": "complexity",
                            "priority": priority,
                            "score": round(score, 2),
                            "file": filepath,
                            "line": complexity.lineno,
                            "function": complexity.name,
                            "message": f"High complexity: McCabe score {complexity.complexity} (threshold: {threshold})",
                            "suggestion": f"Consider refactoring {complexity.name} to reduce complexity",
                            "metrics": {
                                "complexity": complexity.complexity,
                                "threshold": threshold,
                            },
                        }
                    )

        except Exception as e:
            print(f"Complexity analysis error in {filepath}: {e}", file=sys.stderr)

        return findings

    def _calculate_priority(self, score: float) -> str:
        """Calculate priority based on score"""
        thresholds = self.config["priority"]

        if score >= thresholds["critical"]:
            return "critical"
        elif score >= thresholds["high"]:
            return "high"
        elif score >= thresholds["medium"]:
            return "medium"
        else:
            return "low"

    def analyze_files(self, files: List[str]) -> Dict[str, Any]:
        """Analyze multiple files and return findings"""
        all_findings = []

        for filepath in files:
            findings = self.analyze_file(filepath)
            all_findings.extend(findings)

        # Calculate summary statistics
        priority_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for finding in all_findings:
            priority_counts[finding["priority"]] += 1

        return {
            "findings": all_findings,
            "summary": {
                "total_findings": len(all_findings),
                "priority_counts": priority_counts,
                "files_analyzed": len(files),
            },
            "config": {
                "analyzers_enabled": [
                    name
                    for name, config in self.config["analyzers"].items()
                    if config.get("enabled", False)
                ],
            },
        }


def main():
    parser = argparse.ArgumentParser(description="Analyze code for refactor opportunities")
    parser.add_argument(
        "--files",
        nargs="+",
        help="Files to analyze",
    )
    parser.add_argument(
        "--output",
        default="findings.json",
        help="Output file for findings (JSON)",
    )
    parser.add_argument(
        "--config",
        default=".refactor/config.yaml",
        help="Configuration file",
    )

    args = parser.parse_args()

    if not args.files:
        print("Error: No files specified", file=sys.stderr)
        sys.exit(1)

    # Initialize analyzer
    analyzer = RefactorAnalyzer(config_path=args.config)

    # Analyze files
    print(f"Analyzing {len(args.files)} files...")
    results = analyzer.analyze_files(args.files)

    # Write results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    summary = results["summary"]
    print(f"\nAnalysis complete:")
    print(f"  Total findings: {summary['total_findings']}")
    print(f"  Critical: {summary['priority_counts']['critical']}")
    print(f"  High: {summary['priority_counts']['high']}")
    print(f"  Medium: {summary['priority_counts']['medium']}")
    print(f"  Low: {summary['priority_counts']['low']}")
    print(f"\nResults written to: {output_path}")

    # Exit with error if critical findings exist
    if summary["priority_counts"]["critical"] > 0:
        print("\n❌ Critical findings detected!", file=sys.stderr)
        sys.exit(1)

    print("\n✅ No critical findings")
    sys.exit(0)


if __name__ == "__main__":
    main()
