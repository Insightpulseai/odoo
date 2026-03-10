from __future__ import annotations
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path so we can import docflow
sys.path.append(str(Path(__file__).parent.parent))

from src.docflow.runner import DocFlowRunner


def main():
    load_dotenv()

    print(f"DocFlow Runner starting...")

    runner = DocFlowRunner()
    results = runner.run_folder()

    success_count = sum(1 for r in results if r.status != "failed")
    failed_count = sum(1 for r in results if r.status == "failed")
    auto_drafted_count = sum(1 for r in results if r.status == "auto_drafted")
    needs_review_count = sum(1 for r in results if r.status == "needs_review")

    print(f"Done. processed={len(results)}, success={success_count}, failed={failed_count}")
    print(f"  auto_drafted={auto_drafted_count}, needs_review={needs_review_count}")


if __name__ == "__main__":
    main()
