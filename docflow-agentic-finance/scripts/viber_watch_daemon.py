from __future__ import annotations
import os
import sys
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import subprocess

# Add parent directory to path so we can import docflow
sys.path.append(str(Path(__file__).parent.parent))

SUPPORTED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


class Handler(FileSystemEventHandler):
    def __init__(self, inbox: Path, project_root: Path):
        self.inbox = inbox
        self.project_root = project_root

    def on_created(self, event):
        if event.is_directory:
            return
        src = Path(event.src_path)
        if src.suffix.lower() not in SUPPORTED_EXT:
            return

        print(f"[watch] Detected {src}")
        # wait for file to finish writing (simple, effective)
        for _ in range(20):
            try:
                size1 = src.stat().st_size
                time.sleep(0.5)
                size2 = src.stat().st_size
                if size2 == size1 and size2 > 0:
                    break
            except FileNotFoundError:
                return

        dest = self.inbox / src.name
        # avoid collisions
        if dest.exists():
            dest = self.inbox / f"{src.stem}.{int(time.time())}{src.suffix}"

        try:
            shutil.copy2(src, dest)
            print(f"[watch] Copied {src} -> {dest}")

            # trigger one-shot processing (idempotent; archives)
            # Use same python interpreter
            cmd = [sys.executable, str(self.project_root / "scripts" / "run_folder.py")]
            print(f"[watch] Running pipeline: {' '.join(cmd)}")
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"[watch] Error: {e}")


def main():
    load_dotenv()
    watch_dir_str = os.getenv("VIBER_WATCH_DIR", "")
    if not watch_dir_str:
        print("VIBER_WATCH_DIR not set in .env")
        return

    watch_dir = Path(watch_dir_str).expanduser()
    inbox = Path(os.getenv("DOCFLOW_INBOX", "data/inbox"))
    inbox.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).parent.parent

    if not watch_dir.exists():
        print(f"VIBER_WATCH_DIR does not exist: {watch_dir}")
        return

    event_handler = Handler(inbox=inbox, project_root=project_root)
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=False)
    observer.start()
    print(f"[watch] watching {watch_dir} -> inbox {inbox}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
