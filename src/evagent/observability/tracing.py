from __future__ import annotations

import logging

try:
    import structlog
except Exception:  # pragma: no cover - optional dependency fallback
    structlog = None  # type: ignore[assignment]


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")
    if structlog is not None:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.JSONRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
        )


def get_logger(name: str):
    if structlog is not None:
        return structlog.get_logger(name)
    return logging.getLogger(name)
