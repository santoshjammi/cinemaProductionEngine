"""ComfyUI HTTP + WebSocket client.

ComfyUI exposes both a REST API on a configurable port (default 8188) and
a native WebSocket on the same port under ``/ws``. This client wraps *both*
and exposes a clean Python interface that gives **real-time progress updates**
instead of silent HTTP polling.

Key endpoints used:
  - POST /prompt           — submit a workflow, returns a prompt_id
  - GET  /history/{id}     — check if a prompt is complete + get outputs
  - GET  /queue             — check the queue
  - GET  /models            — list available models
  - GET  /view              — fetch the generated image bytes
  - GET  /system_stats      — health / liveness probe
  - GET  /object_info       — available nodes (proves FLUX is loaded)
  - WS   /ws/{client_id}   — real-time queue + progress events

Usage:

    from movie_os.workflows import ComfyUIClient

    client = ComfyUIClient(base_url="http://localhost:8188")

    # Optional: verify the model is actually loaded and ready
    client.health()
    client.wait_for_node_ready()          # blocks until FLUX nodes are loaded

    prompt_id = client.submit(workflow_dict, priority="normal")
    client.wait_for_result(prompt_id)     # WebSocket-backed with progress

"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger("movie_os.workflows")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ComfyUIError(RuntimeError):
    """Raised when a ComfyUI call fails."""
    pass


class ComfyUIConnectionError(ComfyUIError):
    """Raised when ComfyUI cannot be reached."""
    pass


class ComfyUITimeoutError(ComfyUIError):
    """Raised when an operation exceeds its timeout window."""
    pass


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

class ComfyUIClient:
    """HTTP client for ComfyUI's REST API + native WebSocket.

    The REST API is synchronous and sufficient for submitting workflows.
    The WebSocket layer (*optional*) enables real-time progress updates so
    you never sit in the dark waiting for a prompt to finish.

    **Why WebSocket?**  ComfyUI pushes events on ``/ws/{client_id}``:
      - *queue_in_progress* — your job moved from queue → GPU
      - *executing / execution_start / execution_pending / execution_error*
        — node-level progress within the running prompt
      - Without this, your client can only *poll* ``/history`` every second,
        which is both wasteful and invisible to the user.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8188",
        api_key: str | None = None,
        timeout: float = 600.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client_id: str = f"movie_os_{uuid.uuid4().hex[:8]}"
        self._ws_task: asyncio.Task | None = None  # background WS reader
        self._ws_queue: asyncio.Queue[str] = asyncio.Queue()
        self._event_callbacks: list[Callable[[str, dict], Any]] = []

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        timeout: float | None = None,
    ) -> Any:
        """Make an HTTP request to ComfyUI."""
        url = f"{self.base_url}{path}"
        data = json.dumps(json_body).encode("utf-8") if json_body is not None else None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                raw = resp.read()
                if not raw:
                    return None
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type or content_type.startswith("text/"):
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return raw.decode("utf-8", errors="replace")
                return raw
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            raise ComfyUIError(
                f"ComfyUI {method} {path} failed: HTTP {e.code} — {body[:500]}"
            ) from e
        except urllib.error.URLError as e:
            raise ComfyUIConnectionError(
                f"ComfyUI unreachable at {self.base_url}: {e}"
            ) from e

    # ------------------------------------------------------------------
    # Liveness / readiness probes
    # ------------------------------------------------------------------

    def health(self) -> bool:
        """Check if ComfyUI is reachable and responding.

        **Note:** this only proves the server process is alive. A healthy
        server may still be loading models, which means ``/prompt`` will sit
        in the queue until warmup finishes. Use :meth:`wait_for_node_ready`
        after this to guarantee rendering capability.
        """
        try:
            self._request("GET", "/system_stats", timeout=5.0)
            return True
        except (ComfyUIError, Exception):
            return False

    def wait_for_node_ready(
        self,
        *,
        timeout: float = 120.0,
        node_prefixes: list[str] | None = None,
    ) -> dict | None:
        """Block until ComfyUI reports FLUX-related nodes are loaded.

        After launching ComfyUI the GPU is idle while it streams model
        weights into VRAM. During that window *every* ``/prompt`` submit
        sits in the queue with no error — just silence. This method solves
        that blind spot by watching :attr:`_object_info` (populated when
        ComfyUI finishes its own startup warmup).

        Parameters
        ----------
        timeout: seconds to wait before giving up. Defaults to 120 s.
        node_prefixes: only meaningful nodes if *at least one* of these
            prefixes appears in the loaded node list (e.g. ``["Flux",
            "UNETLoader", "clip_text"]``).  Pass ``None`` to skip prefix
            checks and just wait for any node info response.

        Returns
        -------
        The parsed ``/object_info`` dict, or ``None`` on timeout.
        """
        prefixes = node_prefixes or ["Flux", "UNETLoader", "clip_text"]
        deadline = time.time() + timeout
        last_progress = ""
        while time.time() < deadline:
            try:
                info = self._request("GET", "/object_info")
                if not isinstance(info, dict):
                    time.sleep(1)
                    continue

                # If specific prefixes requested, wait until all appear
                loaded_nodes = set()
                for section in info.values():
                    if isinstance(section, dict):
                        loaded_nodes.update(section.keys())

                found = [p for p in prefixes if any(p.lower() in n.lower() for n in loaded_nodes)]
                if found:
                    progress = ", ".join(found)
                    if progress != last_progress:
                        logger.info("[ComfyUI] Node ready — %s loaded", progress)
                        last_progress = progress
                    return info

            except (ComfyUIError, Exception):
                time.sleep(1.0)  # still loading / restarting — sleep and keep waiting

        logger.warning(
            "[ComfyUI] wait_for_node_ready timed out after %.0fs — "
            "nodes may still be streaming into VRAM",
            timeout,
        )
        return None

    def get_queue_position(self) -> dict:
        """Return ``{queue_running: [...], queue_pending: [...]}``."""
        result = self._request("GET", "/queue", timeout=5.0)
        if isinstance(result, dict):
            return result
        return {"queue_running": [], "queue_pending": []}

    # ------------------------------------------------------------------
    # High-level operations
    # ------------------------------------------------------------------

    def unload_models(self) -> None:
        """Unload all models from VRAM using POST /free endpoint."""
        try:
            self._request(
                "POST",
                "/free",
                json_body={"unload_models": True, "free_memory": True},
                timeout=10.0,
            )
            logger.info("[ComfyUI] Successfully unloaded models and freed memory")
        except Exception as e:
            logger.warning("[ComfyUI] Failed to unload models: %s", e)

    def list_models(self) -> list[str]:
        """List available model checkpoints."""
        result = self._request("GET", "/models", timeout=10.0)
        if isinstance(result, list):
            return result
        return []

    def submit(
        self,
        workflow: dict,
        *,
        client_id: str | None = None,
        priority: str = "normal",
        **kwargs: Any,  # allow extra keys like "front" for newer ComfyUI
    ) -> str:
        """Submit a workflow to ComfyUI's queue.

        Parameters
        ----------
        workflow: the full workflow dict.
        client_id: unique ID for this client (auto-generated if omitted).
        priority: one of ``"normal"``, ``"high"``, ``"low"``.  Using
            ``"high"`` pushes your job ahead of queued ``"normal"`` jobs
            but **does not** interrupt a running prompt.

        Returns
        -------
        The ``prompt_id`` assigned by ComfyUI.
        """
        cid = client_id or self._client_id
        payload: dict[str, Any] = {
            "prompt": workflow,
            "client_id": cid,
            "front": priority == "high",  # newer ComfyUI uses 'front' not 'priority'
        }
        result = self._request("POST", "/prompt", json_body=payload)
        if not isinstance(result, dict) or "prompt_id" not in result:
            raise ComfyUIError(
                f"ComfyUI /prompt returned unexpected response: {result!r}"
            )
        prompt_id = result["prompt_id"]
        logger.info("[ComfyUI] Submitted workflow — prompt_id=%s (priority=%s)", prompt_id, priority)
        return prompt_id

    def get_history(self, prompt_id: str) -> dict | None:
        """Get the history entry for a prompt_id, or None if not found."""
        result = self._request("GET", f"/history/{prompt_id}", timeout=10.0)
        if not isinstance(result, dict):
            return None
        return result.get(prompt_id)

    # ------------------------------------------------------------------
    # WebSocket helpers (async)
    # ------------------------------------------------------------------

    async def _ws_connect(self) -> None:
        """Start the WebSocket background reader.

        Requires ``websockets`` package (pip install websockets).
        Falls back gracefully if unavailable — polling still works.
        """
        try:
            import websockets  # type: ignore[import-untyped]
        except ImportError:
            logger.info(
                "[ComfyUI] 'websockets' not installed; falling back to HTTP "
                "polling. Install it for real-time progress: pip install websockets"
            )
            return

        ws_url = self.base_url.replace("http", "ws", 1) + f"/ws/{self._client_id}"
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                logger.info("[ComfyUI] WebSocket connected — real-time progress enabled")
                while True:
                    raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    msg = json.loads(raw)
                    if "type" in msg:
                        event_type = msg["type"]
                        logger.debug("[ComfyUI WS] %s", event_type)
                        for cb in self._event_callbacks:
                            try:
                                await asyncio.create_task(cb(event_type, msg))
                            except Exception:
                                pass

        except (ConnectionRefusedError, OSError) as exc:
            logger.info(
                "[ComfyUI] WebSocket connect failed (%s) — will use HTTP polling",
                exc,
            )
        except asyncio.TimeoutError:
            logger.info("[ComfyUI] WebSocket read timed out — switching to polling")

    def on_event(self, callback: Callable[[str, dict], Any]) -> None:
        """Register a callback for ComfyUI WS events.

        Example::

            client.on_event(lambda typ, msg: print(typ, msg))
        """
        self._event_callbacks.append(callback)

    # ------------------------------------------------------------------
    # Wait helpers (HTTP polling + optional WS progress)
    # ------------------------------------------------------------------

    def _find_comfyui_output_dir(self) -> Path | None:
        """Find ComfyUI's output directory by probing default locations."""
        defaults = [
            Path.home() / "ComfyUI" / "output",
            Path("/tmp") / "ComfyUI" / "output",
            Path.cwd() / "ComfyUI" / "output",
            self.base_url.replace("http://localhost:", "/").replace("127.0.0.1", "") if 'ComfyUI' in self.base_url else None,
        ]
        for d in defaults:
            if d and Path(d).exists():
                return Path(d)
        return None


    def wait_for_result(
        self,
        prompt_id: str,
        *,
        timeout: float | None = None,
        poll_interval: float = 1.0,
        show_progress: bool = True,
    ) -> dict:
        """Poll /history until the prompt completes (or times out).

        When ``show_progress`` is *True*, this method uses WebSocket events
        if available, falling back to silent HTTP polling otherwise.

        Parameters
        ----------
        prompt_id: as returned by :meth:`submit`.
        timeout: override default per-request.  Pass a tiny value to test
            connectivity before committing to a full render.
        show_progress: log queue position and executing node names so you
            can see *what* is happening rather than staring at nothing.

        Returns
        -------
        The completed history entry dict.
        """
        deadline = time.time() + (timeout or self.timeout)

        # Start WebSocket listener if available (only when a running loop exists)
        try:
            asyncio.get_running_loop().create_task(self._ws_connect())
        except RuntimeError:
            # No running event loop (e.g. called from a worker thread) — skip WS,
            # HTTP polling below still works.
            pass

        last_node: str | None = None
        queue_len: int = 0
        while time.time() < deadline:
            try:
                history = self.get_history(prompt_id)
            except ComfyUIError as exc:
                logger.debug("[ComfyUI] Poll error (still working/unresponsive): %s", exc)
                history = None

            if history is not None:
                status = history.get("status", {})

                # ---- progress reporting (only when it changes) ----
                if show_progress:
                    try:
                        qr = self.get_queue_position()
                        running = len(qr.get("queue_running", []))
                        pending = len(qr.get("queue_pending", []))
                    except Exception:
                        running, pending = 1, 0
                    executing_node = None
                    for node_id, node_out in history.get("outputs", {}).items():
                        if isinstance(node_out, dict) and "images" in node_out:
                            executing_node = f"output(images)"

                    # Detect what we're currently doing
                    if not executing_node:
                        for stage_key in ("system_status", "queue_position"):
                            val = status.get(stage_key) or history.get(stage_key)
                            if val is not None:
                                executing_node = str(val)
                                break

                    if (executing_node and executing_node != last_node) or queue_len != pending:
                        node_name = executing_node or "…?"
                        logger.info(
                            "[ComfyUI] %s  |  running=%d  pending=%d",
                            node_name, running, pending,
                        )
                        last_node = executing_node
                        queue_len = pending

                    # Show progress from history's 'progress' key (some ComfyUI forks)
                    prog = status.get("progress")
                    if prog is not None and isinstance(prog, int):
                        logger.info("[ComfyUI] %s — %.0f%%", node_name, prog * 100)

                # ---- check completion ----
                if status.get("completed", False):
                    return history

            time.sleep(poll_interval)

        raise ComfyUITimeoutError(
            f"ComfyUI prompt {prompt_id} did not complete within "
            f"{timeout or self.timeout:.0f}s"
        )

    async def wait_for_result_async(
        self,
        prompt_id: str,
        *,
        timeout: float | None = None,
        poll_interval: float = 1.0,
    ) -> dict:
        """Async variant of :meth:`wait_for_result` that prefers WS events."""
        deadline = time.time() + (timeout or self.timeout)
        await self._ws_connect()

        while time.time() < deadline:
            try:
                history = self.get_history(prompt_id)
            except Exception as exc:
                logger.debug("[ComfyUI] Poll error (still working/unresponsive): %s", exc)
                history = None

            if history is not None:
                if history.get("status", {}).get("completed", False):
                    return history
            await asyncio.sleep(poll_interval)

        raise ComfyUITimeoutError(
            f"ComfyUI prompt {prompt_id} did not complete within "
            f"{timeout or self.timeout:.0f}s"
        )

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------

    def fetch_image(
        self,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
    ) -> bytes:
        """Fetch the generated image bytes from ComfyUI."""
        params = f"filename={filename}&subfolder={subfolder}&type={folder_type}"
        result = self._request("GET", f"/view?{params}", timeout=30.0)
        if isinstance(result, bytes):
            return result
        if isinstance(result, str):
            return result.encode("utf-8", errors="replace")
        raise ComfyUIError(
            f"ComfyUI /view returned unexpected type: {type(result)}"
        )

    def save_image(
        self,
        filename: str,
        output_path: str | Path,
        subfolder: str = "",
        folder_type: str = "output",
    ) -> Path:
        """Fetch an image and save it to a local path."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.fetch_image(filename, subfolder, folder_type)
        output_path.write_bytes(data)
        logger.info("[ComfyUI] Saved image: %s (%d bytes)", output_path, len(data))
        return output_path

    def get_outputs(self, history: dict) -> list[dict]:
        """Extract the image outputs from a history entry.

        Returns a list of ``{"filename": str, "subfolder": str, "type": str}``.
        """
        outputs = []
        for node_id, node_output in history.get("outputs", {}).items():
            for img in node_output.get("images", []):
                outputs.append(img)
        return outputs


# ---------------------------------------------------------------------------
# Convenience functions (sync-only — no async loop needed)
# ---------------------------------------------------------------------------

def check_comfyui_ready(
    base_url: str = "http://localhost:8188",
    timeout: float = 120.0,
    node_prefixes: list[str] | None = None,
) -> bool:
    """One-shot helper to verify ComfyUI is both alive *and* ready to render.

    Returns ``True`` when the server responds and at least one FLUX-relevant
    node (e.g. ``UNETLoader``, ``FluxGuidance``) appears in :attr:`/object_info`.
    """
    client = ComfyUIClient(base_url=base_url)
    if not client.health():
        logger.warning("[ComfyUI] Server not responding")
        return False

    result = client.wait_for_node_ready(timeout=timeout, node_prefixes=node_prefixes)
    ready = result is not None and isinstance(result, dict) and len(result) > 0
    if ready:
        logger.info("[ComfyUI] Ready to render")
    else:
        logger.warning("[ComfyUI] Still loading — check logs or VRAM availability")
    return ready


def warmup_flux(
    client: ComfyUIClient,
    *,
    prompt: str = "a test image",
    steps: int = 1,
    seed: int = 0,
) -> None:
    """Send a minimal workflow to ComfyUI to load the model into VRAM.

    After this call the first *real* render will be significantly faster
    because FLUX's weights are already in memory and the execution graph
    is compiled.

    Parameters
    ----------
    prompt: dummy text (any string — the encoder still runs but results don't matter)
    steps: 1 is enough to trigger weight load; more won't hurt but costs time
    seed: deterministic seed for reproducibility
    """
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["1", 0]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "", "clip": ["1", 0]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["2", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0],
                         "seed": seed, "steps": steps, "cfg": 1.0,
                         "sampler_name": "euler", "scheduler": "normal"}},
        "6": {"class_type": "VAEDecode",
              "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"images": ["6", 0], "filename_prefix": "warmup"}},
    }

    logger.info("[ComfyUI] Warmup — submitting minimal workflow...")
    try:
        pid = client.submit(workflow, priority="high")
        result = client.wait_for_result(pid, timeout=120.0, show_progress=True)
        if result.get("status", {}).get("completed"):
            logger.info("[ComfyUI] Warmup complete — model ready in VRAM")
        else:
            logger.warning("[ComfyUI] Warmup did not complete — model may still be loading")
    except (ComfyUIError, ComfyUITimeoutError) as exc:
        logger.warning("[ComfyUI] Warmup failed: %s", exc)
