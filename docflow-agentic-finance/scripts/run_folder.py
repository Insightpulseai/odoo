from __future__ import annotations
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path so we can import docflow
sys.path.append(str(Path(__file__).parent.parent))

from src.docflow.runner import run_folder


def main():
    load_dotenv()
    inbox = Path(os.getenv("DOCFLOW_INBOX", "data/inbox"))
    archive = Path(os.getenv("DOCFLOW_ARCHIVE", "data/archive"))

    print(f"DocFlow Runner starting...")
    print(f"Inbox: {inbox.absolute()}")
    print(f"Archive: {archive.absolute()}")

    n = run_folder(inbox, archive)
    print(f"Done. processed={n}")


if __name__ == "__main__":
    main()
