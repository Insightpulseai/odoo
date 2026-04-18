"""pytest conftest — add src/ to sys.path for editable-style imports without uv install."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
