#!/usr/bin/env python3
"""Native messaging host for Chrome extension screen capture.

Communicates via stdin/stdout using Chrome's native messaging protocol:
- Read: 4-byte little-endian length prefix + JSON
- Write: 4-byte little-endian length prefix + JSON

Supports macOS only. Uses `screencapture` CLI.
"""
import json
import os
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


CAPTURE_DIR = Path(tempfile.gettempdir()) / "ipai" / "captures"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def read_message():
    """Read a native messaging message from stdin."""
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) < 4:
        return None
    length = struct.unpack("<I", raw_length)[0]
    data = sys.stdin.buffer.read(length)
    return json.loads(data.decode("utf-8"))


def write_message(msg):
    """Write a native messaging message to stdout."""
    encoded = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def generate_capture_id():
    now = datetime.now(timezone.utc)
    return f"cap_{now.strftime('%Y%m%d_%H%M%S')}"


def get_image_dimensions(filepath):
    """Get image dimensions using sips (macOS)."""
    try:
        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", filepath],
            capture_output=True,
            text=True,
            timeout=5,
        )
        width = height = 0
        for line in result.stdout.splitlines():
            if "pixelWidth" in line:
                width = int(line.split(":")[-1].strip())
            elif "pixelHeight" in line:
                height = int(line.split(":")[-1].strip())
        return width, height
    except Exception:
        return 0, 0


def capture_active_window():
    """Capture the frontmost window using macOS screencapture."""
    capture_id = generate_capture_id()
    filepath = str(CAPTURE_DIR / f"{capture_id}.png")

    # -w = interactive window mode, -l = specific window
    # -o = no shadow, -x = no sound
    # Use -w with -o for window capture; fall back to active window via osascript
    try:
        # Get the frontmost window ID
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get id of first window of (first process whose frontmost is true)',
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        window_id = result.stdout.strip()

        if window_id:
            subprocess.run(
                ["screencapture", "-l", window_id, "-o", "-x", filepath],
                check=True,
                timeout=10,
            )
        else:
            # Fallback: capture frontmost window interactively
            subprocess.run(
                ["screencapture", "-w", "-o", "-x", filepath],
                check=True,
                timeout=10,
            )
    except subprocess.CalledProcessError:
        return {"error": "screencapture failed", "capture_id": capture_id}

    if not os.path.exists(filepath):
        return {"error": "capture file not created", "capture_id": capture_id}

    width, height = get_image_dimensions(filepath)

    return {
        "capture_id": capture_id,
        "file_path": filepath,
        "mime_type": "image/png",
        "width": width,
        "height": height,
        "source": "active_window",
    }


def capture_full_screen():
    """Capture the entire screen using macOS screencapture."""
    capture_id = generate_capture_id()
    filepath = str(CAPTURE_DIR / f"{capture_id}.png")

    try:
        subprocess.run(
            ["screencapture", "-x", filepath],
            check=True,
            timeout=10,
        )
    except subprocess.CalledProcessError:
        return {"error": "screencapture failed", "capture_id": capture_id}

    if not os.path.exists(filepath):
        return {"error": "capture file not created", "capture_id": capture_id}

    width, height = get_image_dimensions(filepath)

    return {
        "capture_id": capture_id,
        "file_path": filepath,
        "mime_type": "image/png",
        "width": width,
        "height": height,
        "source": "full_screen",
    }


def main():
    msg = read_message()
    if msg is None:
        write_message({"error": "no input"})
        return

    action = msg.get("action", "")

    if action == "capture_active_window":
        result = capture_active_window()
    elif action == "capture_full_screen":
        result = capture_full_screen()
    else:
        result = {"error": f"unknown action: {action}"}

    write_message(result)


if __name__ == "__main__":
    main()
