"""
M.A.N.T.I.S. — Structured Logging
Winston-style structured logger with file rotation and WebSocket dashboard emitter.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from mantis.config import get_settings

# ── WebSocket broadcast registry ────────────────────────────────────────────
# Set of WebSocket connections to push agent log events to.
_ws_clients: set[Any] = set()


def register_ws_client(ws: Any) -> None:
    _ws_clients.add(ws)


def unregister_ws_client(ws: Any) -> None:
    _ws_clients.discard(ws)


async def broadcast_log(entry: dict) -> None:
    """Send a log entry to all connected dashboard WebSocket clients."""
    payload = json.dumps(entry)
    dead: list[Any] = []
    for ws in _ws_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.discard(ws)


# ── File logging setup ──────────────────────────────────────────────────────

def _ensure_log_dir(log_dir: str) -> Path:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _make_file_handler(log_dir: Path, filename: str, level: int = logging.DEBUG) -> logging.FileHandler:
    handler = logging.FileHandler(log_dir / filename, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"))
    return handler


# ── Logger singletons ───────────────────────────────────────────────────────
_initialized = False


def _setup_logging() -> None:
    global _initialized
    if _initialized:
        return
    _initialized = True

    settings = get_settings()
    log_dir = _ensure_log_dir(settings.log_dir)
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Agent logger — general decision loop events
    agent_logger = logging.getLogger("mantis.agent")
    agent_logger.setLevel(level)
    agent_logger.addHandler(_make_file_handler(log_dir, "agent.log"))
    agent_logger.addHandler(logging.StreamHandler(sys.stdout))

    # Transaction logger — on-chain tx records
    tx_logger = logging.getLogger("mantis.transactions")
    tx_logger.setLevel(logging.INFO)
    tx_logger.addHandler(_make_file_handler(log_dir, "transactions.log"))

    # Error logger
    err_logger = logging.getLogger("mantis.errors")
    err_logger.setLevel(logging.ERROR)
    err_logger.addHandler(_make_file_handler(log_dir, "errors.log"))
    err_logger.addHandler(logging.StreamHandler(sys.stderr))

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_agent_logger() -> logging.Logger:
    _setup_logging()
    return logging.getLogger("mantis.agent")


def get_tx_logger() -> logging.Logger:
    _setup_logging()
    return logging.getLogger("mantis.transactions")


def get_error_logger() -> logging.Logger:
    _setup_logging()
    return logging.getLogger("mantis.errors")


# ── Dashboard log helper ────────────────────────────────────────────────────

async def log_to_dashboard(
    action: str,
    message: str,
    tx_id: str | None = None,
    confidence: float = 0.0,
    urgency: str = "LOW",
) -> None:
    """Write to both file log and broadcast to dashboard WebSocket clients."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "message": message,
        "tx_id": tx_id,
        "confidence": confidence,
        "urgency": urgency,
    }

    logger = get_agent_logger()
    logger.info(f"{action} | {message}" + (f" | tx:{tx_id}" if tx_id else ""))

    if tx_id:
        tx_logger = get_tx_logger()
        tx_logger.info(f"{action} | tx:{tx_id} | {message}")

    await broadcast_log(entry)
