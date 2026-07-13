"""ComfyUI HTTP client.

ComfyUI exposes a REST API on a configurable port (default 8188).
This client wraps the API and exposes a clean Python interface.

Key endpoints used:
  - POST /prompt           — submit a workflow, returns a prompt_id
  - GET  /history/{id}     — check if a prompt is complete + get outputs
  - GET  /queue             — check the queue
  - GET  /models            — list available models
  - GET  /view              — fetch the generated image bytes

Usage:

    from movie_os.workflows.comfyui_client import ComfyUIClient

    client = ComfyUIClient(base_url="http://localhost:8188")
    prompt_id = client.submit(workflow_dict)
    result = client.wait_for_result(prompt_id, timeout=600)
    image_bytes = client.fetch_image(result["image_filename"], result["subfolder"])
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


logger = logging.getLogger("movie_os.workflows.comfyui_client")


class ComfyUIError(RuntimeError):
    """Raised when a ComfyUI call fails."""
    pass


class ComfyUIClient:
    """HTTP client for ComfyUI's REST API.

    ComfyUI runs as a local service (typically on port 8188). This
    client talks to it via JSON over HTTP — no SDK required.
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

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
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
            raise ComfyUIError(
                f"ComfyUI unreachable at {self.base_url}: {e}"
            ) from e

    # ------------------------------------------------------------------
    # High-level operations
    # ------------------------------------------------------------------

    def health(self) -> bool:
        """Check if ComfyUI is reachable and responding."""
        try:
            self._request("GET", "/system_stats", timeout=5.0)
            return True
        except ComfyUIError:
            return False

    def list_models(self) -> list[str]:
        """List available model checkpoints."""
        result = self._request("GET", "/models", timeout=10.0)
        if isinstance(result, list):
            return result
        return []

    def submit(self, workflow: dict, *, client_id: str = "movie_os") -> str:
        """Submit a workflow to ComfyUI's queue.

        Returns the prompt_id. Poll /history/{prompt_id} to check status.
        """
        payload = {"prompt": workflow, "client_id": client_id}
        result = self._request("POST", "/prompt", json_body=payload)
        if not isinstance(result, dict) or "prompt_id" not in result:
            raise ComfyUIError(
                f"ComfyUI /prompt returned unexpected response: {result!r}"
            )
        prompt_id = result["prompt_id"]
        logger.info(f"Submitted workflow to ComfyUI: prompt_id={prompt_id}")
        return prompt_id

    def get_history(self, prompt_id: str) -> dict | None:
        """Get the history entry for a prompt_id, or None if not found."""
        result = self._request("GET", f"/history/{prompt_id}", timeout=10.0)
        if not isinstance(result, dict):
            return None
        return result.get(prompt_id)

    def wait_for_result(
        self,
        prompt_id: str,
        *,
        timeout: float | None = None,
        poll_interval: float = 1.0,
    ) -> dict:
        """Poll until the prompt completes, then return the history entry.

        Returns a dict like:
            {
                "outputs": {
                    "node_id": {
                        "images": [
                            {"filename": "...", "subfolder": "...", "type": "output"}
                        ]
                    }
                },
                "status": {"completed": True, "messages": [...]}
            }
        """
        deadline = time.time() + (timeout or self.timeout)
        while time.time() < deadline:
            history = self.get_history(prompt_id)
            if history:
                status = history.get("status", {})
                if status.get("completed", False):
                    return history
            time.sleep(poll_interval)
        raise ComfyUIError(
            f"ComfyUI prompt {prompt_id} did not complete within {timeout}s"
        )

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
        # Some ComfyUI versions return a JSON-wrapped string — handle both
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
        logger.info(f"Saved ComfyUI image: {output_path} ({len(data)} bytes)")
        return output_path

    def get_queue(self) -> dict:
        """Get the current queue status."""
        result = self._request("GET", "/queue", timeout=5.0)
        if isinstance(result, dict):
            return result
        return {"queue_running": [], "queue_pending": []}

    def get_outputs(self, history: dict) -> list[dict]:
        """Extract the image outputs from a history entry.

        Returns a list of {"filename": str, "subfolder": str, "type": str}.
        """
        outputs = []
        for node_id, node_output in history.get("outputs", {}).items():
            for img in node_output.get("images", []):
                outputs.append(img)
        return outputs
