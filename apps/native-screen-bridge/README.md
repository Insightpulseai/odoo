# Native Screen Bridge

macOS native messaging host for Chrome extension screen capture.

## Install

```bash
# Register the native messaging host with Chrome
./install.sh
```

## How it works

Chrome extension sends JSON over stdin, this host captures a screenshot
using macOS `screencapture` and returns the result over stdout.

## Supported actions

- `capture_active_window` — captures the frontmost window
- `capture_full_screen` — captures the entire screen
