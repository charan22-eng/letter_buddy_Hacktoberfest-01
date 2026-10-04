"""
Letter Buddy – Network guard.

Blocks all non-loopback outbound connections when LETTERBUDDY_OFFLINE=1.
Ollama runs on loopback (127.0.0.1:11434), so it's allowed.
This is the privacy backbone: letters NEVER leave the machine.
"""

from __future__ import annotations

import ipaddress
import logging
import os
import socket

logger = logging.getLogger(__name__)

_orig_connect = socket.socket.connect
_enabled = False


def _guarded_connect(self: socket.socket, addr: tuple | str | bytes) -> None:
    """Intercept socket.connect and block non-loopback destinations."""
    if isinstance(addr, tuple):
        host = str(addr[0])
    elif isinstance(addr, str):
        host = addr
    else:
        host = addr.decode("utf-8", errors="replace") if isinstance(addr, bytes) else str(addr)

    try:
        ok = ipaddress.ip_address(host).is_loopback
    except ValueError:
        ok = host in ("localhost", "::1")

    if not ok:
        raise ConnectionError(
            f"netguard: blocked non-loopback connection to {addr}. "
            f"Letter Buddy runs 100% offline."
        )

    return _orig_connect(self, addr)


def enable() -> None:
    """Enable the network guard. Called at startup if LETTERBUDDY_OFFLINE=1."""
    global _enabled
    if _enabled:
        return
    socket.socket.connect = _guarded_connect  # type: ignore[assignment]
    _enabled = True
    logger.info("netguard: enabled — blocking all non-loopback connections")


def disable() -> None:
    """Disable the network guard (for setup/download phases only)."""
    global _enabled
    if not _enabled:
        return
    socket.socket.connect = _orig_connect  # type: ignore[assignment]
    _enabled = False
    logger.info("netguard: disabled")


def is_enabled() -> bool:
    return _enabled


def auto_enable() -> None:
    """Enable if LETTERBUDDY_OFFLINE env var is set to 1."""
    if os.environ.get("LETTERBUDDY_OFFLINE", "").strip() == "1":
        enable()
