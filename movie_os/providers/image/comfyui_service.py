"""ComfyUI Service Manager (SAI-94 / TASK-014).

A reliable lifecycle manager for the ComfyUI rendering backend:

  - detect an already-running server on the configured URL and reuse it
  - launch a detached server if none is running
  - verify install path exists
  - health-check via /system_stats until ready (bounded)
  - track PID, stream logs, and shut down cleanly (bounded timeout)

Detached launch (no pipe) avoids the KSampler BrokenPipeError that a `| tee`
pipe causes on macOS. On a shared/local backend the same semantics hold.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlopen

logger = logging.getLogger("movie_os.providers.comfyui_service")


@dataclass
class ComfyUIService:
    """State and lifecycle for one ComfyUI service."""

    url: str = "http://localhost:8191"
    install_path: str = "/Users/santosh/ComfyUI-Installs/ComfyUI/ComfyUI"
    python: str = sys.executable
    port: int = 8191
    health_timeout: float = 60.0
    startup_timeout: float = 180.0
    shutdown_timeout: float = 20.0
    pid_file: str = ".runtime/comfyui.pid"
    log_file: str = ".runtime/comfyui.log"
    pid: Optional[int] = field(default=None, init=False)
    _process: Optional[subprocess.Popen] = field(default=None, init=False, repr=False)

    # ── detection ───────────────────────────────────────────────────────
    def is_running(self) -> bool:
        """True if the health endpoint responds on the configured URL."""
        try:
            with urlopen(self.url + "/system_stats", timeout=5) as r:
                return r.status == 200
        except Exception:
            return False

    def _load_stored_pid(self) -> Optional[int]:
        try:
            return int(Path(self.pid_file).read_text().strip())
        except Exception:
            return None

    def install_ok(self) -> bool:
        main_py = Path(self.install_path) / "main.py"
        return main_py.exists()

    # ── launch ──────────────────────────────────────────────────────────
    def launch(self) -> subprocess.Popen:
        """Launch a detached ComfyUI server (no pipe). Returns the Popen."""
        main_py = Path(self.install_path) / "main.py"
        if not main_py.exists():
            raise FileNotFoundError(f"ComfyUI main.py not found at {main_py}")
        log_parent = Path(self.log_file).parent
        log_parent.mkdir(parents=True, exist_ok=True)
        log_fh = open(self.log_file, "ab")
        proc = subprocess.Popen(
            [self.python, "-s", str(main_py), "--port", str(self.port)],
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        self._process = proc
        self.pid = proc.pid
        self._write_pid(proc.pid)
        logger.info(f"[comfyui] launched pid={proc.pid} port={self.port} log={self.log_file}")
        return proc

    def _write_pid(self, pid: int) -> None:
        Path(self.pid_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.pid_file).write_text(str(pid))

    # ── readiness ───────────────────────────────────────────────────────
    def wait_ready(self, timeout: Optional[float] = None) -> bool:
        """Block until /system_stats responds or timeout elapses."""
        deadline = time.time() + (timeout or self.health_timeout)
        while time.time() < deadline:
            if self.is_running():
                return True
            time.sleep(1.0)
        return False

    def wait_startup(self, timeout: Optional[float] = None) -> bool:
        """Wait for full startup (server up + FLUX nodes loaded)."""
        deadline = time.time() + (timeout or self.startup_timeout)
        while time.time() < deadline:
            if self.is_running():
                if self._flux_ready():
                    return True
            time.sleep(2.0)
        return False

    def _flux_ready(self) -> bool:
        """Check the object_info/samplers endpoint to confirm nodes are loaded."""
        try:
            with urlopen(self.url + "/object_info/KSampler", timeout=8) as r:
                return r.status == 200
        except Exception:
            return False

    # ── shutdown ────────────────────────────────────────────────────────
    def shutdown(self) -> bool:
        """Terminate the managed server (and the stored/known PID)."""
        targets = [self.pid]
        stored = self._load_stored_pid()
        if stored and stored not in targets:
            targets.append(stored)
        ok = True
        for pid in targets:
            if pid is None:
                continue
            try:
                os.kill(pid, 15)  # SIGTERM
            except ProcessLookupError:
                continue
            except Exception as e:
                logger.warning(f"[comfyui] kill {pid} failed: {e}")
                ok = False
        # remove pid file
        try:
            Path(self.pid_file).unlink(missing_ok=True)
        except Exception:
            pass
        return ok


# ── orchestrating helper ────────────────────────────────────────────────────
def ensure_comfyui(
    mngr: ComfyUIService | None = None,
    launch_if_missing: bool = True,
    wait_startup: bool = True,
) -> ComfyUIService:
    """Return a ready ComfyUI service, launching one if needed.

    Reuses an already-running server (never double-launches). If none is
    running and launch_if_missing=True, launches and waits for startup.
    """
    mngr = mngr or ComfyUIService()
    if mngr.is_running():
        logger.info(f"[comfyui] reusing running server on {mngr.url}")
        return mngr
    if not mngr.install_ok():
        raise FileNotFoundError(f"ComfyUI install missing at {mngr.install_path}")
    if not launch_if_missing:
        return mngr  # not running, caller chose not to launch
    mngr.launch()
    ready = mngr.wait_startup() if wait_startup else mngr.wait_ready()
    if not ready:
        logger.error("[comfyui] service failed to become ready; see log %s", mngr.log_file)
        raise TimeoutError(f"ComfyUI did not become ready in {mngr.startup_timeout}s")
    return mngr
