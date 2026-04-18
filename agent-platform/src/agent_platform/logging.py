"""Structured logging — uses structlog when available, stdlib fallback otherwise."""

from __future__ import annotations

import logging
from typing import Any

try:
    import structlog as _structlog

    def configure_logging(level: str = "INFO") -> None:
        logging.basicConfig(
            format="%(message)s",
            level=getattr(logging, level.upper(), logging.INFO),
        )
        _structlog.configure(
            wrapper_class=_structlog.make_filtering_bound_logger(
                getattr(logging, level.upper(), logging.INFO)
            ),
        )

    def get_logger(name: str) -> Any:
        return _structlog.get_logger(name)

except ImportError:

    class _StdlibAdapter:
        """Thin wrapper so .info/.warning/.error accept keyword context args."""

        def __init__(self, name: str) -> None:
            self._log = logging.getLogger(name)

        def _fmt(self, msg: str, kw: dict) -> str:
            if not kw:
                return msg
            ctx = " ".join(f"{k}={v}" for k, v in kw.items())
            return f"{msg} {ctx}"

        def info(self, msg: str, **kw: Any) -> None:
            self._log.info(self._fmt(msg, kw))

        def warning(self, msg: str, **kw: Any) -> None:
            self._log.warning(self._fmt(msg, kw))

        def error(self, msg: str, **kw: Any) -> None:
            self._log.error(self._fmt(msg, kw))

        def debug(self, msg: str, **kw: Any) -> None:
            self._log.debug(self._fmt(msg, kw))

    def configure_logging(level: str = "INFO") -> None:  # type: ignore[misc]
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            level=getattr(logging, level.upper(), logging.INFO),
        )

    def get_logger(name: str) -> Any:  # type: ignore[misc]
        return _StdlibAdapter(name)
