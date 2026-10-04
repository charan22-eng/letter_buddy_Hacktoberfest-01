import os

from fastapi import HTTPException, Request


def verify_lan_pin(request: Request):
    """Enforce LAN mode PIN requirement."""
    client_host = request.client.host if request.client else "127.0.0.1"

    # Loopback is always allowed
    if client_host in ("127.0.0.1", "localhost", "::1"):
        return True

    # LAN mode check
    pin = os.environ.get("LETTERBUDDY_LAN_PIN")
    if not pin:
        raise HTTPException(status_code=403, detail="LAN access blocked. Set LETTERBUDDY_LAN_PIN to enable.")

    if len(pin) < 6:
        raise HTTPException(status_code=500, detail="LETTERBUDDY_LAN_PIN must be at least 6 characters for security.")

    req_pin = request.headers.get("X-PIN") or request.query_params.get("pin") or request.cookies.get("letterbuddy_pin")
    if req_pin != pin:
        raise HTTPException(status_code=401, detail="Invalid LAN PIN")

    return True

import asyncio
import time
from pathlib import Path


def purge_old_files_once(directory: Path, max_age_seconds: int = 300):
    """Deletes files in directory older than max_age_seconds."""
    if not directory.exists(): return
    now = time.time()
    for f in directory.iterdir():
        if f.is_file():
            if now - f.stat().st_mtime > max_age_seconds:
                try:
                    f.unlink()
                except Exception:
                    pass

async def background_purge_task(audio_dir: Path):
    """Background task to run auto-purge every minute."""
    while True:
        purge_old_files_once(audio_dir, max_age_seconds=300)
        await asyncio.sleep(60)
