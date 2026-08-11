"""Tests for Docker-sandbox availability detection and its user-facing errors."""

from __future__ import annotations

import os

import pytest
from docker.errors import DockerException

from strix.interface.environment import check_docker_installed
from strix.interface.utils import check_docker_connection, print_sandbox_unavailable


def _output(capsys: pytest.CaptureFixture[str]) -> str:
    return capsys.readouterr().out


def test_check_docker_connection_exits_cleanly_when_daemon_is_down(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _no_daemon() -> None:
        raise DockerException("Error while fetching server API version")

    monkeypatch.setattr("strix.interface.utils.docker.from_env", _no_daemon)

    with pytest.raises(SystemExit) as exc_info:
        check_docker_connection()

    assert exc_info.value.code == 1
    panel_text = _output(capsys)
    assert "DOCKER SANDBOX UNAVAILABLE" in panel_text
    assert "Local autonomous pentesting requires the Strix Docker sandbox." in panel_text
    assert "Strix itself is installed and functioning." in panel_text
    assert "strix view" in panel_text
    assert "app.strix.ai" in panel_text
    assert "Continue using host-side Strix functionality." in panel_text


def test_check_docker_installed_exits_when_cli_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("shutil.which", lambda _name: None)

    with pytest.raises(SystemExit) as exc_info:
        check_docker_installed()

    assert exc_info.value.code == 1
    panel_text = _output(capsys)
    assert "DOCKER SANDBOX UNAVAILABLE" in panel_text
    assert "Docker sandbox is unavailable on this" in panel_text


def test_check_docker_installed_passes_when_cli_is_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda _name: "docker")
    check_docker_installed()


def test_sandbox_unavailable_message_uses_platform_start_commands(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(os, "name", "nt")
    print_sandbox_unavailable("reason")
    nt_text = _output(capsys)
    assert "this Windows host." in nt_text
    assert "Use Docker Desktop if local sandbox execution is required" in nt_text
    assert 'Start-Process "Docker Desktop"' in nt_text
    assert "docker info" in nt_text

    monkeypatch.setattr(os, "name", "posix")
    print_sandbox_unavailable("reason")
    posix_text = _output(capsys)
    assert "this host." in posix_text
    assert "systemctl start docker" in posix_text
    assert "docker info" in posix_text
