"""Tests for the ComfyUI Service Manager (SAI-94 / TASK-014).

These tests exercise the pure logic (detection, install check, pid handling)
without actually launching a ComfyUI server.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from movie_os.providers.image.comfyui_service import ComfyUIService


class TestComfyUIService:
    def test_install_ok_detects_missing_path(self):
        svc = ComfyUIService(install_path="/nonexistent/comfyui")
        assert not svc.install_ok()

    def test_install_ok_accepts_existing_main(self, tmp_path):
        main = tmp_path / "main.py"
        main.write_text("x")
        svc = ComfyUIService(install_path=str(tmp_path))
        assert svc.install_ok()

    def test_reuses_existing_pid_on_shutdown(self, tmp_path):
        pidf = tmp_path / "comfyui.pid"
        pidf.write_text("12345")
        svc = ComfyUIService(pid_file=str(pidf))
        assert svc._load_stored_pid() == 12345

    def test_write_and_read_pid(self, tmp_path):
        pidf = tmp_path / "comfyui.pid"
        svc = ComfyUIService(pid_file=str(pidf))
        svc._write_pid(9876)
        assert int(pidf.read_text()) == 9876
        assert svc._load_stored_pid() == 9876

    def test_launch_raises_when_install_missing(self, tmp_path):
        svc = ComfyUIService(install_path=str(tmp_path / "nope"))
        with pytest.raises(FileNotFoundError):
            svc.launch()

    def test_running_probe_against_unreachable_url_is_false(self):
        svc = ComfyUIService(url="http://127.0.0.1:1")  # nothing listens on :1
        assert not svc.is_running()
