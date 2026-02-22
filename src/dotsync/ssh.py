"""SSH key generation and remote command execution."""

from __future__ import annotations

import subprocess


def run_remote(host: str, command: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a command on a remote machine via SSH."""
    return subprocess.run(
        ["ssh", "-o", f"ConnectTimeout={timeout}", "-o", "BatchMode=yes", host, command],
        capture_output=True,
        text=True,
        check=False,
    )


def is_reachable(host: str, timeout: int = 3) -> bool:
    """Check if a host is reachable via SSH."""
    result = run_remote(host, "echo ok", timeout=timeout)
    return result.returncode == 0
